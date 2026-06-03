"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import type { MatchesResponse } from "../lib/api";

type MatchesOverviewProps = {
  hasJobs: boolean;
  hasProfile: boolean;
  initialMatches: MatchesResponse;
};

export function MatchesOverview({ hasJobs, hasProfile, initialMatches }: MatchesOverviewProps) {
  const router = useRouter();
  const [matches, setMatches] = useState<MatchesResponse>(initialMatches);
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    setMatches(initialMatches);
  }, [initialMatches]);

  async function handleRunMatching() {
    setIsRunning(true);
    setMessage("");

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/matches/run`, {
        method: "POST",
      });
      const payload = (await response.json()) as MatchesResponse | { detail?: string };

      if (!response.ok) {
        throw new Error(("detail" in payload && payload.detail) || `Match run failed with ${response.status}`);
      }

      const snapshot = payload as MatchesResponse;
      setMatches(snapshot);
      setMessage(`Updated current snapshot for ${snapshot.evaluated_count} ranked jobs.`);
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Match run failed.");
    } finally {
      setIsRunning(false);
    }
  }

  const topMatches = matches.matches.slice(0, 10);

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <span className="panel-label">Matching</span>
          <h2>Current ranked jobs snapshot</h2>
          <p className="panel-copy">
            The snapshot stores all scored jobs from the latest run. This view shows the top 10 ranked matches.
          </p>
        </div>
        <div className="match-actions">
          <button onClick={handleRunMatching} disabled={isRunning || !hasProfile || !hasJobs} type="button">
            {isRunning ? "Running..." : "Run matching"}
          </button>
          <span className={`status-pill ${matches.has_snapshot ? "status-ok" : "status-empty"}`}>
            {matches.has_snapshot ? `${matches.evaluated_count} ranked` : "no snapshot"}
          </span>
        </div>
      </div>

      {!hasProfile ? <p>Create a profile before running matching.</p> : null}
      {hasProfile && !hasJobs ? <p>Fetch jobs before running matching.</p> : null}
      {message ? <p className="form-message">{message}</p> : null}

      {matches.has_snapshot ? (
        <>
          <div className={`snapshot-banner ${matches.is_stale ? "snapshot-banner-stale" : "snapshot-banner-fresh"}`}>
            <div>
              <strong>{matches.is_stale ? "Snapshot is stale." : "Snapshot is current."}</strong>
              <p>
                {matches.is_stale
                  ? "Profile changed since the last match run. Rerun matching to refresh scores."
                  : "Persisted scores and explanations reflect the latest match run."}
              </p>
            </div>
            <div className="snapshot-meta">
              <span>Last run: {formatDate(matches.last_run_at)}</span>
              <span>Snapshot profile: {formatDate(matches.snapshot_profile_updated_at)}</span>
              <span>Profile updated: {formatDate(matches.profile_updated_at)}</span>
              <span>Scoring version: {matches.scoring_version || "not available"}</span>
              {matches.is_stale ? (
                <button
                  type="button"
                  onClick={handleRunMatching}
                  disabled={isRunning || !hasJobs}
                  className="button-secondary"
                >
                  {isRunning ? "Running..." : "Rerun matching now"}
                </button>
              ) : null}
            </div>
          </div>

          <div className="job-list">
            {topMatches.map((match) => (
              <article key={match.id} className="job-card">
                <div className="job-copy">
                  <div className="match-card-header">
                    <div>
                      <h3>{match.job.title}</h3>
                      <p>{match.job.company || "Unknown company"}</p>
                    </div>
                    <span className={`recommendation-pill recommendation-${match.recommendation || "skip"}`}>
                      {match.recommendation || "unrated"}
                    </span>
                  </div>
                  <p>{match.explanation || "No explanation saved for this match."}</p>
                  <p className="match-supplement">
                    Matched skills: {match.matched_skills.length > 0 ? match.matched_skills.join(", ") : "none"}
                  </p>
                  <p className="match-supplement">
                    Missing skills: {match.missing_skills.length > 0 ? match.missing_skills.join(", ") : "none"}
                  </p>
                </div>
                <div className="job-meta">
                  <span>Score: {match.match_score ?? "?"}</span>
                  <span>Skills: {match.skill_score ?? "?"}</span>
                  <span>Role: {match.interest_score ?? "?"}</span>
                  <span>Location: {match.location_score ?? "?"}</span>
                  <span>Salary: {match.salary_score ?? "?"}</span>
                  <span>Job location: {match.job.location || "Unknown location"}</span>
                  <span>Salary range: {formatSalaryRange(match.job.salary_min, match.job.salary_max)}</span>
                  <span>Remote type: {match.job.remote_type || "Not specified"}</span>
                  <span>Source: {match.job.source}</span>
                  {match.job.url ? (
                    <a href={match.job.url} target="_blank" rel="noreferrer">
                      Source
                    </a>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        </>
      ) : (
        <p>No match snapshot yet. Run matching after saving a profile and fetching jobs.</p>
      )}
    </section>
  );
}

function formatDate(value: string | null) {
  if (!value) {
    return "not available";
  }

  return new Date(value).toLocaleString();
}

function formatSalaryRange(minimum: number | null, maximum: number | null) {
  if (minimum === null && maximum === null) {
    return "Not specified";
  }

  return `${minimum ?? "?"} - ${maximum ?? "?"}`;
}
