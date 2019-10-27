from app import db

followers = db.Table('followers',
                     db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer, db.ForeignKey('user.id')), extend_existing=True
                     )


class User(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, unique=True)

    username = db.Column(db.String(140))
    phone_number = db.Column(db.String(140))

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
