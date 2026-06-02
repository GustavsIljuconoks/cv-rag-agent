import { getProfile } from "../../lib/api";
import { ProfileForm } from "../../components/profile-form";

export default async function ProfilePage() {
    const profile = await getProfile();

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
            <ProfileForm initialProfile={profile} />
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
