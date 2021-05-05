import pandas as pd
from flask import Flask, jsonify, request
from ReviewerRecommender import *
app = Flask(__name__)

@app.route('/reviewerRecommendation', methods=['POST'])
def get_recommenders():
    data = request.get_json()
    all_response = {'abstractText': data['abstract']}
    df = pd.DataFrame([all_response])
    rRecommender = ReviewerRecommender()
    result = rRecommender.reviewer_recommender(df)
    all_response['authors'] = result
    return jsonify(all_response), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8083')
    # app.run(debug=True)

