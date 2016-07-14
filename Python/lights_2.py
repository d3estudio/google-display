#!/usr/bin/env python
import serial
import time
import traceback
import glob
import sys
import signal
import logging

from lal import LAL
from mal import MAL
from log_utils import ColorLoggingHandler
from vars import TIMEOUT, TIMEOUT_RANDOM, MBED_BAUD_RATE, ARDUINO_BAUD_RATE


root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)

handler = ColorLoggingHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
root_logger.addHandler(handler)

logger = logging.getLogger('Main')

class LightsManager:
    def __init__(self):
        self.arduino = None
        self.mbed = None
        self.lal = None
        self.mal = None
        self.running = True
        logger.info('Attaching signal traps')
        signal.signal(signal.SIGINT, self.received_sigstop)
        signal.signal(signal.SIGTERM, self.received_sigstop)


    def disconnect_devices(self):
        if self.arduino:
            try:
                logger.debug('Disconnecting Arduino')
                self.arduino.close()
            except Exception:
                pass
        if self.mbed:
            try:
                logger.debug('Disconnecting MBED')
                self.mbed.close()
            except Exception:
                pass
        if self.lal:
            self.lal.stop()
        if self.mal:
            self.mal.stop()
        self.arduino = None
        self.mbed = None
        self.lal = None
        self.mal = None

    def find_device_ports(self):
        return {
            'arduino': glob.glob('/dev/ttyUSB*'),
            'mbed': glob.glob('/dev/ttyACM*'),
        }

    def perform_loop(self):
        logger.debug('Performing')
        if not self.arduino or not self.mbed:
            logger.warning('[perform_loop]     Missing MBED or Arduino device.')
            return
        while self.running:
            time.sleep(0.5)
            if self.mal and self.mal.failing:
                logger.warning('MAL reported failure. Returning...')
                return
            if self.lal and self.lal.failing:
                logger.warning('LAL reported failure. Returning...')
                return
        logger.info('Runtime loop was broken.')

    def detect_devices(self):
        self.disconnect_devices()
        ports = self.find_device_ports()
        valid = True
        if len(ports['arduino']) < 1:
            logger.warning('Cannot find possible Arduino port.')
            valid = False
            return
        if len(ports['mbed']) < 1:
            logger.warning('Cannot find possible MBED port.')
            valid = False

        if not valid:
            logger.info('Sleeping 2000ms')
            time.sleep(2)
            return False

        if not self.mbed:
            for port in ports['mbed']:
                try:
                    logger.debug('MBED connection attempt @ {}'.format(port))
                    dev = serial.Serial(port, MBED_BAUD_RATE, timeout=15)
                    for attempt in xrange(1, 4):
                        logger.debug('Readline attempt #{}'.format(attempt))
                        output = dev.readline()
                        if '[' in output:
                            logger.debug('Found MBED on {}'.format(port))
                            self.mbed = dev
                            self.mbed.timeout = 1
                            self.mbed.write_timeout = 1 # Erm, we are not actually writing to the MBED :B
                            self.mal = MAL(self.mbed, self)
                            self.mal.start()
                            break
                        logger.debug('Failed.')
                except (OSError, serial.SerialException):
                    pass
                if self.mbed:
                    break

        if not self.arduino:
            for port in ports['arduino']:
                try:
                    logger.debug('Arduino connection attempt @ {}'.format(port))
                    dev = serial.Serial(port, ARDUINO_BAUD_RATE, timeout=1)
                    for attempt in xrange(1, 4):
                        logger.debug('Readline attempt #{}'.format(attempt))
                        dev.write("\x20")
                        output = dev.read(1)
                        if 'A' in output:
                            logger.debug('Found Arduino on {}'.format(port))
                            self.arduino = dev
                            self.arduino.timeout = 1
                            self.arduino.write_timeout = 15
                            self.arduino.rts = True
                            self.arduino.rts = False
                            self.lal = LAL(self.arduino, self)
                            self.lal.identify()
                            self.lal.start()
                            break
                except (OSError, serial.SerialException):
                    pass
                if self.arduino:
                    break
        return True

    def received_sigstop(self, signum, frame):
        signal.signal(signum, signal.getsignal(signum))
        logger.info('Caught external INTERRUPT signal.')
        logger.info('Wait until threads are stopped...')
        if self.lal:
            self.lal.stop()
        if self.mal:
            self.mal.stop()
        sys.exit(0)


if __name__ == '__main__':
    c = LightsManager()
    while c.running:
        try:
            c.detect_devices()
            c.perform_loop()
        except Exception as e:
            logger.error('Routine faulted: {}'.format(e))
            logger.error(traceback.format_exc())
