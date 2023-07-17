from flask import Flask, jsonify, request, render_template, abort
from flask_cors import CORS
from model import Model

# declare constants
HOST = '0.0.0.0'
PORT = 8081


app = Flask(__name__)
CORS(app)

# možda najbolje pozvati model ovdje da je stalno učitan u memoriju?
model = Model()

@app.route('/predict', methods=['POST'])
def predict():
    input_smiles = request.get_json()['smilesInput']
    output = model.predict(input_smiles)

    return jsonify(
        {
            'predictedClass': output,
        }
    )


if __name__ == '__main__':
    app.run(
        host=HOST, debug=True, port=PORT
    )
