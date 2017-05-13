# jsnapy_flask
Flask app interface for JSNAPy (Junos Snapshot Administrator)

### Requires python2.7, Flask, flask-wtf, & jsnapy
`sudo apt-get install build-essential libssl-dev libffi-dev python-dev` <br>
`sudo -H /usr/bin/pip install jsnapy` <br>
`sudo -H /usr/bin/pip install Flask` <br>
`sudo -H /usr/bin/pip install flask-wtf` <br>

### After install do one of the following:
1. Copy the yaml files from the `./scripts/jsnapy_flask/testfiles` direcotry to `/etc/jsnapy/testfiles/`
2. Edit `/etc/jsnapy/jsnapy.cfg` to point the testfiles directory to where you have `./scripts/jsnapy_flask/testfiles`

### Edit the scripts/jsnapy_flask/device_template.yml file to edit credentials and which testfiles to run.

### To run pre and post change snapshots;
1. Take a pre-change snapshot by entering a hostnaame/IP, selecting Pre, and clicking Submit.
2. Take a post-change snapshot by entering the same hostname/IP, selecting Post, and clicking Submit.
   * Once the post snapshot is complete, it will be compared with the pre-change snapshot and output displayed.
   * Passed tests are green - Indicates all tests passed for the given command
   * Failed tests are red - Indicates a change between the pre/post check
   * Skipped tests are grey - Indicates the test is not applicable to the current config
3. Click on each section to expand
<br>

Still very much a work in progress / weekend project.
<br>