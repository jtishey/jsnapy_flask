#!/usr/bin/env python
"""
Run Juniper Snapshot Admin (python) via HTML
Requires JSNAPy, falsk, flask-wtf, probably other stuff
github.com/jtishey/jsnapy_flask  2017
"""

import os
import re
import logging
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
        # Create the yaml config for jsnapy
        self.make_dev_file()
        # Run pre/post snapshot
        self.route_args()

    def make_dev_file(self):
        """ Create yaml config with the host specified and login creds  """
        with open('./scripts/jsnapy_flask/device_template.yml') as f1:
            self.template = f1.read()
        self.template = self.template.replace('SOME_HOST', self.host)
        self.template = str(self.template)

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
            self.review = ""
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
        self.format_results(post_log)

    def format_results(self, post_log):
        """ Do some output formatting based on verbosity and readability """
        self.data = ""
        for line in post_log:
            line = re.sub('\\x1b\[.{1,2}m', '', line)
            if 'Nodes are not present in given Xpath' in line:
                line = line.replace('Nodes are not present in given Xpath:', 'No info found for the given criteria')
            skip_line = line_filter(line)
            if skip_line is False:
                line = line + '<br>\n'
                self.data = self.data + line
        self.data = format_html.output(self.data)


def line_filter(line):
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
