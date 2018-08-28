import hashlib

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path="", static_folder="static")
app.config.from_object('base_app.config.DevConfig')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from uni_block.controllers import export_api_list
from uni_block.views import export_views_list

end_points = set(export_views_list).union(set(export_api_list))

for api in end_points:
    if hasattr(api, "url"):
        api_url = getattr(api, "url")
    else:
        api_url = api.__name__.lower().split("api")[0]
    api_name = api.__name__.lower()
    print (api_name, " -> ", "/{}".format(api_url))
    view = api.as_view("{}".format(api_name))
    app.add_url_rule(
        "/{}".format(api_url),
        view_func=view
    )
