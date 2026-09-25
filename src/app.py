from flask import Flask, request, jsonify
from db_requests import (
    db_get_cursor,
    db_create_table,
    db_get_persons,
    db_get_by_id,
    db_post_persons,
    db_update_persons,
    db_delete_persons,
)

app = Flask(__name__)


def get_cursor():
    if "DB_CURSOR" in app.config:
        return app.config["DB_CURSOR"]
    return db_get_cursor()


@app.route("/api/v1/persons/<int:personId>", methods=["GET"])
def get_person_by_id(personId):
    status, person = db_get_by_id(get_cursor(), personId)
    if status:
        return jsonify(person), 200
    return jsonify({"error": "Person not found"}), 404


@app.route("/api/v1/persons", methods=["GET"])
def get_persons():
    status, persons = db_get_persons(get_cursor())
    if status:
        return jsonify(persons), 200
    return jsonify({"error": "Database error"}), 500


@app.route("/api/v1/persons", methods=["POST"])
def post_person():
    data = request.get_json(silent=True)

    if not data or "name" not in data:
        return jsonify({"error": "Field 'name' is required"}), 400

    status, person = db_post_persons(
        get_cursor(),
        name=data.get("name"),
        age=data.get("age"),
        address=data.get("address"),
        work=data.get("work"),
    )

    if status:
        return jsonify(person), 201
    return jsonify({"error": "Database error"}), 500


@app.route("/api/v1/persons/<int:personId>", methods=["PATCH"])
def patch_person(personId):
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Empty request body"}), 400

    allowed = {"name", "age", "address", "work"}
    if not any(key in data for key in allowed):
        return jsonify({"error": "No fields to update"}), 400

    status, person = db_update_persons(get_cursor(), personId, data)

    if status:
        return jsonify(person), 200
    return jsonify({"error": "Person not found"}), 404


@app.route("/api/v1/persons/<int:personId>", methods=["DELETE"])
def delete_person(personId):
    status = db_delete_persons(get_cursor(), personId)

    if status:
        return "", 204
    return jsonify({"error": "Person not found"}), 404


def init_app():
    cursor = db_get_cursor()
    db_create_table(cursor)
    return cursor


if __name__ == "__main__":
    cursor = init_app()
    app.config["DB_CURSOR"] = cursor
    app.run(debug=True, host="0.0.0.0")
