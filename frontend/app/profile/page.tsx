import { getMatches, getProfile } from "../../lib/api";
import { ProfileForm } from "../../components/profile-form";

export default async function ProfilePage() {
    const [profile, matches] = await Promise.all([getProfile(), getMatches()]);

    return (
        <main className="page">
            <section className="hero-card">
                <div>
                    <span className="eyebrow">Profile</span>
                    <h1>
                        Maintain the single candidate profile the backend uses
                        for matching.
                    </h1>
                    <p className="hero-copy">
                        This page currently maps to `POST /profile`, `GET
                        /profile`, and `PUT /profile`.
                    </p>
                </div>
            </section>
            <ProfileForm initialProfile={profile} initialMatches={matches} />
            <section className="panel">
                <span className="panel-label">Match Freshness</span>
                {matches.has_snapshot ? (
                    <div
                        className={`snapshot-banner ${matches.is_stale ? "snapshot-banner-stale" : "snapshot-banner-fresh"}`}
                    >
                        <div>
                            <strong>{matches.is_stale ? "Matches are stale." : "Matches are current."}</strong>
                            <p>
                                {matches.is_stale
                                    ? 'The profile changed after the last match run. Use "Save and rerun matching" or rerun from the dashboard.'
                                    : "The current snapshot still reflects the latest saved profile."}
                            </p>
                        </div>
                        <div className="snapshot-meta">
                            <span>Last run: {matches.last_run_at ? new Date(matches.last_run_at).toLocaleString() : "not available"}</span>
                            <span>Snapshot profile: {matches.snapshot_profile_updated_at ? new Date(matches.snapshot_profile_updated_at).toLocaleString() : "not available"}</span>
                            <span>Ranked jobs: {matches.evaluated_count}</span>
                            <span>Scoring version: {matches.scoring_version || "not available"}</span>
                        </div>
                    </div>
                ) : (
                    <p>No match snapshot yet. Save the profile, fetch jobs, then run matching.</p>
                )}
            </section>
            <section className="panel">
                <span className="panel-label">Saved Profile</span>
                {profile ? (
                    <div className="profile-summary">
                        <h2>
                            {profile.preferred_roles ||
                                "Preferred roles not set"}
                        </h2>
                        <p>{profile.summary || "No summary added yet."}</p>
                        <dl className="summary-grid">
                            <div>
                                <dt>Location</dt>
                                <dd>
                                    {profile.preferred_locations || "Not set"}
                                </dd>
                            </div>
                            <div>
                                <dt>Remote</dt>
                                <dd>
                                    {profile.preferred_remote_type || "Not set"}
                                </dd>
                            </div>
                            <div>
                                <dt>Technologies</dt>
                                <dd>
                                    {profile.preferred_technologies ||
                                        "Not set"}
                                </dd>
                            </div>
                            <div>
                                <dt>Salary</dt>
                                <dd>
                                    {profile.salary_expectation_min ?? "?"} -{" "}
                                    {profile.salary_expectation_max ?? "?"}
                                </dd>
                            </div>
                            <div>
                                <dt>Created</dt>
                                <dd>
                                    {new Date(
                                        profile.created_at,
                                    ).toLocaleString()}
                                </dd>
                            </div>
                            <div>
                                <dt>Updated</dt>
                                <dd>
                                    {new Date(
                                        profile.updated_at,
                                    ).toLocaleString()}
                                </dd>
                            </div>
                        </dl>
                    </div>
                ) : (
                    <p>No saved profile yet.</p>
                )}
            </section>
        </main>
    );
}
