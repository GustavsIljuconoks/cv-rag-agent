import re
from dataclasses import dataclass

from app.db.models import CandidateProfile, Job

MATCH_RUN_JOB_LIMIT = 100
APPLY_THRESHOLD = 70
CONSIDER_THRESHOLD = 50
SCORING_VERSION = "deterministic-v1"

SKILL_WEIGHT = 30
ROLE_WEIGHT = 20
LOCATION_WEIGHT = 30
SALARY_WEIGHT = 20


@dataclass
class TransientMatchDetails:
    matched_skills: list[str]
    missing_skills: list[str]


@dataclass
class MatchResult:
    job: Job
    match_score: int
    skill_score: int
    location_score: int
    salary_score: int
    interest_score: int
    explanation: str
    recommendation: str
    matched_skills: list[str]
    missing_skills: list[str]


def match_jobs(profile: CandidateProfile, jobs: list[Job]) -> list[MatchResult]:
    results = [_score_job(profile, job) for job in jobs]
    return sorted(
        results,
        key=lambda result: (
            -result.match_score,
            _sort_text(result.job.title),
            result.job.id,
        ),
    )


def derive_transient_match_details(
    profile: CandidateProfile, job: Job
) -> TransientMatchDetails:
    preferred_skills = _split_preferences(profile.preferred_technologies)
    matched_skills = _find_matches(preferred_skills, _job_text(job))
    missing_skills = [
        skill for skill in preferred_skills if skill not in matched_skills
    ]
    return TransientMatchDetails(
        matched_skills=matched_skills, missing_skills=missing_skills
    )


def build_recommendation(match_score: int) -> str:
    if match_score >= APPLY_THRESHOLD:
        return "apply"

    if match_score >= CONSIDER_THRESHOLD:
        return "consider"

    return "skip"


def _score_job(profile: CandidateProfile, job: Job) -> MatchResult:
    transient = derive_transient_match_details(profile, job)
    preferred_skills = _split_preferences(profile.preferred_technologies)
    preferred_roles = _split_preferences(profile.preferred_roles)

    skill_score = _score_skill_alignment(preferred_skills, transient.matched_skills)
    interest_score = _score_role_alignment(preferred_roles, job.title or "")
    location_score = _score_location_alignment(profile, job)
    salary_score = _score_salary_alignment(profile, job)
    match_score = skill_score + interest_score + location_score + salary_score
    recommendation = build_recommendation(match_score)
    explanation = _build_explanation(
        preferred_skills=preferred_skills,
        matched_skills=transient.matched_skills,
        preferred_roles=preferred_roles,
        interest_score=interest_score,
        location_score=location_score,
        salary_score=salary_score,
    )

    return MatchResult(
        job=job,
        match_score=match_score,
        skill_score=skill_score,
        location_score=location_score,
        salary_score=salary_score,
        interest_score=interest_score,
        explanation=explanation,
        recommendation=recommendation,
        matched_skills=transient.matched_skills,
        missing_skills=transient.missing_skills,
    )


def _score_skill_alignment(
    preferred_skills: list[str], matched_skills: list[str]
) -> int:
    if not preferred_skills:
        return SKILL_WEIGHT // 2

    ratio = len(matched_skills) / len(preferred_skills)
    return round(SKILL_WEIGHT * ratio)


def _score_role_alignment(preferred_roles: list[str], title: str) -> int:
    if not preferred_roles:
        return ROLE_WEIGHT // 2

    normalized_title = _search_text(title)
    matched_roles = _find_matches(preferred_roles, normalized_title)
    ratio = len(matched_roles) / len(preferred_roles)
    return round(ROLE_WEIGHT * ratio)


def _score_location_alignment(profile: CandidateProfile, job: Job) -> int:
    preferred_locations = _split_preferences(profile.preferred_locations)
    remote_preference = _normalize_option(profile.preferred_remote_type)
    job_location = _search_text(job.location or "")
    job_remote_type = _normalize_option(job.remote_type)

    if not preferred_locations and not remote_preference:
        return LOCATION_WEIGHT // 2

    scores: list[int] = []

    if preferred_locations:
        if job_location and any(
            _search_text(location) in job_location for location in preferred_locations
        ):
            scores.append(LOCATION_WEIGHT)
        elif not job_location:
            scores.append(LOCATION_WEIGHT // 2)
        else:
            scores.append(0)

    if remote_preference:
        if job_remote_type == "remote":
            scores.append(LOCATION_WEIGHT)
        elif job_remote_type == "hybrid":
            scores.append(round(LOCATION_WEIGHT * 0.7))
        elif not job_remote_type:
            scores.append(LOCATION_WEIGHT // 2)
        else:
            scores.append(0)

    if not scores:
        return LOCATION_WEIGHT // 2

    return round(sum(scores) / len(scores))


def _score_salary_alignment(profile: CandidateProfile, job: Job) -> int:
    expected_min, expected_max = _normalize_range(
        profile.salary_expectation_min,
        profile.salary_expectation_max,
    )
    job_min, job_max = _normalize_range(job.salary_min, job.salary_max)

    if expected_min is None and expected_max is None:
        return SALARY_WEIGHT // 2

    if job_min is None and job_max is None:
        return SALARY_WEIGHT // 2

    if expected_min is not None and job_max is not None and job_max < expected_min:
        return 0

    if _ranges_overlap(expected_min, expected_max, job_min, job_max):
        return SALARY_WEIGHT

    if expected_max is not None and job_min is not None and job_min > expected_max:
        return SALARY_WEIGHT

    return SALARY_WEIGHT // 2


def _build_explanation(
    *,
    preferred_skills: list[str],
    matched_skills: list[str],
    preferred_roles: list[str],
    interest_score: int,
    location_score: int,
    salary_score: int,
) -> str:
    clauses: list[str] = []

    if preferred_roles:
        if interest_score >= round(ROLE_WEIGHT * 0.6):
            clauses.append("Role alignment looks strong.")
        elif interest_score == 0:
            clauses.append("Role alignment looks weak.")

    if preferred_skills:
        clauses.append(
            f"Matched {len(matched_skills)}/{len(preferred_skills)} preferred technologies."
        )

    if location_score >= round(LOCATION_WEIGHT * 0.75):
        clauses.append("Location or remote setup fits the profile.")
    elif location_score <= round(LOCATION_WEIGHT * 0.25):
        clauses.append("Location or remote setup is a weak fit.")

    if salary_score == SALARY_WEIGHT:
        clauses.append("Salary looks compatible with expectations.")
    elif salary_score == 0:
        clauses.append("Salary appears below the expected minimum.")

    if not clauses:
        return "This result is based on a lightweight deterministic profile-to-job comparison."

    return " ".join(clauses[:3])


def _split_preferences(value: str | None) -> list[str]:
    if not value:
        return []

    parts = re.split(r"[\n,;]+", value)
    result: list[str] = []
    seen: set[str] = set()

    for part in parts:
        cleaned = _clean_display_value(part)
        normalized = _search_text(cleaned)
        if not cleaned or not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(cleaned)

    return result


def _find_matches(preferences: list[str], haystack: str) -> list[str]:
    matches: list[str] = []

    for preference in preferences:
        if _search_text(preference) in haystack:
            matches.append(preference)

    return matches


def _job_text(job: Job) -> str:
    return _search_text(" ".join(filter(None, [job.title, job.description])))


def _normalize_range(
    minimum: int | None, maximum: int | None
) -> tuple[int | None, int | None]:
    if minimum is None and maximum is None:
        return None, None

    if minimum is None:
        return maximum, maximum

    if maximum is None:
        return minimum, minimum

    return min(minimum, maximum), max(minimum, maximum)


def _ranges_overlap(
    first_min: int | None,
    first_max: int | None,
    second_min: int | None,
    second_max: int | None,
) -> bool:
    if (
        first_min is None
        or first_max is None
        or second_min is None
        or second_max is None
    ):
        return False

    return max(first_min, second_min) <= min(first_max, second_max)


def _normalize_option(value: str | None) -> str:
    return _search_text(value or "")


def _clean_display_value(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _search_text(value: str) -> str:
    lowered = value.lower()
    normalized = re.sub(r"[^\w+#./ ]+", " ", lowered, flags=re.UNICODE)
    return re.sub(r"\s+", " ", normalized).strip()


def _sort_text(value: str | None) -> str:
    return _search_text(value or "")
