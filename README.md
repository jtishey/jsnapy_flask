# jsnapy_flask
Flask app interface for JSNAPy (Junos Snapshot Administrator)
<br>

#### Requires python2.7, Flask, flask-wtf, & jsnapy
`sudo apt-get install build-essential libssl-dev libffi-dev python-dev` <br>
`sudo -H /usr/bin/pip install jsnapy` <br>
`sudo -H /usr/bin/pip install Flask` <br>
`sudo -H /usr/bin/pip install flask-wtf` <br>
<br>

#### After install do one of the following:
1. Copy the yaml files from the `./scripts/jsnapy_flask/testfiles` direcotry to `/etc/jsnapy/testfiles/`
2. Edit `/etc/jsnapy/jsnapy.cfg` to point the testfiles directory to where you have `./scripts/jsnapy_flask/testfiles`
<br>
<br>

#### Edit the scripts/jsnapy_flask/device_template.yml file to edit credentials and which testfiles to run.

Still very much a work in progress / weekend project.