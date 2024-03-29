from flask import render_template, flash, redirect, url_for, request, session, abort
from datetime import datetime
from bson import ObjectId
from conference_management_webapp.conference_management.forms import RegistrationForm, LoginForm, ConferenceForm, Paper, \
    PaperReviewerAssignment, ReviewRequest, SubmitReview, SelectConference, UpdateConferenceForm
from science_parse_api.api import parse_pdf
from pathlib import Path
import os, json, gc
from functools import wraps
import requests
from werkzeug.datastructures import FileStorage
import boto3
from conference_management_webapp.conference_management import app, db, bcrypt

pdf_dir = './temp/raw-pdfs'
processed_files_path = './temp/processed-pdfs'
BUCKET_NAME_RAW = 'raw-papers'
BUCKET_NAME_PROCESSED = 'processed-papers'

if not os.path.isdir(pdf_dir):
    os.makedirs(pdf_dir)

if not os.path.isdir(processed_files_path):
    os.makedirs(processed_files_path)

s3 = boto3.client(
    's3',
    aws_access_key_id='',
    aws_secret_access_key=''
)


def serialize_objectid(response):
    if response:
        if '_id' in response:
            if isinstance(response['_id'], ObjectId):
                response['_id'] = str(response['_id'])
    return response


def upload(bucket_name, filename, file):
    # For PutObject Access - reference to add policy to the bucket
    # https: // docs.aws.amazon.com / AmazonS3 / latest / userguide / example - bucket - policies.html
    if file:
        # filename = secure_filename(filename)
        print(f'uploading {filename} to s3...')
        s3.upload_fileobj(
            file,
            bucket_name,
            filename,
            ExtraArgs={
                "ACL": "public-read",
                "ContentType": file.content_type
            }
        )
        print(f'uploaded {filename} to s3')


def paper_clean_up(document_filter, document):
    if document:
        s3_url = document.get('s3_url', None)
        json_url = document.get('json_url', None)

        if s3_url:
            paper_filename = s3_url.split('/')[-1]
            s3.delete_object(Bucket=BUCKET_NAME_RAW, Key=paper_filename)
        if json_url:
            json_filename = json_url.split('/')[-1]
            s3.delete_object(Bucket=BUCKET_NAME_PROCESSED, Key=json_filename)

    if document_filter:
        db.paper.delete_one(document_filter)

    session.pop('paper_id', None)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if session.get('is_authenticated', None):
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        db.user.insert_one({
            'email': form.email.data,
            # 'first_name': form.first_name.data,
            # 'last_name': form.last_name.data,
            'name': form.name.data,
            'password': hashed_password,
            'role_type': {
                'author': [],
                'reviewer': False,
                'editor': False
            }
        })
        flash(f'Account created for {form.email.data}! Please login in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if session.get('is_authenticated', None):
        return redirect(url_for('conference'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.user.find_one({'email': form.email.data, f"role_type.{form.role.data}": {'$ne': False}})
        if user and bcrypt.check_password_hash(user.get('password'), form.password.data):
            session['role'] = form.role.data
            session['user_id'] = str(user.get('_id'))
            session['user_name'] = user.get('name')
            session['is_authenticated'] = True
            next_url = request.form.get("next")
            flash('You have been logged in!', 'success')
            return redirect(next_url) if next_url else redirect(url_for('conference'))
        else:
            flash('Login Unsuccessful. Please enter correct email address and password.', 'danger')
    return render_template('login.html', title='Login', form=form)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if session.get('is_authenticated'):
            return f(*args, **kwargs)
        else:
            flash("Please login first", 'info')
            return redirect(url_for('login', next=request.url))

    return wrap


@app.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    if session.get('is_authenticated', None):
        session.pop('is_authenticated', None)
        session.pop('user_id', None)
        session.pop('user_name', None)
        session.pop('role', None)
        gc.collect()
        flash('Successfully logged out.', 'success')
        return redirect(url_for('login'))


@app.route('/conference/new/', methods=['POST', 'GET'])
@login_required
def create_conference():
    form = ConferenceForm()
    if form.validate_on_submit():
        db.conference.insert_one({
            'name': form.name.data,
            'start_date': form.start_date.data.isoformat(),
            'end_date': form.end_date.data.isoformat(),
            'paper_submission_date': form.paper_submission_date.data.isoformat(),
            'review_submission_date': form.review_submission_date.data.isoformat()
            # 'editor_email': form.editor_email.data,
            # 'created_when': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            # 'updated_when': datetime.utcnow
        })
        flash(f'Created conference: {form.name.data}!', 'success')
        return redirect(url_for('home'))
    return render_template('create_conference.html', title='Create Conference', form=form)


@app.route('/conference/', methods=['POST', 'GET'])
@login_required
def conference():
    form = ConferenceForm()
    form_fields = [field for field in form if field.name != 'submit' and field.name != 'csrf_token']
    conference_list = db.conference.find().sort('end_date', -1)  # sort descending by end_date
    conference_list = [serialize_objectid(record) for record in conference_list]
    for record in conference_list:
        if record.get('paper_submission_date') >= datetime.utcnow().date().isoformat():
            record['submit_paper'] = True
    return render_template(f"{session.get('role')}/conference.html", form_fields=form_fields,
                           conference_list=conference_list)


@app.route('/conference/update/<id>/', methods=['GET', 'POST'])
@login_required
def update_conference(id):
    form = UpdateConferenceForm()
    id_dictionary = {'_id': ObjectId(id)}
    conference_record = db.conference.find_one(id_dictionary)
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
            db.conference.update_one(id_dictionary, updated_conference_record, upsert=False)
            return redirect(url_for('conference'))
        form.name.data = conference_record['name']
        form.start_date.data = datetime.strptime(conference_record['start_date'], '%Y-%m-%d')
        form.end_date.data = datetime.strptime(conference_record['end_date'], '%Y-%m-%d')
        form.paper_submission_date.data = datetime.strptime(conference_record['paper_submission_date'], '%Y-%m-%d')
        form.review_submission_date.data = datetime.strptime(conference_record['review_submission_date'], '%Y-%m-%d')
    return render_template('create_conference.html', title='Update Conference', form=form)


@app.route('/conference/delete/<id>/', methods=['GET', 'POST'])
@login_required
def delete_conference(id):
    record = {'_id': ObjectId(id)}
    db.conference.delete_one(record)
    return redirect(url_for('conference'))


@app.route('/conference/view/<id>/', methods=['GET'])
@login_required
def view_conference(id):
    conference_name = 'Not Found'
    conference_details = db.conference.find_one({'_id': ObjectId(id)})
    if conference_details:
        conference_name = conference_details['name']
    papers = db.paper.find({'conference_id': ObjectId(id)})
    papers_list = [paper for paper in papers]
    return render_template(f"{session.get('role')}/papers.html", papers_list=papers_list,
                           conference_name=conference_name)


def get_assigned_reviewers_list(reviewers_list):
    if reviewers_list:
        for reviewer in reviewers_list:
            reviewer_record = db.user.find_one({'_id': reviewer.get('reviewer_id')})
            if reviewer_record:
                # reviewer['name'] = reviewer_record.get('first_name', '') + ' ' + reviewer_record.get('last_name', '')
                reviewer['name'] = reviewer_record.get('name', '')
                reviewer['reviewer_email'] = reviewer_record.get('email')
    else:
        reviewers_list = []
    return reviewers_list


@app.route('/paper/view/<id>/', methods=['GET', 'POST'])
@login_required
def view_paper(id):
    conference_name = 'Not Found'
    reviewers_list = []
    paper_details = db.paper.find_one({'_id': ObjectId(id)})
    if paper_details:
        # Currently implementation for single author only
        if paper_details['author_id']:
            paper_details['author_email'] = db.user.find_one({'_id': paper_details['author_id']}).get('email')
        conference_record = db.conference.find_one({'_id': paper_details['conference_id']})
        if conference_record:
            conference_name = conference_record.get('name')
        reviewers_list = paper_details.get('reviewer_assignment')
        reviewers_list = get_assigned_reviewers_list(reviewers_list)
    return render_template(f"{session['role']}/paper_details.html", conference_name=conference_name,
                           paper_details=paper_details,
                           reviewers_list=reviewers_list)


# @app.route('/submit/paper/<conference_id>/<paper_id>', methods=['GET', 'POST'])
# def submit_paper(conference_id, paper_id, parsed_json):
#     print(conference_id)
#     print(parsed_json)
#     print(paper_id)
#     return render_template('submit_paper.html')

def get_processed_filename(json_filename):
    processed_filename = os.path.join(processed_files_path, json_filename)
    return processed_filename


def delete_processed_filename(processed_filename):
    if processed_filename and os.path.isfile(processed_filename):
        os.remove(processed_filename)


def write_and_upload_processed_json_file(processed_filename, json_content, json_filename):
    with open(processed_filename, 'w') as pf:
        json.dump(json_content, pf)

    with open(processed_filename, 'rb') as pf:
        upload(BUCKET_NAME_PROCESSED, json_filename,
               FileStorage(pf, name=json_filename, content_type='application/json'))


def read_json_from_s3(json_filename):
    result = s3.get_object(Bucket=BUCKET_NAME_PROCESSED, Key=json_filename)
    text_content = result["Body"].read().decode()
    json_content = eval(text_content)
    return json_content


def json_file_update(form_response, json_filename):
    json_content = read_json_from_s3(json_filename)
    json_fields_mapping = {'paper_title': 'title', 'abstract': 'abstractText', 'keywords': 'keywords'}

    for key, value in json_fields_mapping.items():
        json_content[value] = form_response[key]

    processed_filename = get_processed_filename(json_filename)
    write_and_upload_processed_json_file(processed_filename, json_content, json_filename)
    delete_processed_filename(processed_filename)
    print('processed file updated and deleted from local server')


@app.route('/upload/paper/', methods=['GET', 'POST'])
@login_required
def upload_new_paper():
    form = SelectConference()
    # fetch conferences where the current date is >= conference start date and < submission deadline
    # radio button to select the conference name and submit
    if form.validate_on_submit():
        conference_id = form.conference_id.data
        return redirect(url_for('upload_paper', conference_id=conference_id))
    return render_template('select_conference.html', form=form)


@app.route('/upload/paper/<conference_id>/', methods=['GET', 'POST'])
@login_required
def upload_paper(conference_id):
    current_date = datetime.utcnow().date().isoformat()
    conference_record = db.conference.find_one({'_id': ObjectId(conference_id), 'start_date': {'$lte': current_date},
                                                'paper_submission_date': {'$gte': current_date}})
    if not conference_record:
        abort(404, description="No such conference found.")
    parsed_json = ''
    temp_filename = ''
    processed_filename = ''
    error = False
    form = Paper()
    document_filter = dict()
    document_upsert = dict()
    try:
        if request.method == 'GET':
            return render_template('upload_paper.html', form=form)
        if request.method == 'POST':

            if 'upload' in request.form:
                print('file received')

                document = db.paper.insert_one({'conference_id': ObjectId(conference_id), 'paper_status': 'Uploaded',
                                                'submission_datetime': datetime.utcnow()})
                document_filter = {'_id': document.inserted_id}
                session['paper_id'] = str(document.inserted_id)
                pdf = request.files['file']
                if pdf:
                    serialized_id = str(document.inserted_id)
                    paper_filename = serialized_id + '-Paper.pdf'
                    json_filename = serialized_id + '-ParsedPaper.json'
                    temp_filename = os.path.join(pdf_dir, paper_filename)
                    processed_filename = os.path.join(processed_files_path, json_filename)
                    pdf.save(temp_filename)
                    pdf.filename = temp_filename
                    temp_file_path = Path(temp_filename)
                    host = 'http://127.0.0.1'
                    port = '8080'
                    parsed_json = parse_pdf(host, temp_file_path, port=port)
                    with open(processed_filename, 'w') as pf:
                        json.dump(parsed_json, pf)

                    with open(processed_filename, 'rb') as pf:
                        upload(BUCKET_NAME_PROCESSED, json_filename,
                               FileStorage(pf, name=json_filename, content_type='application/json'))

                    with open(temp_filename, 'rb') as pf:
                        upload(BUCKET_NAME_RAW, paper_filename,
                               FileStorage(pf, name=paper_filename, content_type='application/pdf'))

                    # upload(BUCKET_NAME_RAW, paper_filename, pdf)
                    document_upsert['s3_url'] = f'https://raw-papers.s3-us-west-1.amazonaws.com/{paper_filename}'
                    document_upsert['json_url'] = f'https://processed-papers.s3-us-west-1.amazonaws.com/{json_filename}'
                    document_upsert['paper_title'] = parsed_json.get('title')
                    document_upsert['abstract'] = parsed_json.get('abstractText')
                    document_upsert['author_id'] = ObjectId(session['user_id'])
                    document_upsert['references'] = len(parsed_json.get('references', []))
                    document_upsert['referenceMentions'] = 55
                    db.user.update_one({'_id': ObjectId(session['user_id'])},
                                       {'$addToSet': {'role_type.author': {'paper_id': document.inserted_id}}},
                                       upsert=False)
                    db.paper.update_one(document_filter, {'$set': document_upsert}, upsert=False)

    except Exception as e:
        print(e)
        error = True
        paper_clean_up(document_filter, document_upsert)
    finally:
        delete_processed_filename(processed_filename)
        delete_processed_filename(temp_filename)
    if not error:
        return redirect(url_for('submit_paper', conference_id=conference_id))
    else:
        return render_template('upload_paper.html', form=form)


@app.route('/submit/paper/<conference_id>', methods=['GET', 'POST'])
@login_required
def submit_paper(conference_id):
    try:
        form = Paper()
        document_filter = {'_id': ObjectId(session['paper_id'])}
        paper_record = db.paper.find_one(document_filter)
        json_url = paper_record.get('json_url')
        if json_url:
            json_filename = json_url.split('/')[-1]
            if request.method == 'GET':
                json_content = read_json_from_s3(json_filename)
                form.abstract.data = json_content.get('abstractText')
                form.paper_title.data = json_content.get('title')
            if form.validate_on_submit():
                print('success')
                form_response = dict()
                form_response['paper_title'] = form.paper_title.data
                form_response['keywords'] = form.keywords.data
                form_response['abstract'] = form.abstract.data
                # read json from s3 and compare with form values, update and upload if necessary
                json_file_update(form_response, json_filename=json_filename)
                url = 'http://localhost:8084/getAcceptancePrediction'
                response = requests.post(url, json={'abstract': form.abstract.data, 'title': form.paper_title.data,
                                                    'references': paper_record.get('references'),
                                                    'referenceMentions': paper_record.get('referenceMentions')}).json()
                form_response['Acceptance_Probability'] = response['Acceptance_Probability']
                form_response['accepted'] = response['accepted']
                db.paper.update_one(document_filter, {'$set': form_response},
                                    upsert=False)
                flash(f'Submitted Paper: {form.paper_title.data}!', 'success')

                return redirect(url_for('view_paper', id=session['paper_id']))
    except Exception as e:
        print(e)
    return render_template('submit_paper.html', form=form)


@app.route('/view/papers/<user_id>', methods=['GET', 'POST'])
@login_required
def view_papers_by_user_id(user_id):
    papers = db.paper.find({'author_id': ObjectId(user_id)})
    papers_list = []
    for paper in papers:
        conference_name = db.conference.find_one({'_id': paper.get('conference_id')}).get('name')
        if conference_name:
            paper['conference_name'] = conference_name
            papers_list.append(paper)
    # if papers_list:
    return render_template('author/papers_by_user_id.html', papers_list=papers_list)
    # else:
    #     return render_template('author/papers_by_user_id.html', papers_list=[])


def get_recommended_reviewers(abstract):
    url = 'http://localhost:8083/reviewerRecommendation'
    response = requests.post(url, json={'abstract': abstract}).json()
    # if response.status_code != 200:
    #     abort(500, description='Reviewer Recommendation API Error')
    reviewers = response.get('authors', [])
    recommended_reviewers = []
    if reviewers:
        for reviewer_name in reviewers:
            reviewer = db.user.find_one({'name': reviewer_name, 'role_type.reviewer': {'$ne': False}}, {'email': 1})
            if reviewer:
                recommended_reviewers.append({'name': reviewer_name, 'reviewer_email': reviewer['email']})
    return recommended_reviewers


@app.route('/submit/reviewer/<paper_id>/', methods=['GET', 'POST'])
@login_required
def paper_reviewer_assignment(paper_id):
    if session['role'] != 'editor':
        abort(403)
    form = PaperReviewerAssignment()
    paper_record = db.paper.find_one({'_id': ObjectId(paper_id)})
    reviewers_list = []
    if not paper_record:
        abort(404, description='No such paper found')

    if 'reviewer_assignment' in paper_record and paper_record['reviewer_assignment']:
        reviewers_list = get_assigned_reviewers_list(paper_record['reviewer_assignment'])
    recommended_reviewers_list = []
    recommended_reviewers_list = get_recommended_reviewers(paper_record.get('abstract', ''))

    if request.method == 'GET':
        # display paper name in place of paper_id, authors and abstract to the editor
        return render_template('dynamic_input.html', paper_record=paper_record, form=form,
                               reviewers_list=reviewers_list, recommended_reviewers_list=recommended_reviewers_list)
    else:
        reviewer_emails = request.form.getlist('input_text[]')
        reviewer_ids = []
        for reviewer_email in reviewer_emails:
            # add drop down with reviewer email address, no email address outside the list allowed
            # also email address not equal to authors' email
            # reviewers can be assigned any no. of papers
            # reviewers can only accept X paper for each conference
            # reviewer_record = db.user.find_one({'email': reviewer_email})
            reviewer_record = db.user.find_one({'email': reviewer_email, 'role_type.reviewer': {'$ne': False}})
            if reviewer_record and reviewer_record.get('_id'):
                # check if the paper id already exists as review requested or accepted, if true then don't update
                # check if the paper id already exists as declined, if true then update
                reviewer_id = reviewer_record.get('_id')
                reviewer_record = db.user.find_one(
                    {'_id': reviewer_id, 'role_type.reviewer.paper_id': ObjectId(paper_id)})
                if reviewer_record:
                    filtered_review_status = [record['review_status'] for record in
                                              reviewer_record['role_type']['reviewer'] if
                                              record['paper_id'] == ObjectId(paper_id)]

                    if filtered_review_status:
                        if 'Declined' in filtered_review_status:
                            db.user.update_one({'_id': reviewer_id, 'role_type.reviewer.paper_id': ObjectId(paper_id),
                                                'role_type.reviewer.review_status': 'Declined'},
                                               {'$set': {'role_type.reviewer.$.review_status': 'Review Requested'}},
                                               upsert=False)
                        else:
                            continue
                else:
                    db.user.update_one({'_id': reviewer_id},
                                       {'$addToSet': {'role_type.reviewer': {'paper_id': ObjectId(paper_id),
                                                                             'review_status': 'Review Requested'}}},
                                       upsert=False)
                reviewer_ids.append({'reviewer_id': reviewer_id})
        if reviewer_ids:
            db.paper.update_one({'_id': ObjectId(paper_id)},
                                {'$addToSet': {'reviewer_assignment': {'$each': reviewer_ids}},
                                 '$set': {'paper_status': 'Review Requested'}}, upsert=False)
        return redirect(url_for('view_paper', id=paper_id))


@app.route('/view/review-request/<reviewer_id>/', methods=['GET'])
@login_required
def view_review_request(reviewer_id):
    title = 'View New/Pending Review Requests'
    reviewer_specific_review_requests = []
    if session['user_id'] != reviewer_id or session['role'] != 'reviewer':
        abort(403, description="Access Forbidden")
        # return render_template('view_review_request.html', review_requests=reviewer_specific_review_requests,
        #                        request_status=None, title=title)
    reviewer_record = db.user.find_one({'_id': ObjectId(reviewer_id)})
    if reviewer_record:
        if 'role_type' in reviewer_record:
            if 'reviewer' in reviewer_record['role_type'] and reviewer_record['role_type']['reviewer']:
                review_requests = reviewer_record['role_type']['reviewer']

                for review_request in review_requests:
                    pending_requests = dict()
                    if review_request['review_status'] == 'Review Requested':
                        pending_requests['reviewer_id'] = reviewer_id
                        paper_record = db.paper.find_one({'_id': review_request['paper_id']})
                        pending_requests['paper_id'] = str(review_request['paper_id'])
                        pending_requests['paper_title'] = paper_record.get('paper_title')
                        pending_requests['paper_status'] = paper_record.get('paper_status')
                        conference_id = paper_record.get('conference_id')
                        conference_record = db.conference.find_one({'_id': conference_id})
                        pending_requests['conference_name'] = conference_record.get('name')
                        pending_requests['review_submission_date'] = conference_record.get('review_submission_date')
                        reviewer_specific_review_requests.append(pending_requests)
    return render_template('view_review_request.html', review_requests=reviewer_specific_review_requests,
                           request_status=None, title=title)


@app.route('/view/review-request/<request_status>/<reviewer_id>/', methods=['GET'])
@login_required
def view_review_request_with_status(request_status, reviewer_id):
    reviewer_specific_review_requests = []
    title = 'View Review Requests'
    if request_status.lower() == 'accepted':
        title = 'View Accepted Review Requests'
    elif request_status.lower() == 'declined':
        title = 'View Declined Review Requests'

    if session['user_id'] != reviewer_id or session['role'] != 'reviewer':
        abort(403, description="Access Forbidden")
        # return render_template('view_review_request.html', review_requests=reviewer_specific_review_requests,
        #                        request_status=request_status.lower(), title=title)

    current_date = datetime.utcnow().date().isoformat()
    reviewer_record = db.user.find_one({'_id': ObjectId(reviewer_id)})
    if reviewer_record:
        if 'role_type' in reviewer_record:
            if 'reviewer' in reviewer_record['role_type'] and reviewer_record['role_type']['reviewer']:
                review_requests = reviewer_record['role_type']['reviewer']

                for review_request in review_requests:
                    pending_requests = dict()
                    if review_request['review_status'].lower() == request_status.lower():
                        pending_requests['reviewer_id'] = reviewer_id
                        paper_record = db.paper.find_one({'_id': review_request['paper_id']})
                        pending_requests['paper_id'] = str(review_request['paper_id'])
                        pending_requests['paper_title'] = paper_record.get('paper_title')
                        conference_id = paper_record.get('conference_id')
                        conference_record = db.conference.find_one({'_id': conference_id})
                        pending_requests['conference_name'] = conference_record.get('name')
                        pending_requests['review_submission_date'] = conference_record.get('review_submission_date')
                        pending_requests['add_review'] = conference_record.get('start_date') <= current_date <= \
                                                         conference_record.get('review_submission_date')
                        reviewer_specific_review_requests.append(pending_requests)
    return render_template('view_review_request.html', review_requests=reviewer_specific_review_requests,
                           request_status=request_status.lower(), title=title)


@app.route('/submit/review-request/<reviewer_id>/paper/<paper_id>/', methods=['GET', 'POST'])
@login_required
def review_request(reviewer_id, paper_id):
    if session['user_id'] != reviewer_id or session['role'] != 'reviewer':
        abort(403, description="Access Forbidden")
    form = ReviewRequest()
    # only filter papers that are under status - Review Requested (not the ones - Accepted or Declined)
    reviewer_filter = {'_id': ObjectId(reviewer_id), 'role_type.reviewer.paper_id': ObjectId(paper_id),
                       'role_type.reviewer.review_status': 'Review Requested'}

    paper_filter = {'_id': ObjectId(paper_id)}
    paper_record = db.paper.find_one(paper_filter)
    reviewer = db.user.find_one(reviewer_filter)
    if not reviewer:
        abort(403, description="Access Forbidden")

    if form.validate_on_submit():
        if 'accept' in request.form:
            db.user.update_one(reviewer_filter, {'$set': {'role_type.reviewer.$.review_status': 'Accepted'}},
                               upsert=False)
            flash('Review Request: Accepted', 'success')
            return redirect(url_for('submit_review', reviewer_id=reviewer_id, paper_id=paper_id))

        if 'decline' in request.form:
            db.paper.update_one(paper_filter,
                                {'$pull': {'reviewer_assignment': {'reviewer_id': reviewer_filter['_id']}}},
                                upsert=False)
            db.user.update_one(reviewer_filter, {'$set': {'role_type.reviewer.$.review_status': 'Declined'}},
                               upsert=False)
            flash('Review Request: Declined', 'danger')
            return redirect(
                url_for('view_review_request_with_status', request_status='declined', reviewer_id=reviewer_id))
    return render_template('submit_review_request.html', paper_record=paper_record, form=form)


def get_aspect_scores(reviewer_id, review):
    aspect_scores = {}
    try:
        url = 'http://localhost:8081/getAspectScores'
        response = requests.post(url, json={'id': reviewer_id, 'review': review}).json()
        # get impact and clarity
        # if response.status_code != 200:
        #     print('aspect_scores api error:', response.status_code)
        #     abort(500)
        if 'Impact' in response:
            aspect_scores['impact'] = response['Impact']
        if 'Clarity' in response:
            aspect_scores['clarity'] = response.get('Clarity')
        if 'Technical Soundness' in response:
            aspect_scores['technical_soundness'] = response['Technical Soundness']
        if 'Originality' in response:
            aspect_scores['originality'] = response['Originality']
    except Exception as e:
        print('Error occurred when calling aspect scores api:', e)
    finally:
        return aspect_scores


@app.route('/submit/review/<reviewer_id>/paper/<paper_id>/', methods=['GET', 'POST'])
@login_required
def submit_review(reviewer_id, paper_id):
    form = SubmitReview()
    paper_filter = {'_id': ObjectId(paper_id), 'reviewer_assignment.reviewer_id': ObjectId(reviewer_id)}
    paper_record = db.paper.find_one(paper_filter)
    reviews = []
    if session['user_id'] != reviewer_id or session['role'] != 'reviewer':
        abort(403, description="Access Forbidden")
        # return render_template('submit_review.html', form=form, paper_record=paper_record, reviews=reviews)
    if paper_record:
        conference_id = paper_record.get('conference_id')
        current_date = datetime.utcnow().date().isoformat()
        conference_record = db.conference.find_one({'_id': conference_id, 'start_date': {'$lte': current_date},
                                                    'review_submission_date': {'$gte': current_date}})
        if not conference_record:
            paper_record = []
            return render_template('submit_review.html', form=form, paper_record=paper_record, reviews=reviews)

        reviewer_record = [reviewer_record for reviewer_record in paper_record['reviewer_assignment'] if
                           reviewer_record['reviewer_id'] == ObjectId(reviewer_id)]
        if reviewer_record:
            reviewer_record = reviewer_record[0]
            if reviewer_record.get('reviews'):
                reviews = reviewer_record.get('reviews')

    if form.validate_on_submit():
        # make api call
        aspect_scores = get_aspect_scores(reviewer_id, form.review.data)
        created_when = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db.paper.update_one(paper_filter, {
            '$addToSet': {'reviewer_assignment.$.reviews': {'review': form.review.data,
                                                            'aspect_scores': aspect_scores,
                                                            'created_when': created_when}}}, upsert=False)
        reviews.append({'review': form.review.data, 'created_when': created_when})
        flash('Submitted Review!', 'success')
        form.review.data = ''
    return render_template('submit_review.html', form=form, paper_record=paper_record, reviews=reviews)


@app.route('/view/review/<reviewer_id>/paper/<paper_id>/', methods=['GET', 'POST'])
@login_required
def view_review(reviewer_id, paper_id):
    # visible to paper author and editors only
    paper_filter = {'_id': ObjectId(paper_id), 'reviewer_assignment.reviewer_id': ObjectId(reviewer_id)}
    reviews = []
    review_record = db.paper.find_one(paper_filter, {'reviewer_assignment': 1, 'paper_title': 1})
    if review_record:
        paper_title = review_record.get('paper_title')
        if review_record.get('reviewer_assignment'):
            reviews = [reviewer_dictionary.get('reviews') for reviewer_dictionary in
                       review_record.get('reviewer_assignment') if
                       reviewer_dictionary['reviewer_id'] == ObjectId(reviewer_id)
                       and reviewer_dictionary.get('reviews')]
            if reviews:
                reviews = reviews[0]
    return render_template(f"{session['role']}/view_review.html", reviews=reviews, paper_title=paper_title)


@app.route('/view/papers/<paper_status>/', methods=['GET'])
@login_required
def view_papers_by_status(paper_status):
    title = 'View New/Under-Review Papers'
    filtered_fields = {'conference_id': 1, 'paper_title': 1, 'paper_status': 1, 's3_url': 1}
    if paper_status.lower() == 'accepted':
        title = 'View Accepted Papers'
        papers = db.paper.find({'paper_status': 'Accepted'}, filtered_fields).sort('submission_datetime', -1)
    elif paper_status.lower() == 'rejected':
        title = 'View Rejected Papers'
        papers = db.paper.find({'paper_status': 'Rejected'}, filtered_fields).sort('submission_datetime', -1)
    else:
        papers = db.paper.find({'paper_status': {'$nin': ['Accepted', 'Rejected']}}, filtered_fields).sort(
            'submission_datetime', -1)
    conferences = db.conference.find({}, {'name': 1})
    conferences_dictionary = {conference['_id']: conference['name'] for conference in conferences}
    papers_list = []
    for paper in papers:
        conference_id = paper.get('conference_id')
        if conference_id and conference_id in conferences_dictionary:
            paper['conference_name'] = conferences_dictionary[conference_id]
            papers_list.append(paper)
    return render_template(f"{session['role']}/view_papers_by_status.html", title=title, papers_list=papers_list)


@app.route('/paper/publish-request/<paper_id>/', methods=['POST'])
def paper_publish_request(paper_id):
    paper_status = ''
    if session['role'] != 'editor':
        abort(403, description='Endpoint forbidden')
    if 'Accepted' in request.form:
        paper_status = 'Accepted'
    elif 'Rejected' in request.form:
        paper_status = 'Rejected'
    if paper_status:
        db.paper.update_one({'_id': ObjectId(paper_id)}, {'$set': {'paper_status': paper_status}}, upsert=False)
    return redirect(url_for('view_paper', id=paper_id))
