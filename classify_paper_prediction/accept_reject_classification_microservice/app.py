import pandas as pd
from flask import Flask, jsonify, request
app = Flask(__name__)
from AcceptancePrediction import *

@app.route('/getAcceptancePrediction', methods=['POST'])
def get_accept_reject():
    data = request.get_json()
    all_response = {'abstractText': data['abstract'], 'title': data['title'], 'references': data['references'], 'referenceMentions': data['referenceMentions']}
    acceptance_prediction = AcceptancePrediction()
    df = pd.DataFrame([all_response])
    result = acceptance_prediction.predict_acceptance(df)
    # return jsonify(all_response), 200
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0',  port='8084')