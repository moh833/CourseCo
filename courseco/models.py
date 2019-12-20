from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from courseco import db, login_manager, app
# UserMixen has many helpful functions like is_authenticated
from flask_login import UserMixin


# reload the user object from the user_id stored in the session
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class User(db.Model, UserMixin):
	# UserMixin manages the sessions
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)		
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False) 

	reviews = db.relationship('Review', backref='reviewer', lazy=True)
	lists = db.relationship('List', backref='user', lazy=True)


	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Course(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	description = db.Column(db.Text, nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	avg_rate = db.Column(db.Float)

	reviews = db.relationship('Review', backref='course', lazy=True)
	lists = db.relationship('List', backref='course', lazy=True)

	def __repr__(self):
		return f"Course('{self.name}', '{self.avg_rate}')"

class Review(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	content = db.Column(db.Text)
	rate = db.Column(db.Integer)

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

	def __repr__(self):
		return f"Review('{self.date_posted}', '{self.rate}')"


class List(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	status = db.Column(db.String(10), nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)