import secrets
import os
from PIL import Image 
from flask import render_template, url_for, flash, redirect, request, abort
from courseco import app, db, bcrypt, mail
from courseco.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
							ReviewForm, RequestResetForm, ResetPasswordForm)
from courseco.models import User, Course, Review
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
	# create a query in the url with name '_page' and default value of 1 and with type int
	page = request.args.get('_page', 1, type=int) 
	courses = Course.query.order_by(Course.date_posted.desc()).paginate(page=page, per_page=5)
	return render_template('home.html', courses=courses)


@app.route('/about/')
def about():
	return render_template('about.html', title='About')


@app.route('/register/', methods=['GET', 'POST'])
def register():
	# if the user is already logged in
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data.lower(), password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to login', 'success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Invalid credentials. Try Again.', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route('/logout/')
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_picture):
	# randomize the name of the file
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename) # get the file's name
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path)

	return picture_fn


@app.route('/account/', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data: # DELETE OLD IMAGES
			old_image_file = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
			if os.path.isfile(old_image_file) and current_user.image_file != 'default.jpg':
				os.remove(old_image_file)
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file

		current_user.username = form.username.data
		current_user.email = form.email.data.lower()
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		# initiate with the current data
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', 
							image_file=image_file, form=form)


def calc_rate(course_id):
	course = Course.query.filter_by(id=course_id).first()
	reviews = Review.query.filter_by(course_id=course.id)
	if not reviews.count():
		course.avg_rate = None
		db.session.commit()
		return
	avg_rate = 0
	for review in reviews:
		avg_rate += review.rate
	avg_rate /= reviews.count()
	course.avg_rate = avg_rate
	db.session.commit()


@app.route('/home/<int:course_id>', methods=['GET', 'POST']) # expect an int
def course_page(course_id):
	page = request.args.get('_page', 1, type=int) 
	# if it doesn't exist return 404
	course = Course.query.get_or_404(course_id)
	reviews = Review.query.filter_by(course_id=course.id)\
	.order_by(Review.date_posted.desc())\
	.paginate(page=page, per_page=5)
	current_review = None
	if current_user.is_authenticated:
		current_review = Review.query.filter_by(user_id=current_user.id).filter_by(course_id=course.id).first()
		reviews = Review.query.filter_by(course_id=course.id)\
		.filter(Review.user_id!=current_user.id)\
		.order_by(Review.date_posted.desc())\
		.paginate(page=page, per_page=5)
	form = ReviewForm()
	if form.validate_on_submit():
		review = Review(rate=form.rate.data, content=form.content.data, user_id=current_user.id, course_id=course.id) # or author=current_user.id
		db.session.add(review)
		db.session.commit()
		calc_rate(course.id)
		flash('Your review has been added!', 'success')
		return redirect(url_for('course_page', course_id=course.id))
	return render_template('course_page.html', form=form
			, course=course, reviews=reviews, current_review=current_review)


@app.route('/review/<int:review_id>')
def review(review_id):
	review = Review.query.get_or_404(review_id)
	return render_template('review.html', review=review)


@app.route('/home/<int:review_id>/update', methods=['GET', 'POST'])
@login_required
def update_review(review_id):
	review = Review.query.get_or_404(review_id)
	if review.reviewer != current_user:
		abort(403) # forbidden
	form = ReviewForm()
	if form.validate_on_submit():
		review.rate = form.rate.data
		review.content = form.content.data
		db.session.commit()
		calc_rate(review.course_id)
		flash('Your review has been updated!', 'success')
		return redirect(url_for('course_page', course_id=review.course_id))
	elif request.method == 'GET':
		form.rate.default = review.rate
		form.process()
		form.content.data = review.content
	return render_template('update_review.html', title='Update Review', form=form)


@app.route('/home/<int:review_id>/delete', methods=['POST'])
@login_required
def delete_review(review_id):
	review = Review.query.get_or_404(review_id)
	if review.reviewer != current_user:
		abort(403)
	db.session.delete(review)
	db.session.commit()
	calc_rate(review.course_id)
	flash('Your review has been deleted!', 'success')
	return redirect(url_for('home'))


def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request',
				sender='sender_test@gmail.com',
				recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link or copy it to your browser:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
	mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		send_reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)
	


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)
	if user is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to login', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)


# --------------------------errors--------------------------------------


@app.errorhandler(404)
def error_404(error):
	return render_template('errors/404.html'), 404


@app.errorhandler(403)
def error_403(error):
	return render_template('errors/403.html'), 403


@app.errorhandler(500)
def error_500(error):
	return render_template('errors/500.html'), 500
