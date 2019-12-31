import pandas as pd
import random
from courseco import db

from courseco.models import User, Course, Review
from courseco.routes import calc_rate

df = pd.read_csv('reviews_data.csv')
list_of_courses = []

for course_id, group in df.groupby('course_id'):
    list_of_courses.append(group)

for course in list_of_courses:
    users_ids = random.sample(range(1, 21), 20)
    for index, row in course.iterrows():
        review = Review(course_id=int(row[0]), user_id=users_ids.pop(), content=row[1], rate=int(row[2]))
        db.session.add(review)
        db.session.commit()
    calc_rate(int(row[0]))