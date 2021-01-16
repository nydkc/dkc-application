from flask import jsonify
import logging

def bad_request(e):
    return jsonify({
        "message": e.description,
    }), 400

def register_error_handlers_to(app):
    app.register_error_handler(400, bad_request)
