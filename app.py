#!/usr/bin/env python

from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

# Import Script Blueprints:
from scripts.jsnapy_flask.jsnapy_flask import jsnapy_flask_bp
from scripts.jsnapy_flask.jsnapy_flask import jsnapy_settings_bp

# initialize Flask app
app = Flask(__name__)
CSRFProtect(app)

@app.route('/')
@app.route('/index')
def index():
    """ home page """
    return render_template("index.html", name="index", active_page='index',)


# - Register Script Blueprints - #
app.register_blueprint(jsnapy_flask_bp)
app.register_blueprint(jsnapy_settings_bp)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.debug = True
    app.run()
