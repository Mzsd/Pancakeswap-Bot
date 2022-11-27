from PyQt5.QtCore import QThread, pyqtSignal
from os import stat

import time

# Connector Thread Class
class AccountConnection(QThread):

    any_signal = pyqtSignal(str, str, str)

    def __init__(   self, 
                    parent=None, 
                    index: int=0, 
                    bots: list=None, 
                    addr: str=None, 
                    pkey: str=None):

        super(AccountConnection, self).__init__(parent)
        self.is_running = True
        self.index = index
        self.bots = bots
        self.address = addr
        self.privateKey = pkey

    def stop(self):

        for bot in self.bots:
            bot.disconnect()

        self.any_signal.emit("color: rgb(220, 0, 0);", "Not Connected!", self.address)

        self.is_running = False
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)
        while self.is_running:
            for i in range(len(self.bots)):
                status = self.bots[i].set_address(self.address, self.privateKey)
                if status != True:
                    break

            if status == True:
                status = 'Connected!'
                style = "color: rgb(0, 185, 0);"
            else:
                style = "color: rgb(220, 0, 0);"

            self.any_signal.emit(style, status, self.address)
            time.sleep(20)