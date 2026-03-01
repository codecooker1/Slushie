import datetime
import uuid
import bleach
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.String(36), primary_key=True, default=lambda :str(uuid.uuid4()))

    title = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)

    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now(datetime.timezone.utc))

    is_published = db.Column(db.Boolean, nullable=False, default=False)
    token = db.Column(db.String(36), unique=True, nullable=False)

    def create(self, title, name, email, content):
        self.title = bleach.clean(title)
        self.name = bleach.clean(name)
        self.email = bleach.clean(email)
        self.content = bleach.clean(content)

        self.pub_date = datetime.datetime.now()

        self.token = str(uuid.uuid4())

        db.session.add(self)
        db.session.commit()

    def save(self):
        pass

    def delete(self):
        pass

    def __repr__(self):
        return f"<Post '{self.title}' by '{self.name}'>"