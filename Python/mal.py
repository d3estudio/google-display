import threading
import logging

from vars import ANIMATION_DURATION_IN_SECONDS

logger = logging.getLogger('MAL')

class MAL(threading.Thread):
    def __init__(self, mbed, manager):
        threading.Thread.__init__(self)
        self.running = True
        self.failing = False
        self.manager = manager
        self.mbed = mbed
        self.command_map = {
            'bone':     '10000000',
            'selfie':   '01000000',
            'viagem':   '00100000',
            'surf':     '00010000',
            'cachorro': '00001000',
            'academia': '00000100',
            'amor':     '00000010',
            'trofeu':   '00000001',
        }
        self.reset_timer = None

    def stop(self):
        logger.debug('Stopping...')
        self.running = False

    def reset_state(self):
        if self.manager.lal:
            self.manager.lal.force_state('00000000')
        self.reset_timer = None

    def run(self):
        while self.running:
            try:
                command = self.mbed.readline().replace('\n', '').split(': ')
                if len(command) == 2 and self.manager.lal:
                    if self.manager.lal.idle:
                        logger.debug('Lights are idle. Resetting and returning')
                        self.manager.lal.force_state('00000000')
                        continue
                    if self.reset_timer:
                        logger.debug('Skipping request due to ongoing animation')
                        continue
                    command = command[1].lower()
                    logger.debug('Received command: {}'.format(command))
                    if command in self.command_map:
                        self.manager.lal.force_state(self.command_map[command])
                        self.reset_timer = threading.Timer(ANIMATION_DURATION_IN_SECONDS, self.reset_state)
                        self.reset_timer.start()
            except Exception as e:
                logger.error('Faulted:')
                logger.error(e)
                self.failing = True



