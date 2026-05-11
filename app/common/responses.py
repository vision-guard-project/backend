from flask import jsonify


def success(data=None, message="success", status_code=200):
    body = {"message": message}
    if data is not None:
        body["data"] = data
    return jsonify(body), status_code


def created(data=None, message="created"):
    return success(data=data, message=message, status_code=201)


def error(message="error", code="ERROR", status_code=400, details=None):
    body = {
        "message": message,
        "error": code,
    }
    if details is not None:
        body["details"] = details
    return jsonify(body), status_code
