from TPG26x import *

from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt
from tango.server import Device, attribute, command, pipe, device_property

class TPG26xTango(Device):

    Port = device_property(
        dtype="str",
        default_value="/dev/ttyUSB0",
    )

    Type = device_property(
        dtype="str",
        default_value="TPG261",
    )
    
    pressure = attribute(label="Pressure", dtype=float,
                         display_level=DispLevel.OPERATOR,
                         access=AttrWriteType.READ,
                         doc="Pressure of gauge 1")  #how do i handle 2?

    # how about polling?

    def init_device(self):
        Device.init_device(self)
        # implement somthing that uses channels to distingush between 261 and 262

        if self.Type == 'TPG261':
            self.controller = TPG261(port=self.Port)
            self.connection = self.controller.serial
            if self.connection.isOpen():
                self.set_state(DevState.ON)
                print('Initialised on port %s.'%self.connection.port)
        elif self.Type == 'TPG262':
            self.controller = TPG262(port=self.Port)
            self.connection = self.controller.serial
            if self.connection.isOpen():
                self.set_state(DevState.ON)
                print('Initialised on port %s.'%self.connection.port)
        else:
            pass
            #raise ValueError('Unsupported Device Type)
        
    def read_pressure(self):
        pressure, _  = self.controller.pressure_gauge(1) # how do i handle 2?
        return pressure
    
    def read_Test(self):
        return self.Test

if __name__ == "__main__":
    TPG26xTango.run_server()