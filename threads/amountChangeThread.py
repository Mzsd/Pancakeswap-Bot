from PyQt5.QtCore import QThread, pyqtSignal
from bots import utils
import time

# Amount Change Thread Class
class AmountChange(QThread):

    any_signal = pyqtSignal(float)

    def __init__(self, exchangeBuyLineEdit,  bot, parent=None, index=42) -> None:
        super(AmountChange, self).__init__(parent)
        self.exchangeBuyLineEdit = exchangeBuyLineEdit
        self.is_running = True
        self.index = index
        self.bot = bot
        
    def stop(self):
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)
        first = True
        
        while True:
            time.sleep(1)
            if self.exchangeBuyLineEdit.isEnabled():
                break

        while self.is_running:

            price = self.bot.get_price()

            if self.bot.get_price() != price or first:
                price = self.bot.get_price()
                self.any_signal.emit(   float(self.exchangeBuyLineEdit.text()) * price
                                        if not type(price) == str
                                        else
                                        0.0)
                first = False