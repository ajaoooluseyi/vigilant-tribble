"""added title to role table

Revision ID: 4e2987ca8ec3
Revises: 8c67e47f9d8d
Create Date: 2022-11-30 07:42:28.634322+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e2987ca8ec3'
down_revision = '8c67e47f9d8d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('roles', sa.Column('title', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('roles', 'title')
    # ### end Alembic commands ###
