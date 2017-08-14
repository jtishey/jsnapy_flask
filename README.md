# jsnapy_flask
Flask web app for Juniper JSNAPy (Junos Snapshot Administrator).  Allows you to take a before and after snapshots to be used for verifying services after making a change to a Juniper device.<br>

*Only tested on Ubuntu/Debian-based Linux distros.*


 ![screenshot3](static/images/jsnapy_flask_pic.png "Screenshot")
 
<br>


### 1. Requires python2.7, Flask, flask-wtf, & jsnapy (and their dependencies)
`sudo apt-get install build-essential libssl-dev libffi-dev python-dev` <br>
`sudo pip install jsnapy Flask flask-wtf` <br>

### 2. To run jsnapy_flask
1. Run with `python app.py`
2. Click the settings icon to update the credentials and selected testfiles/location and click Update.
2. Take a pre-change snapshot by entering a hostnaame/IP, selecting Pre, and clicking Submit.
3. Take a post-change snapshot by entering the same hostname/IP, selecting Post, and clicking Submit.
   * Once the post snapshot is complete, it will be compared with the pre-change snapshot and output displayed.
   * Green = All tests passed/skipped
   * Red = A test has failed
   * Grey = All test skipped (nothing found to test)
4. Click on each section to expand tests/details
<br>


#### Settings View
![settings_view](static/images/settings_view.png "settings_view")



#### See also:
Juniper/JSNAPy:<br>
https://github.com/Juniper/jsnapy

Some test files based on:<br>
https://github.com/maxdevyatov/jsnapy_examples

Flask tutorial:<br>
https://github.com/hellt/PLAZA<br>
http://noshut.ru
