from flask import Flask, jsonify, request
from preprocessor import *
from ScorePrediction import *
# from flask_cors import CORS
# import json, os
# from pymongo import MongoClient
# from bson.json_util import dumps
# import random
# Supporting Cross Origin requests for all APIs
# cors = CORS(app)

app = Flask(__name__)


# @app.route('/getAspectScores/<int:id>', methods=['GET'])
@app.route('/getAspectScores', methods=['POST'])
def get_aspect_score():
    data = request.get_json()
    all_response = {'id': data['id'], 'review': data['review'], 'reviewer_id': data['id']}
    score_prediction = ScorePrediction()
    all_response = score_prediction.predictions(all_response)
    return jsonify(all_response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',  port='8081')
