from flask import Flask, jsonify, request
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
    all_response = {'id': data['id'], 'review': data['review']}
    score_prediction = ScorePrediction()
    all_response['clarity'] = score_prediction.predict_clarity(all_response['review'])
    return jsonify(all_response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0',  port='8081')
