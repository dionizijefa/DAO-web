from flask import Flask, jsonify, request
from flask_cors import CORS
from model import DAOWeb

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['POST'])
def predict():
    input_smiles = request.get_json()['smilesInput']
    dao = DAOWeb()
    probability, predicted_class, approved_p, withdrawn_p = dao.predict(input_smiles)

    return jsonify({'predictedProbability': probability})

if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)


