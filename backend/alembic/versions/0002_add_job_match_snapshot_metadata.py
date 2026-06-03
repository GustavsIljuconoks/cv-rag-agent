"""add job match snapshot metadata

Revision ID: 0002_match_snapshot_meta
Revises: 0001_initial_schema
Create Date: 2026-06-03 00:30:00

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002_match_snapshot_meta"
down_revision: Union[str, Sequence[str], None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "job_matches",
        sa.Column("scoring_version", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "job_matches",
        sa.Column("profile_updated_at_snapshot", sa.DateTime(timezone=True), nullable=True),
    )

    op.execute("UPDATE job_matches SET scoring_version = 'deterministic-v1'")
    op.execute("UPDATE job_matches SET profile_updated_at_snapshot = created_at")

    op.alter_column("job_matches", "scoring_version", nullable=False)
    op.alter_column("job_matches", "profile_updated_at_snapshot", nullable=False)


def downgrade() -> None:
    op.drop_column("job_matches", "profile_updated_at_snapshot")
    op.drop_column("job_matches", "scoring_version")
