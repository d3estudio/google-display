#!/usr/bin/env python
import sys, glob, serial, time
from random import randint

timeout = 20
timeout_random = 20

def control_lights(mbedSerial, arduSerial):
    print('[control_lights] Entrypoint')
    last_command = int(time.time())
    random_time = int(time.time())
    if mbedSerial and arduSerial:
        arduSerial.rts = True
        arduSerial.rts = False
        while True:
            command = mbedSerial.readline().replace('\n','').split(': ')
            if len(command) > 1:
                current_command = int(time.time())
                print('[control_lights] Received: {}'.format(command[1]))
                if current_command - last_command <= timeout:
                    if command[1] == 'BONE':
                        arduSerial.write('1')
                    if command[1] == 'SELFIE':
                        arduSerial.write('2')
                    if command[1] == 'VIAGEM':
                        arduSerial.write('3')
                    if command[1] == 'SURF':
                        arduSerial.write('4')
                    if command[1] == 'CACHORRO':
                        arduSerial.write('5')
                    if command[1] == 'ACADEMIA':
                        arduSerial.write('6')
                    if command[1] == 'AMOR':
                        arduSerial.write('7')
                    if command[1] == 'TROFEU':
                        arduSerial.write('8')
                    arduSerial.reset_input_buffer()
                    arduSerial.reset_output_buffer()
                else:
                    print('[control_lights] Ignored due to timeout')
                last_command = current_command
                random_time = current_command
            else:
                if int(time.time())-random_time >= timeout_random:
                    light = str(randint(1,8))
                    print('[control_lights] Sending random light: {}'.format(light))
                    arduSerial.write(light)
                    random_time = int(time.time())
    else:
        print '[control_lights] ARDUINO OR MBED NOT FOUND'

def serial_ports():
   return glob.glob('/dev/ttyACM*')

def detect_ports():
    mbed = False
    arduino = False
    selected = []
    for port in serial_ports():
        if port in selected:
            continue
        if not mbed:
            try:
                s = serial.Serial(port, 921600, timeout=15)
                print '[detect_ports] MBED: Trying port %s at 921600' % port
                repeat = 3
                while True:
                    s.write('A')
                    line = s.readline()
                    if '[' in line:
                        print '[detect_ports] MBED is on %s' % port
                        selected.append(port)
                        mbed = s
                        mbed.timeout = 1
                        mbed.write_timeout = 1
                        break
                    else:
                        if repeat > 0:
                            repeat = repeat - 1
                        else:
                            break
                if mbed:
                    continue
            except (OSError, serial.SerialException):
                pass
        if not arduino:
            try:
                s = serial.Serial(port,921600,timeout=1)
                print '[detect_ports] ARDUINO: Trying port %s at 921600' % port
                repeat = 3
                while True:
                    s.write('A')
                    line = s.readline()
                    if 'arduino' in line:
                        print '[detect_ports] ARDUINO is on %s' % port
                        arduino = s
                        arduino.timeout = 1
                        arduino.write_timeout = 15
                        break
                    else:
                        if repeat > 0:
                            repeat = repeat - 1
                        else:
                            break
                if arduino:
                    continue
            except (OSError, serial.SerialException):
                pass
    try:
        control_lights(mbed, arduino)
    except Exception as e:
        print('[detect_ports] control_lights faulted: {}'.format(e))
        try:
            arduino.close()
        except Exception:
            pass
        try:
            mbed.close()
        except Exception:
            pass
        raise e

if __name__ == '__main__':
    while True:
        try:
            detect_ports()
        except Exception as e:
            print('Error: {}'.format(e))
