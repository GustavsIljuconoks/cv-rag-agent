import unittest
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes.jobs import router as jobs_router
from app.api.routes.matches import router as matches_router
from app.api.routes.profile import router as profile_router
from app.db.base import Base
from app.db.models import CandidateProfile, Job, JobMatch
from app.db.session import get_db


class MatchesApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            "sqlite+pysqlite:///:memory:",
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
            class_=Session,
        )
        Base.metadata.create_all(bind=self.engine)

        self.app = FastAPI()
        self.app.include_router(profile_router)
        self.app.include_router(jobs_router)
        self.app.include_router(matches_router)
        self.app.dependency_overrides[get_db] = self._get_db_override

        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def tearDown(self) -> None:
        self.app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()

    def test_get_matches_returns_empty_snapshot_metadata_when_nothing_exists(self) -> None:
        response = self.client.get("/matches")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "has_snapshot": False,
                "is_stale": False,
                "evaluated_count": 0,
                "last_run_at": None,
                "profile_updated_at": None,
                "snapshot_profile_updated_at": None,
                "scoring_version": None,
                "matches": [],
            },
        )

    def test_run_matches_replaces_existing_snapshot_instead_of_duplicating_rows(self) -> None:
        profile = self._create_profile()
        self._create_job(external_id="job-1", title="Python Engineer", posted_offset_minutes=2)
        self._create_job(external_id="job-2", title="Data Engineer", posted_offset_minutes=1)

        first_run = self.client.post("/matches/run")
        self.assertEqual(first_run.status_code, 200)
        self.assertEqual(first_run.json()["evaluated_count"], 2)
        self.assertEqual(first_run.json()["scoring_version"], "deterministic-v1")

        second_run = self.client.post("/matches/run")
        self.assertEqual(second_run.status_code, 200)
        self.assertEqual(second_run.json()["evaluated_count"], 2)

        with self.SessionLocal() as db:
            stored_matches = list(
                db.scalars(select(JobMatch).where(JobMatch.candidate_profile_id == profile.id))
            )

        self.assertEqual(len(stored_matches), 2)
        self.assertTrue(all(match.scoring_version == "deterministic-v1" for match in stored_matches))
        self.assertTrue(all(match.profile_updated_at_snapshot is not None for match in stored_matches))

    def test_get_matches_marks_snapshot_stale_after_profile_update(self) -> None:
        profile = self._create_profile()
        self._create_job(external_id="job-1", title="Python Engineer", posted_offset_minutes=1)

        run_response = self.client.post("/matches/run")
        self.assertEqual(run_response.status_code, 200)
        last_run_at = datetime.fromisoformat(run_response.json()["last_run_at"].replace("Z", "+00:00"))

        with self.SessionLocal() as db:
            stored_profile = db.get(CandidateProfile, profile.id)
            assert stored_profile is not None
            stored_profile.updated_at = last_run_at + timedelta(minutes=5)
            db.commit()

        response = self.client.get("/matches")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["has_snapshot"])
        self.assertTrue(response.json()["is_stale"])
        self.assertEqual(
            response.json()["snapshot_profile_updated_at"],
            run_response.json()["snapshot_profile_updated_at"],
        )

    def test_run_matches_only_scores_100_most_recent_jobs(self) -> None:
        self._create_profile()

        for index in range(101):
            self._create_job(
                external_id=f"job-{index}",
                title=f"Python Engineer {index}",
                posted_offset_minutes=index,
            )

        response = self.client.post("/matches/run")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["evaluated_count"], 100)
        self.assertEqual(payload["scoring_version"], "deterministic-v1")

        stored_ids = {match["job"]["external_id"] for match in payload["matches"]}
        self.assertNotIn("job-0", stored_ids)
        self.assertIn("job-100", stored_ids)

        with self.SessionLocal() as db:
            stored_match_count = len(list(db.scalars(select(JobMatch))))

        self.assertEqual(stored_match_count, 100)

    def _create_profile(self) -> CandidateProfile:
        profile = CandidateProfile(
            summary="Test profile",
            preferred_roles="Python Engineer",
            preferred_locations="Riga",
            preferred_remote_type=None,
            preferred_technologies="Python",
            salary_expectation_min=1500,
            salary_expectation_max=2500,
        )

        with self.SessionLocal() as db:
            db.add(profile)
            db.commit()
            db.refresh(profile)

        return profile

    def _create_job(self, *, external_id: str, title: str, posted_offset_minutes: int) -> Job:
        base_time = datetime(2026, 6, 1, tzinfo=timezone.utc)
        job = Job(
            source="nva",
            external_id=external_id,
            title=title,
            company="Example Co",
            location="Riga",
            remote_type=None,
            salary_min=1800,
            salary_max=2200,
            description="Python work",
            url=f"https://example.test/{external_id}",
            posted_at=base_time + timedelta(minutes=posted_offset_minutes),
        )

        with self.SessionLocal() as db:
            db.add(job)
            db.commit()
            db.refresh(job)

        return job

    def _get_db_override(self):
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()


if __name__ == "__main__":
    unittest.main()
