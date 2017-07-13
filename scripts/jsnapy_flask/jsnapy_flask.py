#!/usr/bin/env python
"""
Run Juniper Snapshot Admin (python) via HTML
Requires JSNAPy, falsk, flask-wtf, probably other stuff
github.com/jtishey/jsnapy_flask  2017
"""

import logging
import os

from flask import Blueprint, jsonify, render_template, request
from flask_wtf import FlaskForm
from jnpr.jsnapy import SnapAdmin
from wtforms import StringField, PasswordField, SelectMultipleField, validators

import format_html


class JSNAPy_Form(FlaskForm):
    """ Create the flask form """
    with open("scripts/jsnapy_flask/settings.txt") as _f:
        settings = _f.read()
    settings = settings.split(',')
    username_value = settings[0]
    password_value = settings[1]
    testfiles_value = settings[2]

    hostname = StringField('Hostname',
                           validators=[validators.DataRequired()])
    username = StringField('username', validators=[validators.DataRequired()], default=username_value)
    password = PasswordField('password', validators=[validators.DataRequired()], default=password_value)
    test_location = StringField('test_location', validators=[validators.DataRequired()], default=testfiles_value)
    my_choices = []
    i = 0
    yml_files = os.popen("ls " + testfiles_value + "*.yml").read()
    for i, line in enumerate(yml_files.splitlines(), start=1):
        line = line.replace(testfiles_value, '')
        my_choices.append((line, line))
    test_files = SelectMultipleField(choices=my_choices, default=range(1, i + 1))


class Run_JSNAPy:
    """ Execute the jsnapy script to snapshot a device """
    def __init__(self, args):
        """ Expects args from the flask form: hostname & pre/post tag """
        self.get_settings()

        # Initalize variables
        self.host = args.form['hostname']
        self.snap = args.form['snap']
        self.username_value = self.settings[0]
        self.password_value = self.settings[1]
        self.testlocation_value = self.settings[2]
        self.testfiles_value = self.settings[3]
        self.data = ""
        self.error = ""

        # Update the jsnapy.cfg file
        self.update_config()

        # Create the yaml config for jsnapy
        self.make_dev_file()

        # Run pre/post snapshot
        self.route_args()

    def get_settings(self):
        with open('scripts/jsnapy_flask/settings.txt') as _f:
            settings = _f.read()
        self.settings = settings.split(',')

    def update_config(self):
        """ Update config file with testfiles path specified in settings section """
        with open('/etc/jsnapy/jsnapy.cfg') as _f:
            cfg = _f.read()
        cfg2 = ""
        for line in cfg.splitlines():
            if 'test_file_path = ' in line:
                line = 'test_file_path = ' + self.testlocation_value
            cfg2 = cfg2 + line + "\n"
        with open('/etc/jsnapy/jsnapy.cfg', 'w') as _f:
            _f.write(cfg2)

    def make_dev_file(self):
        """ Create yaml config with the host specified and login creds  """
        with open('./scripts/jsnapy_flask/device_template.yml') as f1:
            self.template = f1.read()
        self.template = self.template.replace('SOME_HOST', self.host)
        self.template = self.template.replace('SOME_USER', self.username_value)
        self.template = self.template.replace('SOME_PASS', self.password_value)
        self.template = str(self.template)
        self.template = self.template + self.testfiles_value

    def route_args(self):
        """ Determines if the user wants a pre-check or post-check """
        if self.snap == 'pre':
            self.pre_check()
        elif self.snap == 'post':
            self.post_check()

    def pre_check(self):
        """ Run pre-change snapshot """
        js = SnapAdmin()
        try:
            self.pre_snap = js.snap(self.template, "pre")
            self.data = 'Pre-check snapshot complete'
        except:
            self.error = 'Error running snapshot'
            return

    def post_check(self):
        """ Run post-change snapshot and compare with pre """
        js = SnapAdmin()
        try:
            self.post_snap = js.snap(self.template, "post")
        except:
            self.error = "Error running snapshot"
            return
        self.post_compare()

    def post_compare(self):
        """ Run post check and gather output """
        # Setup a memory buffer to capture logging messages from jsnapy
        jsnapy_log = logging.handlers.MemoryHandler(1024*10, logging.DEBUG)
        jsnapy_log.setLevel(logging.DEBUG)
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        debug_format = logging.Formatter("%(message)")
        jsnapy_log.setFormatter(debug_format)
        log.addHandler(jsnapy_log)

        # Run jsnapy check on pre and post snapshots
        js = SnapAdmin()
        self.result = js.check(self.template, pre_file="pre", post_file="post")

        # Gather output from buffer
        post_log = []
        for line in jsnapy_log.buffer:
            post_log.append(str(line.getMessage()))
        self.data = format_html.formatting(post_log)


class UpdateSettings:
    """ Update the settings file """
    def __init__(self, args):
        """ Expects args from the flask form: Username, Password & Testfiles Path """
        username = str(args.form['username'])
        password = str(args.form['password'])
        test_loc = str(args.form['test_location'])
        test_files = args.form.getlist('test_files', type=str)
        test_list = ''
        for item in test_files:
            test_list = test_list + '  - ' + item + '\n'
        jsettings = username + ',' + password + ',' + test_loc + "," + test_list
        with open('scripts/jsnapy_flask/settings.txt', "w") as _f:
            _f.write(jsettings)


# FLASK SECTION - Blueprint and Route - #

jsnapy_flask_bp = Blueprint('jsnapy_flask', __name__, template_folder='templates', static_folder='static',
                            static_url_path='/jsnapy_flask/static')
jsnapy_settings_bp = Blueprint('jsnapy_settings', __name__, template_folder='templates', static_folder='static',
                               static_url_path='/jsnapy_flask/static')


@jsnapy_flask_bp.route('/jsnapy_flask', methods=['GET', 'POST'])
def jsnapy_flask():
    """ Run Juniper Snapshot Manager on a device """
    if request.method == 'GET':
        form = JSNAPy_Form()
        return render_template("jsnapy_flask.html", name="jsnapy", active_page="jsnapy", form=form)
    elif request.method == 'POST':
        snapshot = Run_JSNAPy(request)
        results = {'data': snapshot.data,
                   'error': snapshot.error
                  }
        return jsonify(results)
    else:
        return ""


@jsnapy_settings_bp.route('/jsnapy_settings', methods=['POST'])
def jsnapy_settings():
    """ Run Juniper Snapshot Manager on a device """
    settings = UpdateSettings(request)
    return ""
