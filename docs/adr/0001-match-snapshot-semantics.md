# Match Snapshot Semantics For V1

For V1, `job_matches` stores the current snapshot of ranked jobs for the current candidate profile, not a historical log of scoring runs. Each `/matches/run` replaces prior rows for that profile atomically, scores the 100 most recent jobs, persists the existing score fields plus a short explanation and recommendation, freezes the schema for V1, and leaves richer details such as `matched_skills` and `missing_skills` in the API response only. `GET /matches` returns snapshot metadata including whether a snapshot exists and whether it is stale relative to the current profile, because profile edits do not automatically rerun matching.

After V1 stabilization, the snapshot also persists `scoring_version` and `profile_updated_at_snapshot` so the stored rows can be interpreted against the exact deterministic scorer and profile state they were created from, without switching to full historical-run semantics.
