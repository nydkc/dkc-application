from flask import Flask, render_template
import dkc
# from manage.views import admin_blueprint

app = Flask(__name__)
dkc.views.register_blueprints_to(app)
# app.register_blueprint(admin_blueprint)

print(app.url_map)

if __name__ == '__main__':
    app.run(host='localhost', port=8080, debug=True)
