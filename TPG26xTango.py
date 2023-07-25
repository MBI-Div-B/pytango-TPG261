#!/usr/bin/python3 -u

from TPG26x import *

from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt
from tango.server import Device, attribute, command, pipe, device_property
import numpy as np
from time import time

class TPG26xTango(Device):

    Port = device_property(
        dtype="str",
        default_value="/dev/ttyUSB0",
    )

    Type = device_property(
        dtype="str",
        default_value="TPG261",
    )
    
    # How to poll: https://github.com/tango-controls/pytango/issues/383
    
    pressure = attribute(label="Pressure", dtype=float,
                         display_level=DispLevel.OPERATOR,
                         polling_period=3000,
                         access=AttrWriteType.READ,
                         format="%7.3e",
                         unit="mbar",
                         doc="Pressure of gauge 1")  #how do i handle 2?    
    
    pressure_minute = attribute(label="Pressure every second", dtype=[float,],
                                max_dim_x = 60,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ,
                         doc="Pressure of gauge 1")
    pressure_hour = attribute(label="Pressure every minute", dtype=[float,],
                                max_dim_x = 60,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ,
                         doc="Pressure of gauge 1")
    pressure_day = attribute(label="Pressure every hour", dtype=[float,],
                                max_dim_x = 24,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ,
                         doc="Pressure of gauge 1")
    pressure_month = attribute(label="Pressure every day", dtype=[float,],
                                max_dim_x = 30,
                         display_level=DispLevel.EXPERT,
                         access=AttrWriteType.READ,
                         doc="Pressure of gauge 1")

    def init_device(self):
        Device.init_device(self)
        # ToDo: implement somthing that uses channels to distingush between 261 and 262

        if self.Type == 'TPG261':
            self.controller = TPG261(port=self.Port)
            self.connection = self.controller.serial
            if self.connection.isOpen():
                self.set_state(DevState.ON)
                self.info_stream('TPG261 initialised on port %s.'%self.connection.port)
        elif self.Type == 'TPG262':
            self.controller = TPG262(port=self.Port)
            self.connection = self.controller.serial
            if self.connection.isOpen():
                self.set_state(DevState.ON)
                self.info_stream('TPG262 initialised on port %s.'%self.connection.port)
        else:
            pass
        
        self._minute_array = np.empty(60)
        self._minute_array[:] = np.NaN
        self._hour_array = np.empty(60)
        self._hour_array[:] = np.NaN
        self._day_array = np.empty(24)
        self._day_array[:] = np.NaN
        self._month_array = np.empty(30)
        self._month_array[:] = np.NaN
        
        self._time = np.ones(4)*time() # minute, hour, day, month
    
    def delete_device(self):
        self.info_stream('close serial')
        self.connection.close()
    
    def read_pressure(self):
        try:
            pressure, _ = self.controller.pressure_gauge(1)
        except:
            pressure = np.NaN
            self.error_stream("Could not get value")
        
        new_time = time()
        delay = np.round(new_time-self._time[0])
        self._time[0] = new_time
        #self.debug_stream("Delay is: %.4f",delay)
        for i in np.arange(delay):
            self._minute_array = np.roll(self._minute_array,-1)
            self._minute_array[-1] = pressure
            
        #self.debug_stream('Delay since last hour_array update is %d / %d s', new_time - self._time[1], 60)
        if new_time - self._time[1] >= (60):
            self._hour_array = np.roll(self._hour_array,-1)
            self._hour_array[-1] = self._minute_array[0]
            self._time[1] = new_time
            self.info_stream("Hour array was updated. New value is %.6f, new time is %d",self._hour_array[-1],new_time)
        
        #self.debug_stream('Delay since last day_array update is %d / %d s', new_time - self._time[2],(60*60))    
        if new_time - self._time[2] >= (60*60):
            self._day_array = np.roll(self._day_array,-1)
            self._day_array[-1] = self._hour_array[0]
            self._time[2] = new_time
            self.info_stream("Day array was updated. New value is %.6f, new time is %d",self._day_array[-1],new_time)
        
        #self.debug_stream('Delay since last month_array update is %d / %d s', new_time - self._time[3], (60*60*24))
        if new_time - self._time[3] >= (60*60*24):
            self._month_array = np.roll(self._month_array,-1)
            self._month_array[-1] = self._day_array[0]
            self._time[3] = new_time
            self.info_stream("Month array was updated. New value is %.6f, new time is %d",self._month_array[-1],new_time)
        self.debug_stream("Returning: %.6f", pressure)
        return pressure

    
    def read_pressure_minute(self):
        return self._minute_array
    
    def read_pressure_hour(self):
        return self._hour_array
    
    def read_pressure_day(self):
        return self._day_array
    
    def read_pressure_month(self):
        return self._month_array

if __name__ == "__main__":
    TPG26xTango.run_server()
