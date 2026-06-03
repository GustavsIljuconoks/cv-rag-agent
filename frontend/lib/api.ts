type HealthResponse = {
  status: string;
};

export type Profile = {
  id: number;
  summary: string | null;
  preferred_roles: string | null;
  preferred_locations: string | null;
  preferred_remote_type: string | null;
  preferred_technologies: string | null;
  salary_expectation_min: number | null;
  salary_expectation_max: number | null;
  created_at: string;
  updated_at: string;
};

export type Job = {
  id: number;
  source: string;
  external_id: string;
  title: string;
  company: string | null;
  location: string | null;
  remote_type: string | null;
  salary_min: number | null;
  salary_max: number | null;
  description: string | null;
  url: string | null;
  posted_at: string | null;
  created_at: string;
  updated_at: string;
};

export type Match = {
  id: number;
  job_id: number;
  candidate_profile_id: number;
  match_score: number | null;
  semantic_score: number | null;
  skill_score: number | null;
  seniority_score: number | null;
  location_score: number | null;
  salary_score: number | null;
  interest_score: number | null;
  explanation: string | null;
  recommendation: string | null;
  created_at: string;
  matched_skills: string[];
  missing_skills: string[];
  job: Job;
};

export type MatchesResponse = {
  has_snapshot: boolean;
  is_stale: boolean;
  evaluated_count: number;
  last_run_at: string | null;
  profile_updated_at: string | null;
  snapshot_profile_updated_at: string | null;
  scoring_version: string | null;
  matches: Match[];
};

const publicApiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const internalApiUrl = process.env.INTERNAL_API_URL ?? "http://backend:8000";

const emptyMatchesResponse: MatchesResponse = {
  has_snapshot: false,
  is_stale: false,
  evaluated_count: 0,
  last_run_at: null,
  profile_updated_at: null,
  snapshot_profile_updated_at: null,
  scoring_version: null,
  matches: [],
};

function getApiUrl() {
  return typeof window === "undefined" ? internalApiUrl : publicApiUrl;
}

async function readJson<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${getApiUrl()}${path}`, { cache: "no-store" });

    if (response.status === 404) {
      return null;
    }

    if (!response.ok) {
      throw new Error(`Request failed with ${response.status}`);
    }

    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getBackendHealth(): Promise<HealthResponse | null> {
  return readJson<HealthResponse>("/health");
}

export async function getProfile(): Promise<Profile | null> {
  return readJson<Profile>("/profile");
}

export async function getJobs(): Promise<Job[]> {
  return (await readJson<Job[]>("/jobs")) ?? [];
}

export async function getMatches(): Promise<MatchesResponse> {
  return (await readJson<MatchesResponse>("/matches")) ?? emptyMatchesResponse;
}
