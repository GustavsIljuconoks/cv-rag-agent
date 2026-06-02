"use client";

import { useState } from "react";

import type { Job } from "../lib/api";

type JobsManagerProps = {
  initialJobs: Job[];
};

type FetchFormState = {
  keyword: string;
  location: string;
  country: string;
  results_per_page: string;
};

export function JobsManager({ initialJobs }: JobsManagerProps) {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);
  const [form, setForm] = useState<FetchFormState>({
    keyword: "python",
    location: "remote",
    country: "gb",
    results_per_page: "10",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState("");

  async function handleFetch(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSubmitting(true);
    setMessage("");

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/fetch`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          keyword: form.keyword,
          location: form.location,
          country: form.country,
          page: 1,
          results_per_page: Number(form.results_per_page),
        }),
      });

      const payload = await response.json();

      if (!response.ok) {
        throw new Error(payload.detail ?? `Job fetch failed with ${response.status}`);
      }

      setJobs(payload.jobs);
      setMessage(`Fetched ${payload.fetched_count} jobs. Inserted ${payload.inserted_count}, updated ${payload.updated_count}.`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Job fetch failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  function updateField(name: keyof FetchFormState, value: string) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  return (
    <>
      <section className="panel panel-form">
        <div className="panel-header">
          <div>
            <span className="panel-label">Fetch Jobs</span>
            <h2>Adzuna ingestion</h2>
          </div>
          <span className={`status-pill ${jobs.length > 0 ? "status-ok" : "status-empty"}`}>{jobs.length} jobs</span>
        </div>

        <form className="profile-form" onSubmit={handleFetch}>
          <div className="field-row field-row-wide">
            <label>
              Keyword
              <input value={form.keyword} onChange={(event) => updateField("keyword", event.target.value)} />
            </label>
            <label>
              Location
              <input value={form.location} onChange={(event) => updateField("location", event.target.value)} />
            </label>
            <label>
              Country
              <input value={form.country} onChange={(event) => updateField("country", event.target.value)} />
            </label>
            <label>
              Results per page
              <input
                type="number"
                min="1"
                max="50"
                value={form.results_per_page}
                onChange={(event) => updateField("results_per_page", event.target.value)}
              />
            </label>
          </div>

          <div className="form-actions">
            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Fetching..." : "Fetch jobs"}
            </button>
            <span className="form-message">{message}</span>
          </div>
        </form>
      </section>

      <section className="panel">
        <span className="panel-label">Stored Jobs</span>
        {jobs.length > 0 ? (
          <div className="job-list">
            {jobs.map((job) => (
              <article key={job.id} className="job-card">
                <div className="job-copy">
                  <h3>{job.title}</h3>
                  <p>{job.company || "Unknown company"}</p>
                  <p>{job.description?.slice(0, 220) || "No description available."}</p>
                </div>
                <div className="job-meta">
                  <span>{job.location || "Unknown location"}</span>
                  <span>{job.salary_min ?? "?"} - {job.salary_max ?? "?"}</span>
                  {job.url ? (
                    <a href={job.url} target="_blank" rel="noreferrer">
                      Source
                    </a>
                  ) : null}
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p>No jobs stored yet.</p>
        )}
      </section>
    </>
  );
}
