from flask import Blueprint, render_template

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
    settings = {
        "due_date": 2020,
    }
    template_values = {"settings": settings}
    return render_template("index.html", **template_values)
