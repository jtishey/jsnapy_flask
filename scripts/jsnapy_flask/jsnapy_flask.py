#!/usr/bin/env python
"""
Run Juniper Snapshot Admin (python) via HTML
Requires JSNAPy, falsk, flask-wtf, probably other stuff
github.com/jtishey/jsnapy_flask  2017
"""

import os
import re
from flask import Blueprint, jsonify, render_template, request
from jnpr.jsnapy import SnapAdmin
import format_html
from flask_wtf import FlaskForm
from wtforms import StringField, validators


class JSNAPy_Form(FlaskForm):
    """ Here's your stupid flask form """
    hostname = StringField('Hostname',
                           validators=[validators.DataRequired()])


class Run_JSNAPy:
    """ Execute the jsnapy script to snapshot a device """
    def __init__(self, args):
        """ Expects args from the flask form: hostname & pre/post tag """
        # Initalize variables
        self.host = args.form['hostname']
        self.snap = args.form['snap']
        self.data = ""
        self.error = ""
        self.review = ""
        # Create the devices.yml file for jsnapy
        self.make_dev_file()
        # Run pre/post snapshot
        self.route_args()

    def make_dev_file(self):
        """ Create a yaml file with the host specified and login creds  """
        # Should look and see if a string is usable instead
        with open('./scripts/jsnapy_flask/device_template.yml') as f1:
            template = f1.read()
        template = template.replace('SOME_HOST', self.host)
        with open('./scripts/jsnapy_flask/devices.yml', 'w') as f2:
            f2.write(template)

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
            self.pre_snap = js.snap("./scripts/jsnapy_flask/devices.yml", "pre")
            self.data = 'Pre-check snapshot complete'
            self.review = ""
        except:
            self.error = 'Error running snapshot'
            return

    def post_check(self):
        """ Run post-change snapshot and compare with pre """
        js = SnapAdmin()
        try:
            self.post_snap = js.snap("./scripts/jsnapy_flask/devices.yml", "post")
        except:
            self.error = "Error running snapshot"
            return
        with open('/var/log/jsnapy/jsnapy.log') as f1:
            pre_log = f1.readlines()
        self.result = js.check("./scripts/jsnapy_flask/devices.yml",
                               pre_file="pre", post_file="post")
        self.get_results(pre_log)

    def get_results(self, pre_log):
        """" Get the post chek output as post_log """
        with open('/var/log/jsnapy/jsnapy.log') as f1:
            post_log = f1.readlines()
        for line in pre_log:
            post_log.pop(0)
        self.format_results(post_log)

    def line_filter(self, line):
        """ Filter lines with specific words """
        blacklist = ['** Device', '--Performing ', 'Tests Included',
                     'jnpr.jsnapy', 'ID gone missing', 'ID list']
        skip_line = False
        if line == '':
            skip_line = True
        else:
            for key in blacklist:
                if key in line:
                    skip_line = True

        return skip_line

    def format_results(self, post_log):
        """ Do some output formatting based on verbosity and readability """
        self.data = ""
        for line in post_log:
            line = re.sub('\\x1b\[.{1,2}m', '', line)
            if 'Nodes are not present in given Xpath' in line:
                line = line.replace('Nodes are not present in given Xpath:', 'No info found for the given criteria')
            skip_line = self.line_filter(line)
            if skip_line is False:
                line = line + '<br>'
                self.data = self.data + line
        self.data = format_html.output(self.data)
        os.remove("./scripts/jsnapy_flask/devices.yml")


# FLASK SECTION - Blueprint and Route - #

jsnapy_flask_bp = Blueprint('jsnapy_flask', __name__, template_folder='templates', static_folder='static',
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
                   'verbose': snapshot.review,
                   'error': snapshot.error
                  }
        return jsonify(results)
    else:
        return ""
