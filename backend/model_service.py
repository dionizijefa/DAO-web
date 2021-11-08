from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from withdrawn.model import DAOWeb
from jinja2 import TemplateNotFound

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)

@app.route('/predict', methods=['POST'])
def predict():
    dao = DAOWeb()
    input_smiles = request.get_json()['smilesInput']
    probability, predicted_class, approved_p, withdrawn_p, molecule_vis, qed_prop, similarities = dao.predict(input_smiles)

    return jsonify({'predictedProbability': probability,
                    'predictedClass': predicted_class,
                    'approvedP': approved_p,
                    'withdrawnP': withdrawn_p,
                    'moleculeVis': molecule_vis,
                    'qedProp': qed_prop,
                    'similarities': similarities})


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
    app.run(
        host=HOST, debug=True, port=PORT
    )
