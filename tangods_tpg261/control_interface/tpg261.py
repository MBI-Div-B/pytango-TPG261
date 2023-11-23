from enum import IntEnum, Enum
import time

class ResponseType(IntEnum):
    ACKNOWLEDGE = 0
    MEASUREMENT = 1

class RequestType(IntEnum):
    MNEMONICS = 0
    ENQUIRY = 1

class CommandList(Enum):
    ENQUIRY = b'\x05'
    PRESSURE_ONE = b'PR1'
    PRESSURE_TWO = b'PR2'
    RESET = b'RES'

class TPG26XControlInterface():
    def __init__(self, backend="net", socket_hostname="netcom1.sxr.lab", socket_port=2011, com_port="/dev/ttyUSB0", baudrate=9600):
        self.backend = backend
        if backend == "net":
            import socket
            self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.con.connect((socket_hostname, socket_port))
        elif backend == "serial":
            import serial
            self.con = serial.Serial(port=com_port, baudrate=baudrate, timeout=1)
            # mega-dirty-hack
            self.con.recv = self.con.read
            self.con.send = self.con.write
        else:
            print(f"No backend {backend} available!")

    def close(self):
        if self.backend == "net":
            pass
        elif self.backend == "serial":
            self.con.close()

    def _send_raw_command(self, command:CommandList):
        self.con.send(command.value + b'\x0D\x0A')  

    def read_command(self, command: CommandList, repeats: int = 0):
        # firstly send the parameter with the desired command
        self._send_raw_command(command)
        # then expect either positive or negative acknowledge
        response_type = None
        ack_response = False
        iter = 0
        while ack_response is False:
            response_type, ack_response = self._recv_response(RequestType.MNEMONICS)
            if iter == repeats:
                break
            iter+=1
            time.sleep(0.05)
        if response_type == ResponseType.ACKNOWLEDGE and ack_response == True:
            self._send_raw_command(CommandList.ENQUIRY)
            response_type, cmd_response = self._recv_response(RequestType.ENQUIRY)
            if response_type == ResponseType.MEASUREMENT:
                return self._decode_enquiry_response(command, cmd_response)

    def _recv_response(self, request_type:RequestType):
        bytes_msg = b''
        valid_response = False
        response_type = value = None

        while len(bytes_msg) < 1024:
            bytes_msg += self.con.recv(1)
            if bytes_msg[-2:] == b'\x0D\x0A': # valid responce end with <CR><LF>
                valid_response = True
                break
        if valid_response:
            if request_type == RequestType.MNEMONICS:
                response_type = ResponseType.ACKNOWLEDGE
                acknowledge = bytes_msg[0:1] # positive acknowledge
                if acknowledge == b'\x06':
                    value = True
                else: # negative acknowledge or invalid response
                    value = False
            elif request_type == RequestType.ENQUIRY: # positive acknowledge
                response_type = ResponseType.MEASUREMENT
                value = bytes_msg[:-2]
        return response_type, value
    
    def _decode_enquiry_response(self, command:CommandList, data_msg:bytes):
        data_str = data_msg.decode("ascii")
        if data_msg == None:
            return
        if command == CommandList.PRESSURE_ONE:
            status, measurement_value = data_str.split(",")
            if status == "0":
                return float(measurement_value)