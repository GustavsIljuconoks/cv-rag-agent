import { JobsManager } from "../../components/jobs-manager";
import { getJobs } from "../../lib/api";

export default async function JobsPage() {
  const jobs = await getJobs();

  return (
    <main className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Jobs</span>
          <h1>Fetch jobs from Adzuna and inspect what is already stored in PostgreSQL.</h1>
          <p className="hero-copy">
            This page maps to `POST /jobs/fetch` and `GET /jobs`. Adzuna credentials must be present in the backend
            environment before fetch will succeed.
          </p>
        </div>
      </section>
      <JobsManager initialJobs={jobs} />
    </main>
  );
}
