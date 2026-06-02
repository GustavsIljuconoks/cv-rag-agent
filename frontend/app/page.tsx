import { getBackendHealth, getProfile } from "../lib/api";

export default async function Home() {
  const [health, profile] = await Promise.all([getBackendHealth(), getProfile()]);

  return (
    <main className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Dashboard</span>
          <h1>Start with the candidate profile, then layer in jobs and matching.</h1>
          <p className="hero-copy">
            The frontend is now talking to the live backend. This first pass only surfaces what the API
            actually supports today.
          </p>
        </div>
      </section>

      <section className="card-grid">
        <article className="panel">
          <span className="panel-label">Backend</span>
          <strong className="status-pill status-ok">{health?.status ?? "offline"}</strong>
          <p>Health endpoint status from `GET /health`.</p>
        </article>

        <article className="panel">
          <span className="panel-label">Profile</span>
          <strong className={`status-pill ${profile ? "status-ok" : "status-empty"}`}>
            {profile ? "configured" : "missing"}
          </strong>
          <p>{profile ? "A candidate profile exists and can be edited." : "No profile has been saved yet."}</p>
        </article>

        <article className="panel">
          <span className="panel-label">Jobs</span>
          <strong className="status-pill status-empty">not started</strong>
          <p>The next backend slice should add job ingestion and listing.</p>
        </article>
      </section>

      <section className="panel">
        <span className="panel-label">Current Profile Snapshot</span>
        {profile ? (
          <div className="profile-summary">
            <h2>{profile.preferred_roles || "Preferred roles not set"}</h2>
            <p>{profile.summary || "No summary added yet."}</p>
            <dl className="summary-grid">
              <div>
                <dt>Location</dt>
                <dd>{profile.preferred_locations || "Not set"}</dd>
              </div>
              <div>
                <dt>Remote</dt>
                <dd>{profile.preferred_remote_type || "Not set"}</dd>
              </div>
              <div>
                <dt>Technologies</dt>
                <dd>{profile.preferred_technologies || "Not set"}</dd>
              </div>
              <div>
                <dt>Salary</dt>
                <dd>
                  {profile.salary_expectation_min ?? "?"} - {profile.salary_expectation_max ?? "?"}
                </dd>
              </div>
            </dl>
          </div>
        ) : (
          <p>Create the first profile from the Profile page to unlock the next slice.</p>
        )}
      </section>
    </main>
  );
}
