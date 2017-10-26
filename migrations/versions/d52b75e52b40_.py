"""empty message

Revision ID: d52b75e52b40
Revises: 247bc31d03eb
Create Date: 2017-10-26 01:30:31.689517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd52b75e52b40'
down_revision = '247bc31d03eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('resources', sa.Column('is_public', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('resources', 'is_public')
    # ### end Alembic commands ###