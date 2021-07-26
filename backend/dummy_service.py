from flask import Flask, jsonify, request
from rdkit.Chem import MolFromSmiles
from flask_cors import CORS
from inference_model import TransformerNet


# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)


@app.route('/predict', methods=['POST'])
def predict():
    input_smiles = request.get_json()['smilesInput']
    mol = MolFromSmiles(input_smiles)
    atoms = mol.GetNumAtoms()

    return jsonify({'predictedProbability': atoms})


if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)
