"""proxy

Revision ID: cccca093ce60
Revises: dc65384e2010
Create Date: 2022-12-29 18:08:11.220441

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'cccca093ce60'
down_revision = 'dc65384e2010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('proxy',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('scheme', sa.String(length=16), nullable=True),
    sa.Column('host', sa.String(length=16), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('login', sa.String(length=32), nullable=True),
    sa.Column('password', sa.String(length=32), nullable=True),
    sa.Column('uses', sa.Integer(), server_default='0', nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('proxy')
    # ### end Alembic commands ###