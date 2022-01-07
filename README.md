# IOTCommander-server-python

IOTCommander is a service to help control custom-made IOT devices over your local network.

The idea is that you are running the server on your IOT device regardless of platform, and then you are able to control
it with the [client application](https://github.com/klitos-giannak/IOTCommander-client-android) or even directly
sending commands through your terminal or browser.

There are two services that are running with IOTCommander. One is to
enable any client to "discover" the IOT devices without any configuration on the client, and the second is to enable
receiving commands from the client. A special [config file](commands_config.json) is meant to be changed upon
installation on the IOT device providing flexibility for usage in any custom IOT. Inside the
[config file](commands_config.json) any number of commands can be specified, with any number out of 4 types of
parameters(text, int, float, boolean) and a mapping to an actual command running on the IOT device's shell.
<b>No configuration is needed on the client</b>, it reads the "supported commands" from the IOT device itself.

This is the python implementation of the server. You can use this in any IOT device capable of connecting to your local
network using any means(wi-fi, ethernet, etc.). You can use this in devices like raspberry-pi, or any other device
capable of running python and connecting to a network (e.g. OrangePi, NanoPi, Onion Omega, etc.). I haven't tested with
micropython in microcontrollers like ESP32 yet, but if you do, please let me know how it goes.

## Installation instructions
1. clone the repository or download as zip and extract
2. cd inside the root directory (IOTCommander-server-python if you haven't changed it)
3. Run `pipenv install` to install needed dependencies
4. Run with `python3 iot_commander.py`

*3 alternative, if you don't have/want to run pipenv, download [MicroWebSrv2](https://github.com/infinite-tree/MicroWebSrv2.git)
and copy the "MicroWebSrv2" directory to the root directory of this project

## Testing
The easiest way to test would be to download the client on your Android device from
[Google Play](https://play.google.com/store/apps/details?id=mobi.duckseason.iotcommander). Then make sure your Android
device is in the same network as the server device and use the app

If you want to test manually, here are some guidelines for a linux shell
- [How to test discover_service.py](docs/DISCOVER_SERVICE.md)
- [How to test commands_service.py](docs/COMMANDS_SERVICE.md)

NOTES:

1. IOTCommander is low on security at this point.
   - It does not implement authentication so any client on your local network will be able to control your IOT devices
   - It does not implement encryption of any kind, so all information exchanged in your local network is plain text

2. IOTCommander was created with IOT devices in mind, for example 
   - turn your LED-strip on or off
   - save a picture from your smart custom-made security camera

   but it's made in such a generic way that you can use it for more advanced stuff, for example
   - Search on Google and show me the results on my pc
   - start playing X song on Spotify on my raspberry-pi hooked on my TV

   