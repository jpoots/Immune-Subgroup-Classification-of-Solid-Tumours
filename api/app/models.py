from app import db


# helped by https://www.youtube.com/watch?v=PppslXOR7TA
class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    pass_hash = db.Column(db.String(80), unique=True, nullable=False)

    def to_json(self):
        return {"id": self.id, "username": self.username, "passHash": self.pass_hash}
