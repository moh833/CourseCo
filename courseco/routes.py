import secrets
import os
from PIL import Image 
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from courseco import app, db, bcrypt, mail
from courseco.forms import (RegistrationForm, LoginForm, UpdateAccountForm, 
							ReviewForm, RequestResetForm, ResetPasswordForm, ListForm)
from courseco.models import User, Course, Review, List
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message


@app.route('/')
@app.route('/home')
def home():
	# create a query in the url with name '_page' and default value of 1 and with type int
	page = request.args.get('_page', 1, type=int) 
	courses = Course.query.order_by(Course.date_posted.asc()).paginate(page=page, per_page=6)
	return render_template('home.html', courses=courses)


@app.route('/about')
def about():
	return render_template('about.html', title='About')


@app.route('/contact')
def contact():
	return render_template('contact.html', title='Contact')


@app.route('/register', methods=['GET', 'POST'])
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
	return render_template('signup.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			if len(current_user.reviews) == 0:
				flash(f'Rate 5 Courses so we can recommend courses for you!', 'info')
			elif len(current_user.reviews) < 5:
				flash(f'Rate more {5-len(current_user.reviews)} Courses so we can recommend courses for you!', 'info')
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Invalid credentials. Try Again.', 'danger')
	return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))


def save_picture(form_picture):
	# randomize the name of the file
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename) # get the file's name
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	
	# output_size = (125, 125)
	output_size = (250, 250)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path)

	return picture_fn


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	user_list = List.query.filter_by(user_id=current_user.id)
	user_reviews = Review.query.filter_by(user_id=current_user.id)
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
	return render_template('profile.html', title='Account', 
							image_file=image_file, form=form, user_list=user_list,
							 user_reviews=user_reviews)


def calc_rate(course_id):
	course_id = int(course_id)
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
	course.avg_rate = round(avg_rate, 1)
	db.session.commit()



@app.route('/list_form', methods=['POST'])
@login_required
def add_to_list():
	course_id = int(request.form['course_id'])
	# course = Course.query.get_or_404(course_id)
	current_l = None
	if current_user.is_authenticated:
		current_l = List.query.filter_by(user_id=current_user.id).filter_by(course_id=course_id).first()
	else:
		abort(403)
	status = request.form['status']
	if not current_l:
		l = List(status=status, user_id=current_user.id, course_id=course_id) # or author=current_user.id
		db.session.add(l)
		db.session.commit()
	else:
		current_l.status = status
		db.session.commit()
	return jsonify({'status' : status})


@app.route('/delete_list', methods=['POST'])
@login_required
def delete_list():
	course_id = int(request.form['course_id'])
	# course = Course.query.get_or_404(course_id)
	l = List.query.filter_by(user_id=current_user.id).filter_by(course_id=course_id).first()
	# if review.reviewer != current_user:
	# 	abort(403)
	if l:
		db.session.delete(l)
		db.session.commit()
		return jsonify({'done' : 'The course has been deleted from your list.'})
	else:
		return jsonify({'error' : 'This course is not in your list yet.'})


# @app.route('/review_form', methods=['POST'])
# @login_required
# def add_review():
# 	course_id = int(request.form['course_id'])
# 	course = Course.query.get_or_404(course_id)
# 	current_review = None
# 	if current_user.is_authenticated:
# 		current_review = Review.query.filter_by(user_id=current_user.id).filter_by(course_id=course.id).first()
# 	else:
# 		abort(403)
# 	rate = float(request.form['rate'])
# 	content = request.form['content']
# 	if not current_review:
# 		review = Review(rate=rate, content=content, user_id=current_user.id, course_id=course.id) # or author=current_user.id
# 		db.session.add(review)
# 		db.session.commit()
# 		calc_rate(course.id)
# 	else:
# 		current_review.rate = rate
# 		current_review.content = content
# 		db.session.commit()
# 		calc_rate(course.id)
# 	return jsonify({'rate' : rate, 'content': content})



# @app.route('/delete_review', methods=['POST'])
# @login_required
# def delete_review():
# 	course_id = int(request.form['course_id'])
# 	review = Review.query.filter_by(user_id=current_user.id).filter_by(course_id=course_id).first()
# 	# if review.reviewer != current_user:
# 	# 	abort(403)
# 	if review:
# 		db.session.delete(review)
# 		db.session.commit()
# 		calc_rate(review.course_id)
# 		return jsonify({'done' : 'Your review has been deleted.'})
# 	else:
# 		return jsonify({'error' : "You don't have a review for this course yet."})


@app.route('/delete_review/<int:course_id>', methods=['GET', 'POST'])
@login_required
def delete_review(course_id):
	review = Review.query.filter_by(course_id=course_id).filter_by(user_id=current_user.id).first()
	if not review:
		flash('You don\'t have a review yet to delete!', 'danger')
		return redirect(url_for('course_page', course_id=course_id))
	if review.reviewer != current_user:
		abort(403)
	db.session.delete(review)
	db.session.commit()
	calc_rate(course_id)
	flash('Your review has been deleted!', 'success')
	return redirect(url_for('course_page', course_id=course_id))




@app.route('/home/<int:course_id>', methods=['GET', 'POST']) # expect an int
def course_page(course_id):
	# page = request.args.get('_page', 1, type=int) 
	# if it doesn't exist return 404
	course = Course.query.get_or_404(course_id)
	reviews = Review.query.filter_by(course_id=course.id)\
	.order_by(Review.date_posted.desc())
	# reviews = Review.query.filter_by(course_id=course.id)\
	# .order_by(Review.date_posted.desc())\
	# .paginate(page=page, per_page=5)
	current_review = None
	current_l = None
	if current_user.is_authenticated:
		current_review = Review.query.filter_by(user_id=current_user.id).filter_by(course_id=course.id).first()
		current_l = List.query.filter_by(user_id=current_user.id).filter_by(course_id=course.id).first()
		reviews = Review.query.filter_by(course_id=course.id)\
		.filter(Review.user_id!=current_user.id)\
		.order_by(Review.date_posted.desc())
		# reviews = Review.query.filter_by(course_id=course.id)\
		# .filter(Review.user_id!=current_user.id)\
		# .order_by(Review.date_posted.desc())\
		# .paginate(page=page, per_page=5)
	review_form = ReviewForm()
	list_form = ListForm()
	if review_form.validate_on_submit():
		if not current_review:
			review = Review(rate=review_form.rate.data, content=review_form.content.data, user_id=current_user.id, course_id=course.id) # or author=current_user.id
			db.session.add(review)
			db.session.commit()
			calc_rate(course.id)
			flash('Your review has been added!', 'success')
		else:
			current_review.rate = review_form.rate.data
			current_review.content = review_form.content.data
			db.session.commit()
			calc_rate(course.id)
			flash('Your review has been updated!', 'success')
		return redirect(url_for('course_page', course_id=course.id))
	# if list_form.validate_on_submit():
	# 	if not current_l:
	# 		l = List(status=list_form.status.data, user_id=current_user.id, course_id=course.id) # or author=current_user.id
	# 		db.session.add(l)
	# 		db.session.commit()
	# 	else:
	# 		current_l.status = list_form.status.data
	# 		db.session.commit()
	# 		flash(f'The course has been added to {list_form.status.data}!', 'success')
	# 		return redirect(url_for('course_page', course_id=course.id))
	elif request.method == 'GET':
		if current_review:
			review_form.rate.default = current_review.rate
			review_form.content.default = current_review.content
		review_form.process()
		if current_l:
			list_form.status.default = current_l.status
		list_form.process()
	return render_template('course.html', review_form=review_form, list_form=list_form
			, course=course, reviews=reviews, current_review=current_review, current_l=current_l)


def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request',
				sender=app.config['MAIL_USERNAME'],
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
