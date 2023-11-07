from FlaskTV import db, login_manager
from FlaskTV import bcrypt
from flask_login import UserMixin
from FlaskTV import func


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(length=30), nullable=False, unique=True)
    email_address = db.Column(db.String(length=50), nullable=False, unique=True)
    password_hash = db.Column(db.String(length=60), nullable=False)
    modified_pages = db.relationship('Page', backref='owned_user', lazy=True)

    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)


class Page(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(length=255), nullable=False)
    file = db.Column(db.String(length=255), nullable=False)
    time = db.Column(db.Integer(), nullable=False)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    enabled = db.Column(db.Boolean(), nullable=False)

    def __repr__(self):
        return f'Page name {self.name}\nFile {self.file}\nTime {self.time}\nOwner {self.owner}'

    @property
    def creator(self):
        return User.query.filter_by(id=self.owner).first()


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    owner = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    comment = db.Column(db.String(length=255), nullable=False)
    action = db.Column(db.String(length=255), nullable=False)
    pagefile_related = db.Column(db.String(length=255), nullable=True)
    time_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    @property
    def creator(self):
        return User.query.filter_by(id=self.owner).first()
