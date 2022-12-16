from flask import Flask, request, jsonify
from flask.json import JSONEncoder

from util import teamAPI, batsmanAPI, bowlerAPI


import numpy as np


class NpEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


app = Flask(__name__)
app.json_encoder = NpEncoder


@app.route("/")
def home():
    return "hello"


@app.route("/team_record", methods=['get'])
def team_record():
    team = request.args.get('team')
    return jsonify(teamAPI(team))


@app.route("/batsman_record", methods=['get'])
def batsman_record():
    batsman = request.args.get('batsman')
    return jsonify(batsmanAPI(batsman))


@app.route("/bowler_record", methods=['get'])
def bowler_record():
    bowler = request.args.get('bowler')
    return jsonify(bowlerAPI(bowler))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=4444)
