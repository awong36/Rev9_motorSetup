#!/usr/bin/env python
# heater setup version 1.0
# updates: setup heater parameters
#Program designed by Adrian Wong
import sys, serial, time
import modbus_tk.defines as cst
import modbus_tk.modbus_rtu as modbus_rtu
from CommonFunction import loadSettings, signedInt

def setup():  #communication setup
    #Configure Hardware
    com_port = csvInfo[0]  #For windows
    #com_port = '/dev/ttyO4' #For UART4
    #com_port = '/dev/ttyO2' #For UI using UART2
    #com_port = '/dev/ttyUSB0' #For BB USB port
    baud = 115200
    byte = 8
    par = serial.PARITY_EVEN
    stop = 1
    timeout = 1

    #configure communication settings in serConfig
    master = modbus_rtu.RtuMaster(
        serial.Serial(port=com_port, baudrate=baud, bytesize=byte, parity=par, stopbits=stop, xonxoff=0))
    master.set_timeout(timeout)
    master.set_verbose(True)

    return master

class rev9Config(object):
    sysPath = 'system/'
    motorPIDReg = [300,322,344,366,388,410]

    motRgn91UP = [20,1,1,5,30,1,500,170,700,1000,1000,100,1000,100,5,1000,1000,0,0,1000,700,600]
    motRgn91DN = [20,1,1,2,30,1,500,170,30000,1000,1000,25,1000,1000,5,1000,1000,0,0,1000,700,600]
    motRgn92UP = [20,1,1,2,30,1,500,170,30000,1000,1000,100,1000,100,5,1000,1000,0,0,1000,700,400]
    motRgn92DN = [20,1,1,2,30,1,500,170,30000,1000,1000,100,1000,100,5,1000,1000,0,0,1000,700,600]
    motRgn93UP = [20,1,1,10,50,1,500,200,30000,1000,1000,5,1000,100,5,1000,1000,0,0,1000,700,600]
    motRgn93DN = [20,10,1,50,40,1,500,150,30000,1000,1000,5,1000,100,5,1000,1000,0,0,1000,700,600]

    def setPID(self,master):
        print "Setting PID..."
        for y in range (0,5):
            for x in range(0,21):
                master.execute(1, cst.WRITE_SINGLE_REGISTER, self.motorPIDReg[0]+ x, output_value=self.motRgn91UP[x])
                master.execute(1, cst.WRITE_SINGLE_REGISTER, self.motorPIDReg[1]+ x, output_value=self.motRgn91DN[x])
                master.execute(1, cst.WRITE_SINGLE_REGISTER, self.motorPIDReg[2]+ x, output_value=self.motRgn92UP[x])
                master.execute(1, cst.WRITE_SINGLE_REGISTER, self.motorPIDReg[3]+ x, output_value=self.motRgn92DN[x])
                master.execute(1, cst.WRITE_SINGLE_REGISTER, self.motorPIDReg[4]+ x, output_value=self.motRgn93UP[x])
                master.execute(1, cst.WRITE_SINGLE_REGISTER, self.motorPIDReg[5]+ x, output_value=self.motRgn93DN[x])
        print "PID settings Completed"

    def goHome(self,master):
        temp = master.execute(1, cst.READ_HOLDING_REGISTERS, 25, 1)
        temp = signedInt(temp[0])
        if temp == 5:
            status = 1
        else:
            status = 0
            master.execute(1, cst.WRITE_SINGLE_REGISTER, 25, output_value=0)
            master.execute(1, cst.WRITE_SINGLE_REGISTER, 255, output_value=1)

        while status == 0:
            temp = master.execute(1, cst.READ_HOLDING_REGISTERS, 25, 1)
            temp = signedInt(temp[0])
            if temp == 5:
                status = 1
                print "Homing Completed..."

    def goSetpoint(self,master,x):
        master.execute(1, cst.WRITE_SINGLE_REGISTER, 0, output_value=x)
        print "Moving to Setpoint...%r" %x

def main():
    global instruments
    global csvInfo

    csvInfo = loadSettings(rev9Config.sysPath + 'settings.csv')
    master = setup()

    rev9motor = rev9Config()
    rev9motor.setPID(master)
    rev9motor.goHome(master)

    while True:
        rev9motor.goSetpoint(master,0)
        time.sleep(2)
        rev9motor.goSetpoint(master,-600)
        time.sleep(2)


if __name__ == "__main__":
    main()