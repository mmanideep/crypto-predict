from flask import render_template
from flask.views import MethodView


class Index(MethodView):

    url = ""

    def get(self):
        return render_template('index.html')
