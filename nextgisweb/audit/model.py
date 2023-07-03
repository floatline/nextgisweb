import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

from nextgisweb.env import declarative_base

Base = declarative_base()

tab_log = sa.Table(
    'audit_log', Base.metadata,
    sa.Column('tstamp', sa.DateTime),
    sa.Column('request_method', sa.String),
    sa.Column('request_path', sa.String),
    sa.Column('request_remote_addr', sa.String),
    sa.Column('response_status_code', sa.Integer),
    sa.Column('route_name', sa.String),
    sa.Column('user_id', sa.Integer),
    sa.Column('user_display_name', sa.String),
    sa.Column('data', pg.JSONB),
)

# tab_sink = sa.Table(
#     'audit_sink', Base.metadata,
#     sa.Column('id', sa.Text, primary_key=True),
#     sa.Column('pos', sa.BigInteger, nullable=False),
#     sa.Column('updated', sa.DateTime, nullable=False),
#     sa.Column('deleted', sa.DateTime, nullable=True),
# )

