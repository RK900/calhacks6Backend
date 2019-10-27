from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import relationship

from app import db
import datetime

import pytz


def timestamp_to_datetime(seconds, tz=None):
    """Returns a datetime.datetime of seconds in UTC

    :param seconds: timestamp relative to the epoch
    :param tz: timezone of the timestamp
    """
    if tz is None:
        tz = pytz.UTC
    dt = datetime.datetime.fromtimestamp(seconds, tz)
    return dt.astimezone(pytz.UTC)


def utcnow():
    """Returns a current timezone-aware datetime.datetime in UTC
    """
    return datetime.datetime.now(datetime.timezone.utc)


followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')), extend_existing=True
                     )


class User(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, unique=True)

    username = db.Column(db.String(140))
    phone_number = db.Column(db.String(140))
    image = db.Column(db.String(140))
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def get_dic(self):
        return {
            "username": self.username,
            "phone_number": self.id,
            "lat": self.lat,
            "lon": self.lon
        }

    def __repr__(self):
        return "Username: {}, Phone Number: {}, Lat: {}, Lon: {}".format(self.username, self.id, self.lat, self.lon)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def get_messages(self, other_user, num=10):
        query = Messages.query.filter_by(or_(and_(Messages.sender_id == self.id, Messages.receiver_id == other_user.id),
                                             and_(Messages.receiver_id == self.id,
                                                  Messages.sender_id == other_user.id)))
        data = query.order_by(desc(Messages.created_at)).limit(num).all()
        return [{"msg": item.msg, "sender_id": item.id, "created_at": item.created_at.strftime("%m/%d/%Y, %H:%M:%S")}
                for
                item in
                data]


class Messages(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    msg = db.Column(db.String(140))
    created_at = db.Column(db.DateTime, default=utcnow())
    sender_id = db.Column(db.Integer)
    receiver_id = db.Column(db.Integer)
