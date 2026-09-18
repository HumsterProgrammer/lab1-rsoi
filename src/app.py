from flask import Flask
from db_requests import *

"""
* `GET /persons/{personId}` – информация о человеке;
* `GET /persons` – информация по всем людям;
* `POST /persons` – создание новой записи о человеке;
* `PATCH /persons/{personId}` – обновление существующей записи о человеке;
* `DELETE /persons/{personId}` – удаление записи о человеке.

PersonRequest:
  required:
  - name
  type: object
  properties:
    name:
      type: string
    age:
      type: integer
      format: int32
    address:
      type: string
    work:
      type: string
PersonResponse:
  required:
  - id
  - name
  type: object
  properties:
    id:
      type: integer
      format: int32
    name:
      type: string
    age:
      type: integer
      format: int32
    address:
      type: string
    work:
      type: string
"""

app_name = "persons"
app = Flask(app_name)

# `GET /persons/{personId}` – информация о человеке;
@app.route("/persons/<personId>", methods=["GET"])
def get_persons_id(personId):
	status, data = get_by_id(personId)
	if status:
		# собираем json
		return json_response, 200
	return "", 404

# `GET /persons` – информация по всем людям;
@app.route("/persons", methods=["GET"])
def get_persons():
	return "501 Not Implemented", 200

# `POST /persons` – создание новой записи о человеке;
@app.route("/persons", methods=["POST"])
def post_persons():
	return "501 Not Implemented", 201

# `PATCH /persons/{personId}` – обновление существующей записи о человеке;
@app.route("/persons", methods=["PATCH"])
def patch_persons():
	return "501 Not Implemented"
	
# `DELETE /persons/{personId}` – удаление записи о человеке.
@app.route("/persons", methods=["DELETE"])
def delete_persons():
	return "501 Not Implemented"

if __name__ == "__main__":
	app.run(debug=True)
