from PyQt5.QtCore import QThread, pyqtSignal
from bots import utils
import time

# Amount Change Thread Class
class MessageBox(QThread):

    any_signal = pyqtSignal(str, str)

    def __init__(self, buyLineEdit, sellLineEdit, parent=None, index=101) -> None:
        super(MessageBox, self).__init__(parent)
        self.buyLineEdit = buyLineEdit
        self.sellLineEdit = sellLineEdit
        self.is_running = True
        self.index = index

    def stop(self):
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)

        selling_amount = self.sellLineEdit.text()

        while self.is_running:

            if selling_amount != self.sellLineEdit.text():
                selling_amount = self.sellLineEdit.text()
                self.any_signal.emit(   self.buyLineEdit.text(),
                                        self.sellLineEdit.text())