from PyQt5.QtCore import QThread, pyqtSignal
from bots import utils
import time

# Max Value Thread Class
class MaxValue(QThread):

    any_signal = pyqtSignal(float)

    def __init__(self, exchangeComboBox, bot, parent=None, index=33) -> None:
        super(MaxValue, self).__init__(parent)
        self.exchangeComboBox = exchangeComboBox
        self.index = index
        self.bot = bot

    def stop(self):
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)
        token_name = str(self.exchangeComboBox.currentText())
        now = time.time()
        balances = self.bot.get_balance()
        print(f"Getting Balance took: {time.time()-now}s")
        token = utils.search_token(token_name, self.bot.tokens)

        amount = balances[self.exchangeComboBox.currentIndex()]

        self.any_signal.emit(   (   amount - 0.01 
                                    if amount - 0.01 >=0 
                                    else 0.0
                                )
                                if token['ADDRESS'] == self.bot.router.functions.WETH().call()
                                else 0.0
                                if amount == '-'
                                else amount)