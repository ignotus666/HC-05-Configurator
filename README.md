# HC-05 Configurator
![HC-05-configurator_pic](https://github.com/user-attachments/assets/7b77f596-b9d0-4e0d-8b73-48dabe2bd9a3)

A Python application designed to configure HC-05 Bluetooth devices through a graphical user interface. The application allows users to query and set various parameters of the HC-05 module using AT commands. I use a USB-FTDI converter.

## Features

By default the user interface lists some of the most typical AT commands, but there is a full list of commands accessible via Preferences -> Customize Commands. Checked commands will be shown in the main window.

## Requirements

To run this project, you need to install the following dependencies:

- PyQt5: For creating the GUI.
- pyserial: For serial communication with the HC-05 module.

## Usage

1. Connect your HC-05 module to your computer via a USB-FTDI converter.
2. Open the application and select the appropriate serial port (e.g., `/dev/ttyUSB0`).
3. "Query" buttons will show the module's setting for the selected parameter.
4. "Set" buttons will send the argument(s) entered into the field for the corresponding paramter. It is not necessary to enter the full command, just the argument(s).

It is possible to save profiles and load them. Any arguments that have been entered into the parameter fields (either manually by the user or by using "Query") can be saved to a .cfg file.

**Note**: some versions of HC-05 modules (particularly cheap Chinese knock-offs) will not allow you to set or even query certain parameters. Some modules require you to keep the "state" button held down to enter full AT mode, while others may need the "EN" connected to 3.3V. YMMV.
