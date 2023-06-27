"""added access begin and end to users table

Revision ID: d1eae6045afc
Revises: 3a25c4a34af5
Create Date: 2022-12-04 20:15:02.961560+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd1eae6045afc'
down_revision = '3a25c4a34af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('access_begin', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('access_end', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'access_end')
    op.drop_column('users', 'access_begin')
    # ### end Alembic commands ###
