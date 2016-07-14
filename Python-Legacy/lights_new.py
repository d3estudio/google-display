#!/usr/bin/env python

import glob, serial, time
from random import randint

class LightController:
    def __init__(self):
        self.timeout = 10
        self.timeout_random = 20
        self.arduino = None
        self.mbed = None
        self.last_command = None
        self.random_time = None
        self.baud_rate = 921600
        self.known_commands = [
            'bone',
            'selfie',
            'viagem',
            'surf',
            'cachorro',
            'academia',
            'amor',
            'trofeu'
        ]

    def close_ports(self):
        print('[close_ports] Performing')
        if self.arduino:
            try:
                self.arduino.close()
            except Exception:
                pass
        if self.mbed:
            try:
                self.mbed.close()
            except Exception:
                pass

    def send_light_index(self, index):
        if self.arduino:
            self.arduino.write('{}'.format(index))
            self.arduino.reset_input_buffer()
            self.arduino.reset_output_buffer()
            print('[send_light_index] Sent value: "{}"'.format(index))

    def perform_loop(self):
        print('[perform_loop] Performing')
        self.last_command = int(time.time())
        self.random_time = int(time.time())
        if not self.arduino or not self.mbed:
            print('[perform_loop] Missing arduino or mbed reference')
            return

        self.arduino.rts = True
        self.arduino.rts = False

        while True:
            command = self.mbed.readline().replace('\n', '').split(': ')
            if len(command) != 2:
                if int(time.time()) - self.random_time >= self.timeout_random:
                    self.random_time = int(time.time())
                    light = str(randint(1, 8))
                    print('[perform_loop] Picked random light. Sending:')
                    self.send_light_index(light)
            else:
                current_command = int(time.time())
                command = command[1].lower()
                print('[perform_loop] Received command: {}'.format(command))
                if self.timeout >= current_command - self.last_command:
                    print('[perform_loop] Skipping due to timeout')
                    continue
                if not command in self.known_commands:
                    print('[perform_loop] Warning: Unknown command {}'.format(command))
                    continue
                self.send_light_index(self.known_commands.index(command) + 1)
                self.last_command = current_command
                self.random_time = current_command

    def enumerate_ports(self):
        return glob.glob('/dev/ttyACM*')

    def attempt_communication(self, device):
        device.write('A')
        return device.readline()

    def execute(self):
        self.mbed = None
        self.arduino = None
        selected = []
        for port in self.enumerate_ports():
            if port in selected:
                continue
            if not self.mbed:
                try:
                    print('[detect_ports] Attempting MBED comm on {}@{}'.format(port, self.baud_rate))
                    device = serial.Serial(port, self.baud_rate, timeout=15)
                    repeat = 3
                    while True:
                        if self.mbed:
                            break
                        result = self.attempt_communication(device)
                        if '[' in result:
                            print('[detect_ports] MBED found at {}'.format(port))
                            device.timeout = 1
                            device.write_timeout = 1 # We don't actually write to the MBED...
                            self.mbed = device
                            break
                        else:
                            if repeat > 0:
                                repeat = repeat - 1
                            else:
                                break
                except (OSError, serial.SerialException):
                    pass

            if not self.arduino:
                try:
                    print('[detect_ports] Attempting Arduino comm on {}@{}'.format(port, self.baud_rate))
                    device = serial.Serial(port, self.baud_rate, timeout=2)
                    repeat = 3
                    while True:
                        if self.arduino:
                            break
                        result = self.attempt_communication(device)
                        if 'arduino' in result:
                            print('[detect_ports] Arduino found at {}'.format(port))
                            device.timeout = 1
                            device.write_timeout = 15
                            self.arduino = device
                            break
                        else:
                            if repeat > 0:
                                repeat = repeat - 1
                            else:
                                break
                except (OSError, serial.SerialException):
                    pass
        try:
            self.perform_loop()
        except Exception as e:
            self.close_ports()
            raise e

if __name__ == '__main__':
    c = LightController()
    while True:
        try:
            c.execute()
        except Exception as e:
            print('Error: {}'.format(e))
