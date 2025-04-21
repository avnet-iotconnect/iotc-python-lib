# Introduction
This project is the library that abstracts the /IOTCONNECT protocols for the SDKs like the
[/IOTCONNECT Python Lite SDK](https://github.com/avnet-iotconnect/iotc-python-lite-sdk)
and the [/IOTCONNECT Greengrass SDK](https://github.com/avnet-iotconnect/iotc-python-greengrass-sdk).

This library should generally not be used in other projects as the SDKs should be able 
to provide all the functionality that you would need in your python applications.

# Features

The library provides common code for interacting with /IOTCONNECT MQTT and HTTP device connectivity services:
* Format Telemetry (Reporting) messages
* Provide events for OTA and Command processing
* Streamline OTA and Command acknowledgements
* Obtain Discovery and Identity information

# Using The Library

To use this library in your project, ensure that your pyton project depends on iotconnect-lib.
Use a fixed major version dependency (E.g. "iotconnect-lib<2.0.0".) to 
avoid potential major version breaking your application calls.

The best way to learn how to use this library is to examine the unit test usage examples
in the [tests](tests) directory.   

# Licensing

This python package is distributed under the [MIT License](LICENSE.md).


