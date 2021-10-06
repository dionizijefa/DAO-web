from flask import Flask, jsonify, request
from flask_cors import CORS
from model import DAOWeb

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)

dao = DAOWeb()


@app.route('/predict', methods=['POST'])
def predict():
    input_smiles = request.get_json()['smilesInput']
    probability, predicted_class, approved_p, withdrawn_p = dao.predict(input_smiles)

    return jsonify({'predictedProbability': probability,
                    'predictedClass': predicted_class,
                    'approvedP': approved_p,
                    'withdrawnP': withdrawn_p})


@app.route('/explain', methods=['POST'])
def explain():
    input_smiles = request.get_json()['smilesInput']
    graph, feature_importance = dao.explain(input_smiles)

    return jsonify({
        'graph': graph,
        'featureImportance': feature_importance
    })


if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)
