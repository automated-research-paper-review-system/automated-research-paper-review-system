from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, TextAreaField
from wtforms.fields.html5 import DateField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class ConferenceForm(FlaskForm):
    name = StringField('Conference Name', validators=[DataRequired()])
    start_date = DateField('Conference Start Date', validators=[DataRequired()])
    end_date = DateField('Conference End Date', validators=[DataRequired()])
    paper_submission_date = DateField('Paper Submission Date', validators=[DataRequired()])
    review_submission_date = DateField('Review Submission Date', validators=[DataRequired()])
    # editor_email = StringField('Creator Email', validators=[Email()])
    submit = SubmitField('Submit')


# Conference list -> choose conference -> upload paper for that conference id

class Paper(FlaskForm):
    # view_all_conference
    # conference_id = StringField('Conference ID', validators=[DataRequired()])
    # author_ids = []
    paper_title = TextAreaField('Paper Title', validators=[DataRequired()])
    keywords = TextAreaField('Keywords', validators=[DataRequired()])
    abstract = TextAreaField('Abstract', validators=[DataRequired()])
    # paper = FileField('Paper Document (PDF only)', validators=[FileRequired(), FileAllowed(['pdf'], 'PDF only!')])
    submit = SubmitField('Submit')


class ReviewRequest(FlaskForm):
    accept = SubmitField('Accept')
    decline = SubmitField('Decline')


class PaperReviewerAssignment(FlaskForm):
    submit = SubmitField('Submit')


class SubmitReview(FlaskForm):
    review = TextAreaField('Add Review', validators=[DataRequired()])
    submit = SubmitField('Submit')
