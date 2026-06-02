import { JobsManager } from "../../components/jobs-manager";
import { getJobs } from "../../lib/api";

export default async function JobsPage() {
  const jobs = await getJobs();

  return (
    <main className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Jobs</span>
          <h1>Fetch jobs from interchangeable sources and inspect what is stored in PostgreSQL.</h1>
          <p className="hero-copy">
            This page maps to `POST /jobs/fetch` and `GET /jobs`. Adzuna and NVA Latvia are implemented, and EURES
            remains an explicit stub.
          </p>
        </div>
      </section>
      <JobsManager initialJobs={jobs} />
    </main>
  );
}
