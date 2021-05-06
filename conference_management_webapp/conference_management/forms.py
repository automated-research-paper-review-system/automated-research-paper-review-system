import re
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, TextAreaField, RadioField
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from conference_management_webapp.conference_management import db


class RegistrationForm(FlaskForm):
    # first_name = StringField('First Name', validators=[DataRequired()])
    # last_name = StringField('Last Name', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        user = db.user.find_one({'email': email.data.strip()})
        if user:
            raise ValidationError('That email is taken. Please choose a different email address or Login.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = RadioField('Role', choices=[('author', 'Author'), ('reviewer', 'Reviewer'), ('editor', 'Editor')],
                      validators=[DataRequired()])
    submit = SubmitField('Login')


class ConferenceForm(FlaskForm):
    name = StringField('Conference Name', validators=[DataRequired()])
    start_date = DateField('Conference Start Date', validators=[DataRequired()])
    end_date = DateField('Conference End Date', validators=[DataRequired()])
    paper_submission_date = DateField('Paper Submission Date', validators=[DataRequired()])
    review_submission_date = DateField('Review Submission Date', validators=[DataRequired()])
    # editor_email = StringField('Creator Email', validators=[Email()])
    submit = SubmitField('Submit')

    def validate_name(self, name):
        conference = db.conference.find_one({'name': name.data.strip()})
        if conference:
            raise ValidationError('Conference name taken. Please give a unique conference name.')

    def validate_start_date(self, start_date):
        if start_date.data < datetime.now().date():
            raise ValidationError('Please set start date greater than or equal to current date.')

    def validate_end_date(self, end_date):
        if self.start_date.data > end_date.data:
            raise ValidationError('Please set end date greater than start date.')

    def validate_paper_submission_date(self, paper_submission_date):
        if not (self.start_date.data <= paper_submission_date.data <= self.end_date.data):
            raise ValidationError('Please set paper submission date >= start date and <= end date.')

    def validate_review_submission_date(self, review_submission_date):
        if not (self.paper_submission_date.data <= review_submission_date.data <= self.end_date.data):
            raise ValidationError('Please set review submission date >= paper submission date and <= end date.')


class UpdateConferenceForm(FlaskForm):
    name = StringField('Conference Name', validators=[DataRequired()])
    start_date = DateField('Conference Start Date', validators=[DataRequired()])
    end_date = DateField('Conference End Date', validators=[DataRequired()])
    paper_submission_date = DateField('Paper Submission Date', validators=[DataRequired()])
    review_submission_date = DateField('Review Submission Date', validators=[DataRequired()])
    # editor_email = StringField('Creator Email', validators=[Email()])
    submit = SubmitField('Submit')

    # def validate_start_date(self, start_date):
    #     if start_date.data < datetime.now().date():
    #         raise ValidationError('Please set start date greater than or equal to current date.')

    def validate_end_date(self, end_date):
        if self.start_date.data > end_date.data:
            raise ValidationError('Please set end date greater than start date.')

    def validate_paper_submission_date(self, paper_submission_date):
        if not (self.start_date.data <= paper_submission_date.data <= self.end_date.data):
            raise ValidationError('Please set paper submission date >= start date and <= end date.')

    def validate_review_submission_date(self, review_submission_date):
        if not (self.paper_submission_date.data <= review_submission_date.data <= self.end_date.data):
            raise ValidationError('Please set review submission date >= paper submission date and <= end date.')


class Paper(FlaskForm):
    # author_ids = []
    paper_title = TextAreaField('Paper Title', validators=[DataRequired()])
    keywords = TextAreaField('Keywords', validators=[DataRequired()])
    abstract = TextAreaField('Abstract', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def validate_paper(self, paper_title):
        paper_title = re.sub(r'\s+', ' ', paper_title.data)
        paper = db.paper.find_one({'paper_title': paper_title})
        if paper:
            raise ValidationError('That paper title is taken. Please choose a unique paper title.')


class ReviewRequest(FlaskForm):
    accept = SubmitField('Accept')
    decline = SubmitField('Decline')


class PaperReviewerAssignment(FlaskForm):
    submit = SubmitField('Submit')


class SubmitReview(FlaskForm):
    review = TextAreaField('Add Review', validators=[DataRequired()])
    submit = SubmitField('Submit')


class SelectConference(FlaskForm):
    conferences = db.conference.find({'start_date': {'$lte': datetime.utcnow().date().isoformat()},
                                      'paper_submission_date': {'$gte': datetime.utcnow().date().isoformat()}})
    conferences_list = [conference for conference in conferences]
    choices = []
    if conferences_list:
        choices = [(conference['_id'],
                    f"{conference['name']} | Paper Submission Deadline: {conference['paper_submission_date']}") for
                   conference in conferences_list]
    conference_id = RadioField('Select Conference', choices=choices, validators=[DataRequired()])
    submit = SubmitField('Submit')
