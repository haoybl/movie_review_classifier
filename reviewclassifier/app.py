# Import required libraries
from flask import Flask, render_template, request
from wtforms.form import Form
from wtforms import TextAreaField, validators
from wtforms.validators import DataRequired, Length
import sqlite3
import os
import pickle
import numpy as np

# Load the vectorizer script file
from vectorizer import vect


app = Flask(__name__)

# Unpickle and set up the classification model
current_dir = os.path.dirname(__file__)
clf = pickle.load(open(os.path.join(current_dir,
                                    'pkl_objects/classifier.pkl'), 'rb'))

db = os.path.join(current_dir, 'reviews.sqlite')

def classify(file):
	label = {0:'negative',
	         1:'positive'}
	X = vect.transform([file])
	y = clf.predict(X)[0]
	return label[y], np.max(clf.predict_proba(X))

# Train classification model
def train(file, y):
	X = vect.transform([file])
	clf.partial_fit(X, [y])

# Insert entered reviews into database
def sqlite_insert(path, file, y):
	connection = sqlite3.connect(path)
	c = conn.cursor()
	c.execute("INSERT INTO reviews_db (review, sentiment, date)"\
	" VALUES (?, ?, DATETIME('now'))", (file, y))
	connection.commit()
	connection.close()

app = Flask(__name__)
class MovieReviewForm(Form):
	moviereview = TextAreaField('', [validators.DataRequired(),
	                                 validators.length(min=10)])

@app.route('/')
def index():
	form = MovieReviewForm(request.form)
	return render_template('moviereviewform.html', form=form)

@app.route('/outcomes', methods=['POST'])
def outcomes():
	form = MovieReviewForm(request.form)
	if request.method == 'POST' and form.validate():
		review = request.form['moviereview']
		y, proba = classify(review)
		return render_template('outcomes.html',
	content=review,
	prediction=y,
	probability=round(proba*100, 2))
	return render_template('moviereviewform.html', form=form)

@app.route('/thanks', methods=['POST'])
def thanks():
	return render_template('thanks.html')


if __name__ == '__main__':
	app.run(debug=False) # Turn debug to True while debugging


