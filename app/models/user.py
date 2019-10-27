from app import db


class User(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, unique=True)

    username = db.Column(db.String(140))
    phone_number = db.Column(db.String(140))

    lat = db.Column(db.Float)
    lon = db.Column(db.Float)

    def get_dic(self):
        return {
            "username": self.username,
            "phone_number": self.id
        }
