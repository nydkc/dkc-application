from flask import Blueprint, render_template
from datetime import datetime

index_bp = Blueprint("index", __name__, template_folder="templates")

# class MainPage(BaseHandler):

#     def get(self):
#         config = ndb.Key(Settings, 'config').get()
#         template_values = {
#             'config': config
#         }
#         self.render_template('index.html', template_values)


@index_bp.route("/")
def index():
    # TODO(dannyqiu): update with settings from ndb
    template_values = {
        'settings': {
            'due_date': datetime.now(),
        }
    }
    return render_template("index.html", **template_values)
