import gc
from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from withdrawn.model import DAOWeb
from jinja2 import TemplateNotFound
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1 per minute", "10 per hour"],
)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    try:
        return render_template('index.html')
    except TemplateNotFound:
        abort(404)

@app.route('/predict', methods=['POST'])
@limiter.limit(["1 per minute", "10 per hour"],
               error_message='Service is limited to 10 predictions per hour and 1 per minute'
               )
def predict():
    dao = DAOWeb()
    input_smiles = request.get_json()['smilesInput']
    probability, predicted_class, approved_p, withdrawn_p, molecule_vis, qed_prop, similarities = dao.predict(input_smiles)
    gc.collect()

    return jsonify({'predictedProbability': probability,
                    'predictedClass': predicted_class,
                    'approvedP': approved_p,
                    'withdrawnP': withdrawn_p,
                    'moleculeVis': molecule_vis,
                    'qedProp': qed_prop,
                    'similarities': similarities})


@app.route('/explain', methods=['POST'])
@limiter.limit(["1 per minute", "10 per hour"],
               error_message='Service is limited to 10 predictions per hour and 1 per minute',
               per_method="True")
def explain():
    dao = DAOWeb()
    input_smiles = request.get_json()['smilesInput']
    graph, feature_importance = dao.explain(input_smiles)
    gc.collect()

    return jsonify({
        'graph': graph,
        'featureImportance': feature_importance
    })


@app.route('/complement', methods=['POST'])
@limiter.limit(["1 per minute", "10 per hour"],
               error_message='Route is limited to 10 predictions per hour and 1 per minute')
def complement():
    dao = DAOWeb()
    input_smiles = request.get_json()[0]['smilesInput']
    predicted_probability = request.get_json()[1]
    prediction, tasks, force = dao.complementary_model(input_smiles, predicted_probability)
    gc.collect()

    return jsonify({
        'prediction': prediction,
        'tasks': tasks,
        'force': force,
    })


if __name__ == '__main__':
    app.run(
        host=HOST, debug=True, port=PORT
    )
