"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-03 00:00:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "candidate_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("preferred_roles", sa.Text(), nullable=True),
        sa.Column("preferred_locations", sa.Text(), nullable=True),
        sa.Column("preferred_remote_type", sa.String(length=50), nullable=True),
        sa.Column("preferred_technologies", sa.Text(), nullable=True),
        sa.Column("salary_expectation_min", sa.Integer(), nullable=True),
        sa.Column("salary_expectation_max", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_candidate_profiles_id"),
        "candidate_profiles",
        ["id"],
        unique=False,
    )

    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("remote_type", sa.String(length=50), nullable=True),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "source",
            "external_id",
            name="uq_jobs_source_external_id",
        ),
    )
    op.create_index(op.f("ix_jobs_id"), "jobs", ["id"], unique=False)

    op.create_table(
        "job_matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("candidate_profile_id", sa.Integer(), nullable=False),
        sa.Column("match_score", sa.Integer(), nullable=True),
        sa.Column("semantic_score", sa.Integer(), nullable=True),
        sa.Column("skill_score", sa.Integer(), nullable=True),
        sa.Column("seniority_score", sa.Integer(), nullable=True),
        sa.Column("location_score", sa.Integer(), nullable=True),
        sa.Column("salary_score", sa.Integer(), nullable=True),
        sa.Column("interest_score", sa.Integer(), nullable=True),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("recommendation", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_profile_id"], ["candidate_profiles.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_job_matches_id"), "job_matches", ["id"], unique=False)

    op.create_table(
        "applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("candidate_profile_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("cover_letter", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["candidate_profile_id"], ["candidate_profiles.id"]),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_applications_id"), "applications", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_applications_id"), table_name="applications")
    op.drop_table("applications")
    op.drop_index(op.f("ix_job_matches_id"), table_name="job_matches")
    op.drop_table("job_matches")
    op.drop_index(op.f("ix_jobs_id"), table_name="jobs")
    op.drop_table("jobs")
    op.drop_index(op.f("ix_candidate_profiles_id"), table_name="candidate_profiles")
    op.drop_table("candidate_profiles")
