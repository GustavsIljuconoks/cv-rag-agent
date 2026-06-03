import unittest
from datetime import datetime, timezone

from app.db.models import CandidateProfile, Job
from app.services.matching import (
    APPLY_THRESHOLD,
    CONSIDER_THRESHOLD,
    LOCATION_WEIGHT,
    ROLE_WEIGHT,
    SALARY_WEIGHT,
    SKILL_WEIGHT,
    build_recommendation,
    derive_transient_match_details,
    match_jobs,
)


class MatchingServiceTests(unittest.TestCase):
    def test_strong_match_returns_full_score_breakdown(self) -> None:
        profile = CandidateProfile(
            preferred_roles="Python Engineer",
            preferred_locations="Riga",
            preferred_technologies="Python, FastAPI",
            salary_expectation_min=1500,
            salary_expectation_max=2500,
        )
        job = Job(
            id=1,
            source="nva",
            external_id="job-1",
            title="Python Engineer",
            company="Example Co",
            location="Riga, Latvia",
            remote_type=None,
            salary_min=1800,
            salary_max=2200,
            description="Python FastAPI backend services",
            url="https://example.test/job-1",
            posted_at=datetime.now(timezone.utc),
        )

        result = match_jobs(profile, [job])[0]

        self.assertEqual(result.skill_score, SKILL_WEIGHT)
        self.assertEqual(result.interest_score, ROLE_WEIGHT)
        self.assertEqual(result.location_score, LOCATION_WEIGHT)
        self.assertEqual(result.salary_score, SALARY_WEIGHT)
        self.assertEqual(
            result.match_score,
            SKILL_WEIGHT + ROLE_WEIGHT + LOCATION_WEIGHT + SALARY_WEIGHT,
        )
        self.assertEqual(result.recommendation, "apply")
        self.assertEqual(result.matched_skills, ["Python", "FastAPI"])
        self.assertEqual(result.missing_skills, [])

    def test_remote_and_missing_salary_stay_neutral_not_punitive(self) -> None:
        profile = CandidateProfile(
            preferred_roles="Backend Developer",
            preferred_remote_type="remote",
            preferred_technologies="Python",
        )
        job = Job(
            id=2,
            source="nva",
            external_id="job-2",
            title="Backend Developer",
            company="Remote Co",
            location=None,
            remote_type="remote",
            salary_min=None,
            salary_max=None,
            description="Python API work",
            url="https://example.test/job-2",
            posted_at=datetime.now(timezone.utc),
        )

        result = match_jobs(profile, [job])[0]

        self.assertEqual(result.skill_score, SKILL_WEIGHT)
        self.assertEqual(result.interest_score, ROLE_WEIGHT)
        self.assertEqual(result.location_score, LOCATION_WEIGHT)
        self.assertEqual(result.salary_score, SALARY_WEIGHT // 2)
        self.assertEqual(result.recommendation, "apply")

    def test_transient_skill_details_keep_missing_skills_for_response(self) -> None:
        profile = CandidateProfile(preferred_technologies="Python, FastAPI, Docker")
        job = Job(
            id=3,
            source="nva",
            external_id="job-3",
            title="Python Developer",
            company="Example Co",
            location="Riga",
            remote_type=None,
            salary_min=2000,
            salary_max=2500,
            description="Python APIs with FastAPI",
            url="https://example.test/job-3",
            posted_at=datetime.now(timezone.utc),
        )

        details = derive_transient_match_details(profile, job)

        self.assertEqual(details.matched_skills, ["Python", "FastAPI"])
        self.assertEqual(details.missing_skills, ["Docker"])

    def test_recommendation_thresholds_are_fixed_bands(self) -> None:
        self.assertEqual(build_recommendation(APPLY_THRESHOLD), "apply")
        self.assertEqual(build_recommendation(CONSIDER_THRESHOLD), "consider")
        self.assertEqual(build_recommendation(CONSIDER_THRESHOLD - 1), "skip")


if __name__ == "__main__":
    unittest.main()
