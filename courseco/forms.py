from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from courseco.models import User


rates = [('', 'Rate')] + [(str(x), str(x)) for x in range(1, 6)]
course_list = [('', 'Type'), ('completed', 'Completed'), ('connected', 'Connected'), ('wish', 'Wish'), ('dropped', 'Dropped')]


class RegistrationForm(FlaskForm):
	# add parameter render_kw={'placeholder': 'Username'}
	username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)], render_kw={'autofocus': 'true'})
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)], render_kw={'autocomplete': 'on'})
	password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=50), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data.lower()).first()
		if user:
			raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)], render_kw={'autofocus': 'true', 'autocomplete': 'on'})
	password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)], render_kw={'autofocus': 'true'})
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)], render_kw={'autocomplete': 'on'})
	picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That username is taken. Please choose a different one.')

	def validate_email(self, email):
		if email.data.lower() != current_user.email:
			user = User.query.filter_by(email=email.data.lower()).first()
			if user:
				raise ValidationError('That email is taken. Please choose a different one.')


class ReviewForm(FlaskForm):
	rate = SelectField('Rate', validators=[DataRequired()], choices = rates)
	content = TextAreaField('Content', validators=[DataRequired()])
	submit = SubmitField('Submit')


class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)], render_kw={'autofocus': 'true'})
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data.lower()).first()
		if user is None:
			raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=50), EqualTo('password')])
	submit = SubmitField('Reset Password')


class ListForm(FlaskForm):
	status = SelectField('Type', validators=[DataRequired()], choices=course_list)
	submit = SubmitField('Add')