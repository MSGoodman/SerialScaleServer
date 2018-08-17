"""
This module spins up a quick flask server to interface with the SerialScaleReader.
This allows us to use a serial port over http since a browser can't access it.
"""
import sys
import json
from flask import Flask, request
from scale import SerialScaleReader

app = Flask(__name__)

scale_reader = SerialScaleReader(port='COM1')

@app.route("/")
def index():
    """ Serves a page that tells you to use a more accurate endpoint for the scale """
    return ("Access a serial port scale via http: <ul>"
            "<li><a href='/read'>'/read'</a> to read scale response</li>"
            "<li><a href='/get_settings'>'/get_settings'</a> to view scale settings</li>"
            "<li><a href='/update_settings'>'/update_settings'</a> to change scale settings via GET or POST</li> </ul>")

@app.route("/update_settings", methods=['GET', 'POST'])
def update_settings():
    """ Updates the serial port reader with settings sent as parameters in a GET or form data in a POST """
    if request.method == 'POST':
        new_settings = {k: v for k, v in request.form.items()}
    else:
        new_settings = {k: v for k, v in request.args.items()}
    return json.dumps(scale_reader.update_and_get_settings(**new_settings))

@app.route("/get_settings")
def get_settings():
    """ Gets the serial port reader settings """
    return json.dumps(scale_reader.get_settings())

@app.route("/read")
def read():
    """ Sends a read command and reads the response from the serial port """
    return scale_reader.read_weight()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port_arg = sys.argv[1]
        scale_reader = SerialScaleReader(port=port_arg)
    app.run()
