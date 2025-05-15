import sqlalchemy
from database.scritps.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    tg_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    lat = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    long = sqlalchemy.Column(sqlalchemy.Float, nullable=True)
    time = sqlalchemy.Column(sqlalchemy.Time, nullable=True)
    tz = sqlalchemy.Column(sqlalchemy.String, nullable=True)
