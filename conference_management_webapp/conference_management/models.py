conference = [
    {
        'id': 1,
        'name': 'conf1',
        'start_date': '',
        'end_date': '',
        'paper_submission_date': '',
        'review_submission_date': '',
        'created_when': '',
        'updated_when': '',
        'editor_email': ''
    }
]

user = [
    {
        'id': 1,
        'first_name': '',
        'last_name': '',
        'email': '',
        'password': '',
        # 'role_type': [
        #     {
        #         'author': [
        #             {
        #                 'paper_id': ''
        #             }
        #         ]
        #     },
        #     {
        #         'reviewer': [
        #             {
        #                 'paper_id': '',
        #                 'review_status': ''
        #             }
        #         ]
        #     },
        #     {
        #         'editor': {}
        #     }
        # ],
        'role_type': {
            'author': [
                {
                    'paper_id': ''
                }
            ],
            'reviewer': [
                {
                    'paper_id': '',
                    'review_status': ''
                }
            ],
            'editor': {}
        },
        'created_when': '',
        'updated_when': ''
    }
]

paper = [
    {
        'id': 1,
        'conference_id': 1,
        'author_id': [],
        'paper_title': '',
        'abstract': '',
        'keywords': [],
        's3_url': '',
        'json_url': '',
        'paper_status': '',
        'reviewer_assignment': [
            {
                'reviewer_id': '',
                'reviews': [
                    {
                        'user_id': 1,
                        'role_type': '',
                        'review': '',
                        'aspect_scores': {
                            'clarity': '',
                            'impact': ''
                        },
                        'created_when': ''
                    }
                ]
            },
            {
                'reviewer_id': '',
                'reviews': [
                    {
                        'user_id': 2,
                        'role_type': '',
                        'review': '',
                        'aspect_scores': {
                            'clarity': '',
                            'impact': ''
                        },
                        'created_when': ''
                    }
                ]
            }
        ],
        'submission_datetime': ''
    }
]

# update review status for reviewer
# db.user.update_one({'_id': ObjectId('607b49730155fa693c01f4f1'), 'role_type.reviewer.paper_id': ObjectId('60721be9d53edfbacee32e2d'), 'role_type.reviewer.review_status': 'requested'}, {'$set': {'role_type.reviewer.$.review_status': 'accepted'}})


# db.paper.update_one({'_id': ObjectId('60721be9d53edfbacee32e2d')}, {'$addToSet': {'reviewer_assignment': {'$each': [{'reviewer_email': 'karnavee@gmail.com'}]}}}, upsert=False)

# [{'_id': ObjectId('1'),'first_name': 'Sathya Sri', 'last_name': 'Pasham', 'email': 'sathya@gmail.com', 'password': 'password', 'role_type': {'author': [], 'reviewer': [], 'editor': False}},
# {'_id':ObjectId('2'), 'first_name': 'Shivani', 'last_name': 'Suryawanshi', 'email': 'shivani@gmail.com', 'password': 'password', 'role_type': {'author': [], 'reviewer': [], 'editor': True}},
# {'_id': ObjectId('3'), 'first_name': 'Kapil', 'last_name': 'Mulchandani', 'email': 'kapil@gmail.com', 'password': 'password', 'role_type': {'author': [], 'reviewer': [], 'editor': False}}]

# [{'first_name': 'Sathya Sri', 'last_name': 'Pasham', 'email': 'sathya@gmail.com', 'password': 'password', 'role_type': {'author': [], 'reviewer': [], 'editor': False}},
# {'first_name': 'Shivani', 'last_name': 'Suryawanshi', 'email': 'shivani@gmail.com', 'password': 'password', 'role_type': {'author': [], 'reviewer': [], 'editor': True}},
# {'first_name': 'Kapil', 'last_name': 'Mulchandani', 'email': 'kapil@gmail.com', 'password': 'password', 'role_type': {'author': [], 'reviewer': [], 'editor': False}}]

# {'first_name': 'Karnavee', 'last_name': 'Kamdar', 'email': 'karnavee.kamdar@sjsu.edu', 'password': 'password', 'role_type': {'author': [], 'reviewer': [], 'editor': False}}

# db.paper.update_one({'_id': ObjectId('60847527242c50912306639a'), 'reviewer_assignment.reviewer_id': 2}, {'$addToSet': {'reviewer_assignment.$.reviews': {'review': 'first review', 'aspect_score': {'impact': 5, 'clarity': 4}}}})

# db.user.create_index("email")
# db.conference.create_index('name')

# to remove an object with specified reviewer_id
# db.paper.update_one({'_id': ObjectId('60847527242c50912306639a')},{'$pull': {'reviewer_assignment':
# {'reviewer_id': ObjectId('60848855229a4fedb06f954f')}}})

# db.user.update_one(reviewer_filter, {'$pull': {
#         'role_type.reviewer': {'paper_id': ObjectId('60847527242c50912306639a'), 'review_status': 'Review Requested'}}})