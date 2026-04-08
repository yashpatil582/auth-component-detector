import axios from "axios";
import type { ScrapeRequest, ScrapeResponse } from "../types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
});

export async function scrapeUrl(req: ScrapeRequest): Promise<ScrapeResponse> {
  const { data } = await api.post<ScrapeResponse>("/api/scrape", req);
  return data;
}

export async function getExamples(): Promise<ScrapeResponse[]> {
  const { data } = await api.get<ScrapeResponse[]>("/api/examples");
  return data;
}
