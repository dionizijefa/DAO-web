from flask import Flask, jsonify, request
from flask_cors import CORS
from withdrawn.model import DAOWeb

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['POST'])
def predict():
    dao = DAOWeb()
    input_smiles = request.get_json()['smilesInput']
    probability, predicted_class, approved_p, withdrawn_p, molecule_vis = dao.predict(input_smiles)

    return jsonify({'predictedProbability': probability,
                    'predictedClass': predicted_class,
                    'approvedP': approved_p,
                    'withdrawnP': withdrawn_p,
                   'moleculeVis': molecule_vis})


@app.route('/explain', methods=['POST'])
def explain():
    dao = DAOWeb()
    input_smiles = request.get_json()['smilesInput']
    graph, feature_importance = dao.explain(input_smiles)

    return jsonify({
        'graph': graph,
        'featureImportance': feature_importance
    })

@app.route('/complement', methods=['POST'])
def complement():
    dao = DAOWeb()
    input_smiles = request.get_json()[0]['smilesInput']
    predicted_probability = request.get_json()[1]
    prediction, tasks, force = dao.complementary_model(input_smiles, predicted_probability)

    return jsonify({
        'prediction': prediction,
        'tasks': tasks,
        'force': force,
    })


if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)
