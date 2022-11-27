from PyQt5.QtCore import QThread, pyqtSignal

import time

# Balance Updater Thread Class
class BalanceUpdater(QThread):

    any_signal = pyqtSignal(list)

    def __init__(   self, 
                    parent=None, 
                    index: int=0, 
                    bot=None):

        super(BalanceUpdater, self).__init__(parent)
        self.is_running = True
        self.index = index
        self.bot = bot

    def stop(self):
        self.is_running = False
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)
        while self.is_running:
            time.sleep(0.5)
            balances = self.bot.get_balance()
            self.any_signal.emit(balances)
            time.sleep(2)