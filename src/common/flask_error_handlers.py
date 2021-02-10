from flask import jsonify


def client_error_handler(code):
    def handler(e):
        resp = {
            "message": e.description,
        }
        return jsonify(resp), code

    return handler


def register_error_handlers_to(app):
    for code in (400, 409, 413):
        app.register_error_handler(code, client_error_handler(code))
