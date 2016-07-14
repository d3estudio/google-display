import threading
import logging
import struct
import collections
from vars import ANIMATION_DELAY_IN_SECONDS, IDLE_DELAY_IN_SECONDS, COMMAND_IDENTIFY, COMMAND_GET_STATE, COMMAND_SET_STATE

logger = logging.getLogger('LAL')

class LAL(threading.Thread):
    def __init__(self, arduino, manager):
        threading.Thread.__init__(self)
        self.failing = False
        self.running = True
        self.manager = manager
        self.arduino = arduino
        self.state = 0
        self.idle_animation = [
            '00000000',
            '10000001',
            '01000010',
            '00100100',
            '00011000',
            '11111111',
        ]
        self.animation_queue = collections.deque()
        self.timer = None
        self.idle_timer = None
        self.idle = False

    def stop(self):
        logger.debug('Stopping...')
        self.running = False
        self.animation_queue.clear()

    def write(self, data):
        try:
            self.arduino.write(data)
        except Exception as e:
            logger.error('Faulted:')
            logger.error(e)
            self.failing = True

    def enqueue_animation(self):
        logger.debug('Enqueuing animation')
        self.animation_queue.extend(self.idle_animation)

    def run(self):
        self.timer = threading.Timer(ANIMATION_DELAY_IN_SECONDS, self.loop)
        self.timer.start()
        self.restart_idle_timer()
        logger.debug('Thread started')

    def loop(self):
        next_step = None
        try:
            next_step = self.animation_queue.pop()
        except IndexError:
            pass
        if next_step:
            self.set_state(next_step)
            self.idle = True
        if self.running:
            self.timer = threading.Timer(ANIMATION_DELAY_IN_SECONDS, self.loop)
            self.timer.start()

    def get_state(self):
        self.write(COMMAND_GET_STATE)
        result = self.arduino.read(1)
        logger.debug('Get state result: {:02X}'.format(ord(result)))

    def identify(self):
        self.write(COMMAND_IDENTIFY)
        result = self.arduino.read(1)
        logger.debug('Identification result: {:02X}'.format(ord(result)))

    def send_state(self):
        self.write(COMMAND_SET_STATE)
        self.write(struct.pack(">B", self.state))
        self.restart_idle_timer()
        logger.debug('Wrote state: {:02X}'.format(self.state))

    def restart_idle_timer(self):
        if self.idle_timer:
            self.idle_timer.cancel()
        if self.running:
            self.idle_timer = threading.Timer(IDLE_DELAY_IN_SECONDS, self.enqueue_animation)
            self.idle_timer.start()

    def force_state(self, value):
        logger.debug('Forcing state: {}'.format(value))
        self.animation_queue.clear()
        self.set_state(value)
        self.restart_idle_timer()
        self.idle = False

    def set_state(self, value):
        if len(value) < 1:
            return

        result = 0x0
        offsets = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]
        for i in xrange(0, min(len(value), 8)):
            if value[i] == '1':
                result = result | offsets[i]
        self.state = result
        self.send_state()
