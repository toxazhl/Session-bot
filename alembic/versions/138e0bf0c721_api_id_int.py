"""        api_id: int,

Revision ID: 138e0bf0c721
Revises: dd655e994056
Create Date: 2022-11-14 06:46:45.257570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '138e0bf0c721'
down_revision = 'dd655e994056'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('session', sa.Column('api_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('session', 'api_id')
    # ### end Alembic commands ###
