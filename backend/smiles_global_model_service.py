from flask import Flask, jsonify, request
from rdkit.Chem import MolFromSmiles
from flask_cors import CORS
from inference_model import TransformerNet
from inference_model import process_molecule

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)


class Inference:
    def __init__(self, ckpt_path):
        self.model = TransformerNet.load_from_checkpoint(ckpt_path)

    def forward(self):
        out = self.model.forward()
        out = out.squeeze(-1).detach().cpu().numpy()


@app.route('/predict', methods=['POST'])
def predict():
    input_smiles = request.get_json()['smilesInput']
    node, adj, dist, mask = process_molecule(input_smiles)
    print(node)

    return jsonify({'predictedProbability': atoms})


if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)
