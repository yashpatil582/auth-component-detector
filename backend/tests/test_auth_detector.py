"""Unit tests for the auth detection algorithm."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.auth_detector import detect_auth_components, generate_summary


# ---------------------------------------------------------------------------
# Test HTML fixtures
# ---------------------------------------------------------------------------

SIMPLE_LOGIN_FORM = """
<html><body>
<form id="login-form" action="/auth/login" method="POST">
  <label for="username">Username</label>
  <input type="text" id="username" name="username" placeholder="Enter username">
  <label for="password">Password</label>
  <input type="password" id="password" name="password" placeholder="Enter password">
  <button type="submit">Sign In</button>
</form>
</body></html>
"""

EMAIL_PASSWORD_FORM = """
<html><body>
<div class="login-container">
  <form action="/api/session" method="POST">
    <input type="email" name="email" placeholder="Email address" autocomplete="email">
    <input type="password" name="password" placeholder="Password" autocomplete="current-password">
    <input type="submit" value="Log In">
    <a href="/forgot">Forgot password?</a>
  </form>
</div>
</body></html>
"""

SPA_NO_FORM = """
<html><body>
<div id="app">
  <div class="auth-panel">
    <div class="login-box">
      <input type="text" name="username" placeholder="Username">
      <input type="password" name="password" placeholder="Password">
      <button>Continue</button>
    </div>
  </div>
</div>
</body></html>
"""

OAUTH_PAGE = """
<html><body>
<div class="login-options">
  <form action="/login" method="POST">
    <input type="email" name="email" placeholder="Email">
    <input type="password" name="password">
    <button type="submit">Sign In</button>
  </form>
  <div class="social-login">
    <a href="https://accounts.google.com/o/oauth2" class="btn-google">Sign in with Google</a>
    <button class="btn-github">Continue with GitHub</button>
  </div>
</div>
</body></html>
"""

NO_AUTH_PAGE = """
<html><body>
<h1>Welcome to our blog</h1>
<p>This is a regular page with no authentication components.</p>
<form action="/search" method="GET">
  <input type="text" name="q" placeholder="Search...">
  <button type="submit">Search</button>
</form>
</body></html>
"""

FORGOT_PASSWORD_LINKS = """
<html><body>
<form action="/login" method="POST">
  <input type="text" name="username">
  <input type="password" name="password">
  <button type="submit">Login</button>
</form>
<a href="/password/reset">Forgot password?</a>
<a href="/account/recover">Can't sign in?</a>
</body></html>
"""


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_simple_login_form():
    results = detect_auth_components(SIMPLE_LOGIN_FORM)
    assert len(results) >= 1
    form = next(c for c in results if c.component_type == "login_form")
    assert form.confidence >= 0.8
    assert "password" in form.html_snippet.lower()


def test_email_password_form():
    results = detect_auth_components(EMAIL_PASSWORD_FORM)
    login_forms = [c for c in results if c.component_type == "login_form"]
    assert len(login_forms) >= 1
    assert login_forms[0].confidence >= 0.7

    forgot_links = [c for c in results if c.component_type == "forgot_password_link"]
    assert len(forgot_links) >= 1


def test_spa_no_form():
    results = detect_auth_components(SPA_NO_FORM)
    # Should still detect auth via formless detection
    assert len(results) >= 1
    form = next(c for c in results if c.component_type == "login_form")
    assert form.confidence >= 0.7
    assert "password" in form.html_snippet.lower()


def test_oauth_detection():
    results = detect_auth_components(OAUTH_PAGE)
    oauth = [c for c in results if c.component_type == "oauth_button"]
    assert len(oauth) >= 1
    providers = {c.attributes.get("provider") for c in oauth}
    assert "google" in providers or "github" in providers


def test_no_auth_page():
    results = detect_auth_components(NO_AUTH_PAGE)
    login_forms = [c for c in results if c.component_type == "login_form"]
    assert len(login_forms) == 0


def test_forgot_password():
    results = detect_auth_components(FORGOT_PASSWORD_LINKS)
    forgot = [c for c in results if c.component_type == "forgot_password_link"]
    assert len(forgot) >= 1


def test_generate_summary_with_results():
    results = detect_auth_components(OAUTH_PAGE)
    summary = generate_summary(results)
    assert "Found" in summary
    assert "login form" in summary.lower() or "oauth" in summary.lower()


def test_generate_summary_empty():
    results = detect_auth_components(NO_AUTH_PAGE)
    summary = generate_summary(results)
    assert "No authentication" in summary


def test_confidence_ordering():
    results = detect_auth_components(SIMPLE_LOGIN_FORM)
    # Results should be sorted by confidence descending
    for i in range(len(results) - 1):
        assert results[i].confidence >= results[i + 1].confidence


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
