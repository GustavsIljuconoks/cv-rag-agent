import { getProfile } from "../../lib/api";
import { ProfileForm } from "../../components/profile-form";

export default async function ProfilePage() {
  const profile = await getProfile();

  return (
    <main className="page">
      <section className="hero-card">
        <div>
          <span className="eyebrow">Profile</span>
          <h1>Maintain the single candidate profile the backend uses for matching.</h1>
          <p className="hero-copy">
            This page currently maps to `POST /profile`, `GET /profile`, and `PUT /profile`.
          </p>
        </div>
      </section>
      <ProfileForm initialProfile={profile} />
    </main>
  );
}
