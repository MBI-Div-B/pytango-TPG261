from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt
from tango.server import Device, attribute, command, pipe, device_property
from time import time

import socket
import serial
from .control_interface.tpg261 import TPG26XControlInterface, CommandList

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

    def init_device(self):
        Device.init_device(self)
        # ToDo: implement somthing that uses channels to distingush between 261 and 262
        self.control_interface = TPG26XControlInterface(backend=self.ConnectType, socket_hostname=self.HostName, socket_port=self.PortNumber, baudrate=self.Baudrate)
        self.set_state(DevState.ON)

    def delete_device(self):
        self.info_stream("close serial")
        self.control_interface.close()

    def read_pressure(self):
        return self.control_interface.read_command(CommandList.PRESSURE_ONE)

if __name__ == "__main__":
    TPG261.run_server()
