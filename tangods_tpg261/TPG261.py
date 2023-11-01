#!/usr/bin/python3 -u

from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt
from tango.server import Device, attribute, command, pipe, device_property
from time import time

import socket
import serial


class TPG261(Device):
    ConnectType = device_property(
        dtype="str", default_value="serial", doc="either `net` or `serial`"
    )

    SerialPort = device_property(
        dtype="str",
        default_value="/dev/ttyUSB0",
        doc="Serial port of device",
    )

    Baudrate = device_property(
        dtype="int",
        default_value=9600,
        doc="Baudrate of serial port",
    )

    HostName = device_property(
        dtype="str",
        default_value="device.domain",
        doc="Hostname / IP address of device",
    )

    PortNumber = device_property(
        dtype="int",
        default_value=2001,
        doc="Socket port number of device",
    )

    pressure = attribute(
        label="Pressure",
        dtype=float,
        display_level=DispLevel.OPERATOR,
        access=AttrWriteType.READ,
        format="%7.3e",
        unit="mbar",
    )

    ETX = chr(3)  # End text (Ctrl-c)
    CR = chr(13)  # Carriage return
    LF = chr(10)  # Line feed
    ENQ = chr(5)  # Enquiry
    ACK = chr(6)  # Acknowledge
    NAK = chr(21)  # Negative acknowledge

    def init_device(self):
        Device.init_device(self)
        # ToDo: implement somthing that uses channels to distingush between 261 and 262

        if self.ConnectType == "serial":
            self.con = serial.Serial(
                port=self.SerialPort, baudrate=self.Baudrate, timeout=1
            )
            self.set_state(DevState.ON)
            self.info_stream(
                "Connected to serial port {:s} with baudrate {:d}".format(
                    self.SerialPort, self.Baudrate
                )
            )
        elif self.ConnectType == "net":
            self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.con.connect((self.HostName, self.PortNumber))
            self.set_state(DevState.ON)
            self.info_stream(
                "Connected to socket hostname {:s} at port {:d}".format(
                    self.HostName, self.PortNumber
                )
            )
        else:
            self.set_state(DevState.OFF)
            self.error_stream("Unknown `ConnectType` {:s}".format(self.ConnectType))

    def delete_device(self):
        self.info_stream("close serial")
        self.con.close()

    def read_pressure(self):
        self._send_command("PR1")
        reply = self._get_data()
        status_code = int(reply.split(",")[0])
        pressure = float(reply.split(",")[1])

        self.debug_stream("Returning: %.6f", pressure)
        return pressure

    def _cr_lf(self, string):
        """Pad carriage return and line feed to a string
        :param string: String to pad
        :type string: str
        :returns: the padded string
        :rtype: str
        """
        command = string + self.CR + self.LF
        return command.encode()

    def _send_command(self, command):
        if self.ConnectType == "net":
            self.con.send(self._cr_lf(command))
            response = self.con.recv(1024)
        elif self.ConnectType == "serial":
            self.con.write(self._cr_lf(command))
            response = self.con.readline()

        if response == self._cr_lf(self.NAK):
            message = "Serial communication returned negative acknowledge"
            raise IOError(message)
        elif response != self._cr_lf(self.ACK):
            message = "Communication returned unknown response:\n{}" "".format(
                repr(response)
            )
            raise IOError(message)

    def _get_data(self):
        """Get the data that is ready on the device"""
        command = self.ENQ
        if self.ConnectType == "net":
            self.con.send(command.encode())
            data = self.con.recv(1024)
        elif self.ConnectType == "serial":
            self.con.write(command.encode())
            data = self.con.readline()

        return data.decode().rstrip(self.LF).rstrip(self.CR)


if __name__ == "__main__":
    TPG261.run_server()
