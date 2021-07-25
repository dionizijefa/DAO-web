from flask import Flask, jsonify, request
from rdkit.Chem import MolFromSmiles

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    input_smiles = request.get_json()

    mol = MolFromSmiles(input_smiles)
    atoms = mol.GetNumAtoms()

    return jsonify({'predicted_probability': atoms})

if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)


