"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import type { Profile } from "../lib/api";

type ProfileFormProps = {
  initialProfile: Profile | null;
};

type FormState = {
  summary: string;
  preferred_roles: string;
  preferred_locations: string;
  preferred_remote_type: string;
  preferred_technologies: string;
  salary_expectation_min: string;
  salary_expectation_max: string;
};

function toFormState(profile: Profile | null): FormState {
  return {
    summary: profile?.summary ?? "",
    preferred_roles: profile?.preferred_roles ?? "",
    preferred_locations: profile?.preferred_locations ?? "",
    preferred_remote_type: profile?.preferred_remote_type ?? "",
    preferred_technologies: profile?.preferred_technologies ?? "",
    salary_expectation_min: profile?.salary_expectation_min?.toString() ?? "",
    salary_expectation_max: profile?.salary_expectation_max?.toString() ?? "",
  };
}

function toPayload(form: FormState) {
  return {
    summary: form.summary || null,
    preferred_roles: form.preferred_roles || null,
    preferred_locations: form.preferred_locations || null,
    preferred_remote_type: form.preferred_remote_type || null,
    preferred_technologies: form.preferred_technologies || null,
    salary_expectation_min: form.salary_expectation_min ? Number(form.salary_expectation_min) : null,
    salary_expectation_max: form.salary_expectation_max ? Number(form.salary_expectation_max) : null,
  };
}

export function ProfileForm({ initialProfile }: ProfileFormProps) {
  const router = useRouter();
  const [form, setForm] = useState<FormState>(() => toFormState(initialProfile));
  const [message, setMessage] = useState<string>("");
  const [isSaving, setIsSaving] = useState(false);
  const [mode, setMode] = useState<"create" | "update">(initialProfile ? "update" : "create");

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsSaving(true);
    setMessage("");

    const method = mode === "create" ? "POST" : "PUT";

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/profile`, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(toPayload(form)),
      });

      if (!response.ok) {
        throw new Error(`Profile request failed with ${response.status}`);
      }

      setMode("update");
      setMessage("Profile saved.");
      router.refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Profile request failed.");
    } finally {
      setIsSaving(false);
    }
  }

  function updateField(name: keyof FormState, value: string) {
    setForm((current) => ({ ...current, [name]: value }));
  }

  return (
    <section className="panel panel-form">
      <div className="panel-header">
        <div>
          <span className="panel-label">Candidate Profile</span>
          <h2>{mode === "create" ? "Create profile" : "Update profile"}</h2>
        </div>
        <span className={`status-pill ${mode === "create" ? "status-empty" : "status-ok"}`}>{mode}</span>
      </div>

      <form className="profile-form" onSubmit={handleSubmit}>
        <label>
          Summary
          <textarea
            rows={5}
            value={form.summary}
            onChange={(event) => updateField("summary", event.target.value)}
          />
        </label>

        <label>
          Preferred roles
          <input
            value={form.preferred_roles}
            onChange={(event) => updateField("preferred_roles", event.target.value)}
          />
        </label>

        <label>
          Preferred locations
          <input
            value={form.preferred_locations}
            onChange={(event) => updateField("preferred_locations", event.target.value)}
          />
        </label>

        <label>
          Preferred remote type
          <input
            value={form.preferred_remote_type}
            onChange={(event) => updateField("preferred_remote_type", event.target.value)}
          />
        </label>

        <label>
          Preferred technologies
          <textarea
            rows={4}
            value={form.preferred_technologies}
            onChange={(event) => updateField("preferred_technologies", event.target.value)}
          />
        </label>

        <div className="field-row">
          <label>
            Salary min
            <input
              type="number"
              value={form.salary_expectation_min}
              onChange={(event) => updateField("salary_expectation_min", event.target.value)}
            />
          </label>

          <label>
            Salary max
            <input
              type="number"
              value={form.salary_expectation_max}
              onChange={(event) => updateField("salary_expectation_max", event.target.value)}
            />
          </label>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={isSaving}>
            {isSaving ? "Saving..." : mode === "create" ? "Create profile" : "Save changes"}
          </button>
          <span className="form-message">{message}</span>
        </div>
      </form>
    </section>
  );
}
