"""
Multi-signal authentication component detector.

Detects login forms, password fields, username fields, OAuth buttons,
and forgot-password links using a heuristic scoring approach.
"""

from __future__ import annotations

import re
from bs4 import BeautifulSoup, Tag

from models.schemas import AuthComponent


# ---------------------------------------------------------------------------
# Keyword banks
# ---------------------------------------------------------------------------

AUTH_KEYWORDS: dict[str, list[str]] = {
    "form_action": [
        "login", "signin", "sign-in", "sign_in", "auth", "session",
        "authenticate", "logon", "log-in", "log_in",
    ],
    "username_field": [
        "user", "email", "login", "account", "uid", "identity",
        "handle", "username", "uname",
    ],
    "password_field": [
        "pass", "pwd", "password", "secret", "passwd",
    ],
    "submit_button": [
        "sign in", "log in", "login", "submit", "enter", "continue",
        "sign-in", "log-in", "go", "authenticate",
    ],
    "oauth": [
        "google", "github", "facebook", "apple", "microsoft",
        "sso", "oauth", "saml", "twitter", "linkedin",
    ],
    "forgot": [
        "forgot", "reset", "recover", "can't sign in",
        "trouble signing in", "reset password", "forgot password",
    ],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _text(tag: Tag) -> str:
    """Get visible text content, lowercased and stripped."""
    return (tag.get_text(separator=" ", strip=True) or "").lower()


def _attr_str(tag: Tag) -> str:
    """Concatenate all attribute values into a single searchable string."""
    parts: list[str] = []
    for val in tag.attrs.values():
        if isinstance(val, list):
            parts.extend(val)
        elif isinstance(val, str):
            parts.append(val)
    return " ".join(parts).lower()


def _matches_keywords(text: str, keywords: list[str]) -> bool:
    """Check if any keyword appears in the given text."""
    text_lower = text.lower()
    return any(kw in text_lower for kw in keywords)


def _css_selector(tag: Tag) -> str:
    """Build a simple CSS selector path for a tag."""
    parts: list[str] = []
    current: Tag | None = tag
    while current and current.name and current.name != "[document]":
        sel = current.name
        if current.get("id"):
            sel += f"#{current['id']}"
            parts.insert(0, sel)
            break
        elif current.get("class"):
            classes = current["class"] if isinstance(current["class"], list) else [current["class"]]
            sel += "." + ".".join(classes[:2])
        parts.insert(0, sel)
        current = current.parent
    return " > ".join(parts) if parts else tag.name


def _extract_attrs(tag: Tag) -> dict[str, str]:
    """Extract key attributes as a flat dict."""
    keep = ["id", "name", "type", "class", "placeholder", "aria-label",
            "autocomplete", "action", "method", "href"]
    attrs: dict[str, str] = {}
    for k in keep:
        val = tag.get(k)
        if val:
            attrs[k] = " ".join(val) if isinstance(val, list) else str(val)
    return attrs


def _snippet(tag: Tag, max_len: int = 5000) -> str:
    """Return a prettified HTML snippet, truncated if needed."""
    html = tag.prettify()
    if len(html) > max_len:
        html = html[:max_len] + "\n<!-- ... truncated -->"
    return html


# ---------------------------------------------------------------------------
# Phase 1: Form-level detection
# ---------------------------------------------------------------------------

def _detect_login_forms(soup: BeautifulSoup) -> list[AuthComponent]:
    """Find <form> elements that look like login forms."""
    components: list[AuthComponent] = []

    for form in soup.find_all("form"):
        score = 0.0

        # Signal 1: Contains a password input (+0.4)
        password_inputs = form.find_all("input", attrs={"type": "password"})
        if password_inputs:
            score += 0.4

        # Signal 2: Contains a username/email input (+0.2)
        has_username = False
        for inp in form.find_all("input"):
            inp_type = (inp.get("type") or "text").lower()
            if inp_type == "email":
                has_username = True
                break
            if inp_type == "text":
                attr_text = _attr_str(inp)
                if _matches_keywords(attr_text, AUTH_KEYWORDS["username_field"]):
                    has_username = True
                    break
            if inp.get("autocomplete") in ("username", "email"):
                has_username = True
                break
        if has_username:
            score += 0.2

        # Signal 3: Has a submit button with login text (+0.2)
        has_submit = False
        for btn in form.find_all(["button", "input"]):
            btn_type = (btn.get("type") or "").lower()
            btn_text = _text(btn)
            if btn_type == "submit" or _matches_keywords(
                btn_text, AUTH_KEYWORDS["submit_button"]
            ):
                has_submit = True
                break
        if has_submit:
            score += 0.2

        # Signal 4: Form action URL contains auth keywords (+0.1)
        action = (form.get("action") or "").lower()
        if _matches_keywords(action, AUTH_KEYWORDS["form_action"]):
            score += 0.1

        # Signal 5: Auth keywords in form attributes / children attributes (+0.1)
        form_attrs = _attr_str(form)
        if _matches_keywords(form_attrs, AUTH_KEYWORDS["form_action"]):
            score += 0.1

        if score >= 0.5:
            components.append(AuthComponent(
                component_type="login_form",
                html_snippet=_snippet(form),
                selector=_css_selector(form),
                confidence=min(score, 1.0),
                attributes=_extract_attrs(form),
            ))

    return components


# ---------------------------------------------------------------------------
# Phase 2: Formless auth detection (SPAs)
# ---------------------------------------------------------------------------

def _detect_formless_auth(soup: BeautifulSoup) -> list[AuthComponent]:
    """Find password inputs not inside a <form> and locate their container."""
    components: list[AuthComponent] = []

    for pwd_input in soup.find_all("input", attrs={"type": "password"}):
        # Skip if already inside a form (handled by Phase 1)
        if pwd_input.find_parent("form"):
            continue

        # Walk up to find a meaningful container
        container = pwd_input.parent
        for _ in range(5):
            if container is None or container.name in (None, "[document]", "body", "html"):
                break
            # Check if this container has other auth-related inputs
            sibling_inputs = container.find_all("input")
            if len(sibling_inputs) >= 2:
                break
            container = container.parent

        if container and container.name not in (None, "[document]", "body", "html"):
            score = 0.7  # Formless but has password input
            # Boost if username field is present
            for inp in container.find_all("input"):
                inp_type = (inp.get("type") or "text").lower()
                if inp_type in ("text", "email") or inp.get("autocomplete") in (
                    "username", "email"
                ):
                    score += 0.1
                    break

            components.append(AuthComponent(
                component_type="login_form",
                html_snippet=_snippet(container),
                selector=_css_selector(container),
                confidence=min(score, 1.0),
                attributes=_extract_attrs(container),
            ))

    return components


# ---------------------------------------------------------------------------
# Phase 3: OAuth / SSO button detection
# ---------------------------------------------------------------------------

OAUTH_ACTION_PHRASES = [
    "sign in with", "log in with", "login with", "continue with",
    "sign up with", "connect with", "authenticate with",
]

OAUTH_ENDPOINTS = [
    "accounts.google.com", "github.com/login/oauth",
    "facebook.com/dialog", "appleid.apple.com", "login.microsoftonline.com",
    "api.twitter.com/oauth", "linkedin.com/oauth",
]


def _detect_oauth_buttons(soup: BeautifulSoup) -> list[AuthComponent]:
    """Detect OAuth/SSO sign-in buttons."""
    components: list[AuthComponent] = []
    seen_texts: set[str] = set()

    for el in soup.find_all(["a", "button"]):
        el_text = _text(el)
        el_attrs = _attr_str(el)
        href = (el.get("href") or "").lower()

        # Must have BOTH a provider keyword AND a sign-in action phrase,
        # OR link to a known OAuth endpoint
        has_provider = _matches_keywords(f"{el_text} {el_attrs}", AUTH_KEYWORDS["oauth"])
        has_action = any(phrase in el_text for phrase in OAUTH_ACTION_PHRASES)
        has_oauth_endpoint = any(ep in href for ep in OAUTH_ENDPOINTS)

        if not ((has_provider and has_action) or has_oauth_endpoint):
            continue

        if el_text in seen_texts:
            continue
        seen_texts.add(el_text)

        provider = "unknown"
        combined = f"{el_text} {el_attrs} {href}"
        for kw in AUTH_KEYWORDS["oauth"]:
            if kw in combined:
                provider = kw
                break

        components.append(AuthComponent(
            component_type="oauth_button",
            html_snippet=_snippet(el),
            selector=_css_selector(el),
            confidence=0.80,
            attributes={**_extract_attrs(el), "provider": provider},
        ))

    return components


# ---------------------------------------------------------------------------
# Phase 4: Forgot password link detection
# ---------------------------------------------------------------------------

def _detect_forgot_password(soup: BeautifulSoup) -> list[AuthComponent]:
    """Detect forgot-password and account-recovery links."""
    components: list[AuthComponent] = []

    for link in soup.find_all("a"):
        link_text = _text(link)
        link_attrs = _attr_str(link)
        combined = f"{link_text} {link_attrs}"

        if _matches_keywords(combined, AUTH_KEYWORDS["forgot"]):
            components.append(AuthComponent(
                component_type="forgot_password_link",
                html_snippet=_snippet(link),
                selector=_css_selector(link),
                confidence=0.7,
                attributes=_extract_attrs(link),
            ))

    return components


# ---------------------------------------------------------------------------
# Deduplication & ranking
# ---------------------------------------------------------------------------

def _deduplicate_and_rank(components: list[AuthComponent]) -> list[AuthComponent]:
    """Remove nested duplicates of the same type and sort by confidence descending."""
    if not components:
        return []

    # Only deduplicate within the same component_type
    sorted_comps = sorted(components, key=lambda c: -c.confidence)
    result: list[AuthComponent] = []
    seen_by_type: dict[str, list[str]] = {}

    for comp in sorted_comps:
        snippet_clean = re.sub(r"\s+", " ", comp.html_snippet.strip())
        seen_snippets = seen_by_type.get(comp.component_type, [])
        is_subset = False
        for seen in seen_snippets:
            if snippet_clean in seen or seen in snippet_clean:
                if len(snippet_clean) <= len(seen):
                    is_subset = True
                    break
        if not is_subset:
            result.append(comp)
            seen_by_type.setdefault(comp.component_type, []).append(snippet_clean)

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_auth_components(html: str) -> list[AuthComponent]:
    """
    Main entry point. Parses HTML, runs all detection phases,
    returns scored and deduplicated AuthComponent list.
    """
    soup = BeautifulSoup(html, "html.parser")
    candidates: list[AuthComponent] = []

    # Phase 1: Form-level scan
    candidates.extend(_detect_login_forms(soup))

    # Phase 2: Formless field scan (SPAs)
    candidates.extend(_detect_formless_auth(soup))

    # Phase 3: OAuth / SSO buttons
    candidates.extend(_detect_oauth_buttons(soup))

    # Phase 4: Forgot password links
    candidates.extend(_detect_forgot_password(soup))

    # Deduplicate and rank
    return _deduplicate_and_rank(candidates)


def generate_summary(components: list[AuthComponent]) -> str:
    """Generate a human-readable summary of detected components."""
    if not components:
        return "No authentication components detected on this page."

    type_counts: dict[str, int] = {}
    for c in components:
        type_counts[c.component_type] = type_counts.get(c.component_type, 0) + 1

    parts: list[str] = []
    if "login_form" in type_counts:
        n = type_counts["login_form"]
        parts.append(f"{n} login form{'s' if n > 1 else ''}")
    if "oauth_button" in type_counts:
        n = type_counts["oauth_button"]
        parts.append(f"{n} OAuth/SSO button{'s' if n > 1 else ''}")
    if "forgot_password_link" in type_counts:
        n = type_counts["forgot_password_link"]
        parts.append(f"{n} forgot-password link{'s' if n > 1 else ''}")

    max_conf = max(c.confidence for c in components)
    return f"Found {', '.join(parts)} (max confidence: {max_conf:.0%})"
