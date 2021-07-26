from flask import Flask, jsonify, request
from flask_cors import CORS
from inference_model import TransformerNet
from inference_model import process_molecule
import numpy as np

# declare constants
HOST = '0.0.0.0'
PORT = 8081

app = Flask(__name__)
CORS(app)


class Inference:
    def __init__(self, ckpt_path):
        self.model = TransformerNet.load_from_checkpoint(ckpt_path)

    def forward(self, node, adj, dist, mask):
        out = self.model.forward(node, adj, dist, mask, None)
        out = out.squeeze(-1).detach().cpu().numpy()
        return out


@app.route('/predict', methods=['POST'])
def predict():
    input_smiles = request.get_json()['smilesInput']
    node, adj, dist, mask = process_molecule(input_smiles)

    model = Inference('epoch=6-step=405.ckpt')
    logit = model.forward(node, adj, dist, mask)
    odds = np.exp(logit)
    probability = odds / (1+odds)

    return jsonify({'predictedProbability': probability})


if __name__ == '__main__':
    app.run(host=HOST, debug=True, port=PORT)
