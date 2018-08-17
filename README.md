Serial Scale Server
====
Browsers don't have the ability to access devices connected via serial port, which is unfortunate for people who wish to use postal scales or other old hardware from a website. A somewhat-convoluted but actually rather simple solution is to spin up a quick flask webserver on the local device that creates an http interface between the COM port and the browser.

# How To Use
First, make sure you have [Python 3](https://www.python.org/) installed. Then, just download the code, run `pip install -r requirements.txt` to get the necessary libraries (using a virtualenv is suggested but not necessary), and call `python -m app` from the package directory, at which point the scale server methods should be accessible at localhost's port 5000. You can optionally pass a command line argument of the COM port to use by default, for example `python -m app COM2`.
# How It Works
## The Scale
The **SerialScaleReader** object is essentially a wrapper around the [pySerial library](https://pythonhosted.org/pyserial/), applied specifically to interact with a scale. It has a few useful methods:
* **read_weight:** Writes the command to the COM port to get the weight from the scale (command configurable via init kwarg), waits a moment for a response (length of wait also configurable via init kwarg), and then returns whatever the scale sends back.
* **get_settings:** Gets the settings of the pyserial object that is used to communicate with the scale.
* <a name="update_settings"></a> **update_settings:** Changes the settings of the pyserial object that is used to communicate with the scale. Includes:

Setting  | Accepted Values
------------- | -------------
[port](https://en.wikipedia.org/wiki/COM_(hardware_interface))   | Device names on your computer, for example 'COM1', 'COM2'
[baud_rate](https://en.wikipedia.org/wiki/Serial_port#Speed)  | Integer
[parity](https://en.wikipedia.org/wiki/Serial_port#Parity)  | 'none', 'even', 'odd', 'mark', 'space'
[stop_bits](https://en.wikipedia.org/wiki/Serial_port#Stop_bits)  | 1, 1.5, 2
[byte_size](https://en.wikipedia.org/wiki/Serial_port#Data_bits)  | 5, 6, 7, 8

* **update_and_get_settings:** Calls update_settings and get_settings, returning both the current settings and any errors encountered when updating them. Mostly for convenience.

## The Server
The server is incredibly simple, essentially just a one-to-one link between an endpoint and the SerialScaleReader object's methods. The endpoints are as follows:
* **/:** The root. It just encourages you to do something useful.
* **/get_settings:** Returns the serial port settings as json.
* **/update_settings:** Updates the serial port settings, returning them (and any errors) as json. Values can be sent as parameters in a GET request (`e.g. localhost:5000/update_settings?port=COM3&baud_rate=9600&stop_bits=1.5`) in order to make it easier to bookmark and share presets, or via form data in a POST request. The values which can be sent match the SerialScaleReader's [update_settings kwargs](#update_settings).
* **/read:** Returns whatever is read from the scale (or the error received if it failed)
