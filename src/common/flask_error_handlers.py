from flask import jsonify

def bad_request(e):
    return jsonify({
        "message": e.description,
    }), 400

def payload_too_large(e):
    return jsonify({
        "message": e.description,
    }), 413

def register_error_handlers_to(app):
    app.register_error_handler(400, bad_request)
    app.register_error_handler(413, payload_too_large)
