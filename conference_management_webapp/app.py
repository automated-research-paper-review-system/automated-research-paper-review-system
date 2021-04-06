from flask import Flask, render_template, flash, redirect, url_for
import flask
from forms import RegistrationForm, LoginForm, ConferenceForm, Paper
from flask_pymongo import PyMongo
from datetime import datetime
from bson import ObjectId

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/conference_management'
mongo = PyMongo(app)
db = mongo.db


def serialize_objectid(response):
    if response:
        if '_id' in response:
            if isinstance(response['_id'], ObjectId):
                response['_id'] = str(response['_id'])
    return response


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created for {form.email.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@admin.com' and form.password.data == 'pas$WorD':
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please enter correct email address and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/conference/new/', methods=['POST', 'GET'])
def create_conference():
    form = ConferenceForm()
    if form.validate_on_submit():
        db.conference.insert_one({
            'name': form.name.data,
            'start_date': form.start_date.data.strftime('%Y-%m-%d'),
            'end_date': form.end_date.data.strftime('%Y-%m-%d'),
            'paper_submission_date': form.paper_submission_date.data.strftime('%Y-%m-%d'),
            'review_submission_date': form.review_submission_date.data.strftime('%Y-%m-%d')
            # 'editor_email': form.editor_email.data,
            # 'created_when': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            # 'updated_when': datetime.utcnow
        })
        flash(f'Created conference: {form.name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('create_conference.html', title='Create Conference', form=form)


@app.route('/conference/', methods=['POST', 'GET'])
def conference():
    form = ConferenceForm()
    form_fields = [field for field in form if field.name != 'submit' and field.name != 'csrf_token']
    conference_list = db.conference.find()
    conference_list = [serialize_objectid(record) for record in conference_list]
    return render_template('conference.html', form_fields=form_fields, conference_list=conference_list)


@app.route('/conference/update/<id>/', methods=['GET', 'POST'])
def update_conference(id):
    form = ConferenceForm()
    id_dictionary = {'_id': ObjectId(id)}
    conference_record = db.conference.find_one_or_404(id_dictionary)
    if conference_record:
        if form.validate_on_submit():
            updated_conference_record = {'$set': {
                'name': form.name.data,
                'start_date': form.start_date.data.strftime('%Y-%m-%d'),
                'end_date': form.end_date.data.strftime('%Y-%m-%d'),
                'paper_submission_date': form.paper_submission_date.data.strftime('%Y-%m-%d'),
                'review_submission_date': form.review_submission_date.data.strftime('%Y-%m-%d')
                # 'editor_email': form.editor_email.data,
                # 'created_when': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
                # 'updated_when': datetime.utcnow
            }}
            db.conference.update_one(id_dictionary, updated_conference_record)
            return redirect(url_for('conference'))
        form.name.data = conference_record['name']
        form.start_date.data = datetime.strptime(conference_record['start_date'], '%Y-%m-%d')
        form.end_date.data = datetime.strptime(conference_record['end_date'], '%Y-%m-%d')
        form.paper_submission_date.data = datetime.strptime(conference_record['paper_submission_date'], '%Y-%m-%d')
        form.review_submission_date.data = datetime.strptime(conference_record['review_submission_date'], '%Y-%m-%d')
    return render_template('create_conference.html', title='Update Conference', form=form)


@app.route('/conference/delete/<id>', methods=['GET', 'POST'])
def delete_conference(id):
    record = {'_id': ObjectId(id)}
    db.conference.delete_one(record)
    return redirect(url_for('conference'))


@app.route('/submit/paper/<conference_id>', methods=['GET', 'POST'])
def submit_paper(conference_id):
    form = Paper()
    if form.validate_on_submit():
        paper_title = form.paper_title.data
        keywords = form.keywords.data
        abstract = form.abstract.data




if __name__ == '__main__':
    app.run()
