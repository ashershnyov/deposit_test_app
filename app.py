from flask import Flask, make_response, request
from flask.json import jsonify
from schema import Schema, And, Use, SchemaError
import datetime
from calendar import monthrange


DATE_FORMAT = "%d.%m.%Y"

JSON_STRUCT = Schema({
    "date": And(Use(str), lambda x: datetime.datetime.strptime(x, DATE_FORMAT)), 
    "periods": And(Use(int), lambda x: 1 <= x <= 60),
    "amount": And(Use(int), lambda x: 10000 <= x <= 3000000),
    "rate": And(Use(float), lambda x: 1 <= x <= 8)
})


def next_month(date: str) -> str:
    date = datetime.datetime.strptime(date, DATE_FORMAT)
    return (datetime.datetime(year=date.year + date.month // 12, month=date.month % 12 + 1, 
                              day=monthrange(date.year, date.month % 12 + 1)[-1]).strftime(DATE_FORMAT))


def check_vector(vector: dict):
    try:
        JSON_STRUCT.validate(vector)
    except SchemaError as e:
        msg = str(e).split("\n")[0]
        if msg[-1] == '\'' or msg[-1] == '\"':
            return msg
        else: return msg[:-1]


def mod_round(val: float):
    if round(val, 2) == int(round(val, 2)):
        return int(round(val, 2))
    else:
        return round(val, 2)


def process_vector(vector: dict) -> dict:
    current_date = vector["date"]
    proc_vector = {current_date: mod_round(vector["amount"] * (1 + vector["rate"] / 12 / 100))}
    for _ in range(vector["periods"] - 1):
        proc_vector[next_month(current_date)] = mod_round(proc_vector[current_date] * (1 + vector["rate"] / 12 / 100))
        current_date = next_month(current_date)
    return proc_vector


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.errorhandler(404)
def not_found_error(error):
    return make_response(jsonify({"error": "Page not found!"}), 404)


@app.errorhandler(405)
def not_found_error(error):
    return make_response(jsonify({"error": "Method not allowed!"}), 405)


@app.route("/deposit/process", methods=["POST"])
def index():
    if not request.json:
        return make_response(jsonify({"error": "No vector was sent!"}), 400)
    vector_dict = request.json
    check_tmp = check_vector(vector_dict)
    if not check_tmp:
        return jsonify(process_vector(vector_dict))
    else:
        return make_response(jsonify({"error": check_tmp}), 400)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)