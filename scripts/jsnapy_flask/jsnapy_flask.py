#!/usr/bin/env python
"""
Run Juniper Snapshot Admin (python) via HTML
Requires JSNAPy, falsk, flask-wtf, probably other stuff
github.com/jtishey/jsnapy_flask  2017
"""

import base64
import logging
import os

from flask import Blueprint, jsonify, render_template, request
from flask_wtf import FlaskForm
from jnpr.jsnapy import SnapAdmin
from wtforms import StringField, PasswordField, SelectMultipleField, validators

import format_html


class JSNAPy_Form(FlaskForm):
    """ Create the flask form """
    hostname = StringField('Hostname',
                           validators=[validators.DataRequired()])
    username = StringField('username', validators=[validators.DataRequired()], default="")
    password = PasswordField('password', validators=[validators.DataRequired()], default="")
    test_location = StringField('test_location', validators=[validators.DataRequired()], default="")
    test_files = SelectMultipleField()
    port_num = StringField('port', validators=[validators.DataRequired()], default="830")


class Run_JSNAPy:
    """ Execute the jsnapy script to snapshot a device """
    def __init__(self, args):
        """ Expects args from the flask form: hostname & pre/post tag """

        # Initalize variables
        self.host = args.form['hostname']
        self.snap = args.form['snap']
        self.data = ""
        self.error = ""

        # Read settings file and assign variables
        self.settings = get_settings()

        # Update the jsnapy.cfg file
        self.update_config()

        # Create the yaml config for jsnapy
        self.make_dev_file()

        # Run pre/post snapshot
        self.route_args()

    def update_config(self):
        """ Update jsnapy.cfg file with testfiles path specified in settings section """
        jsnapy_config = get_jsnapy_config()
        with open(jsnapy_config) as _f:
            cfg = _f.read()
        cfg2 = ""
        for line in cfg.splitlines():
            if 'test_file_path = ' in line:
                line = 'test_file_path = ' + self.settings['testlocation_value']
            cfg2 = cfg2 + line + "\n"
        with open(jsnapy_config, 'w') as _f:
            _f.write(cfg2)

    def make_dev_file(self):
        """ Create yaml config with the host specified and login creds  """
        self.template = ("hosts:\n"
                         "  - device: " + str(self.host) + "\n"
                         "    username: " + self.settings['username_value'] + "\n"
                         "    passwd: " + self.settings['password_value'] + "\n"
                         "    port: " + str(self.settings['port']) + "\n"
                         "tests:\n" +
                         self.settings['testfiles_value'])

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
        except Exception as ex:
            self.error = str(ex.args) + "\n" + str(ex.message)
            return

    def post_check(self):
        """ Run post-change snapshot and compare with pre """
        js = SnapAdmin()
        try:
            self.post_snap = js.snap(self.template, "post")
        except Exception as ex:
            self.error = str(ex.args) + "\n" + str(ex.message)
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

def get_settings():
    """ Open settings.txt and get values """
    settings = {}
    with open('scripts/jsnapy_flask/settings.txt') as _f:
        s = _f.read()
    s = base64.b64decode(s)
    s = s.split(',')
    settings['username_value'] = s[0]
    settings['password_value'] = s[1]
    settings['testlocation_value'] = s[2]
    settings['testfiles_value'] = s[3]
    settings['port'] = s[4]
    return settings

def get_jsnapy_config():
    """ Open jsnapy.cfg file """
    if os.environ.has_key('VIRTUAL_ENV'):
        jsnapy_config = os.environ['VIRTUAL_ENV'] + '/etc/jsnapy/jsnapy.cfg'
        if os.path.exists(jsnapy_config):
            return jsnapy_config
    jsnapy_config = '/etc/jsnapy/jsnapy.cfg'
    return jsnapy_config

class UpdateSettings:
    """ Update the settings file """
    def __init__(self, args):
        """ Expects args from the flask form: Username, Password & Testfiles Path """
        self.settings = get_settings()
        self.username = str(args.form['username'])
        self.password = str(args.form['password'])
        self.test_loc = str(args.form['test_location'])
        self.test_files = args.form.getlist('test_files')
        self.port_num = str(args.form['port_num'])

        self.format_password()
        self.format_test_files()
        self.format_port_number()
        self.write_settings()

    def format_password(self):
        """ Use existing password if submitted one is blank """
        if self.password == "":
            self.password = self.settings['password_value']

    def format_test_files(self):
        """ Make test list into a string and use previous if empty """
        self.test_list = ''
        if self.test_files == "":
            self.test_files = self.settings['testfiles_value']
        for item in self.test_files:
            self.test_list = self.test_list + '  - ' + item + '\n'

    def format_port_number(self):
        """ Default port number for NETCONF 830 """
        if self.port_num == "":
            self.port_num = "830"

    def write_settings(self):
        """ Write settings.txt file """
        self.jsettings = self.username + ',' + self.password + ',' + self.test_loc + "," \
            + self.test_list + "," + self.port_num
        save_data = base64.b64encode(str(self.jsettings))
        with open('scripts/jsnapy_flask/settings.txt', "w") as _f:
            _f.write(save_data)


def generate_form_values(form):
    """ Set values for settings form """
    my_choices = []
    my_selected = []
    settings = get_settings()
    yml_files = os.popen("ls " + settings['testlocation_value'] + "*.yml").read()
    for line in yml_files.splitlines():
        line = line.replace(settings['testlocation_value'], '')
        my_choices.append((line, line))
    for line in settings['testfiles_value'].splitlines():
        line = line.replace('  - ', '').rstrip()
        my_selected.append(line)
    form.username.data = settings['username_value']
    form.password.data = settings['password_value']
    form.test_location.data = settings['testlocation_value']
    form.test_files.choices = my_choices
    form.test_files.data = my_selected
    form.port_num.data = settings['port']
    return form

# FLASK SECTION - Blueprint and Route - #

jsnapy_flask_bp = Blueprint('jsnapy_flask', __name__, template_folder='templates',
                            static_folder='static', static_url_path='/jsnapy_flask/static')
jsnapy_settings_bp = Blueprint('jsnapy_settings', __name__, template_folder='templates',
                               static_folder='static', static_url_path='/jsnapy_flask/static')


@jsnapy_flask_bp.route('/jsnapy_flask', methods=['GET', 'POST'])
def jsnapy_flask():
    """ Run Juniper Snapshot Manager on a device """
    if request.method == 'GET':
        form = JSNAPy_Form()
        form = generate_form_values(form)
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
    UpdateSettings(request)
    return ""
