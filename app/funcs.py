from database.scritps.db_session import create_session
from database.scritps.models.users import User
from datetime import time, datetime, timezone
from app.request import *


def check_user_in_db(user_id):
    session = create_session()
    user = session.query(User).filter(User.tg_id == user_id).first()
    if user:
        return True
    else:
        return False


def write_to_users(user_id, data):
    session = create_session()
    user = User(tg_id=user_id,
                name=data['name'],
                lat=float(data['loc'].split(',')[0]),
                long=float(data['loc'].split(',')[1]),
                time=time(int(data['time'].split(':')[0]), int(data['time'].split(':')[1])))
    session.add(user)
    session.commit()
        
        
def get_user_name(user_id):
    session = create_session()
    user = session.query(User).filter(User.tg_id == user_id).first()
    return user.name
    
    
def get_user_lat_long(user_id):
    session = create_session()
    user = session.query(User).filter(User.tg_id == user_id).first()
    return [user.lat, user.long]


def get_user_time(user_id):
    session = create_session()
    user = session.query(User).filter(User.tg_id == user_id).first()
    return f'{user.time.hour:02d}:{user.time.minute:02d}'


def update_user_loc(user_id, loc):
    session = create_session()
    user = session.query(User).filter(User.tg_id == user_id).first()
    print(user.lat, user.long)
    user.lat = float(loc.split(',')[0])
    user.long = float(loc.split(',')[1])
    session.commit()
    print(user.lat, user.long)
    
    
def update_user_time(user_id, time_raw: str):
    session = create_session()
    user = session.query(User).filter(User.tg_id == user_id).first()
    user.time = time(int(time_raw.split(':')[0]), int(time_raw.split(':')[1]))
    session.commit()
    
    
def get_all_ids():
    session = create_session()
    users = session.query(User).all()
    ids = []
    for user in users:
        ids.append(user.tg_id)
    return ids
