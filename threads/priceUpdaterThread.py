
from binance.exceptions import BinanceAPIException
from requests.exceptions import ConnectionError
from PyQt5.QtCore import QThread, pyqtSignal
from binance.client import Client
from bots import utils

import time

# Price Updater Thread Class
class PriceUpdater(QThread):

    # For Debug
    object_id=None

    any_signal = pyqtSignal(int)
    updatedPrice = pyqtSignal(float, str)

    def __init__(self, parent=None, index=0) -> None:
        super(PriceUpdater, self).__init__(parent)
        # self.price_label = None
        self.is_running = True
        self.index = index
        self.bot = None

    def set_object_id(self, object_id):
        self.object_id = object_id

    def set_binance_config(self, config):
        self.binance_config = config

    def set_bot(self, bot):
        self.bot = bot

    def stop(self):
        self.is_running = False
        print('Stopping thread...', self.index)

        # Debug code to check if thread is being destroyed or not
        if self.object_id:
            print(self.object_id)
        print()
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)
        error = True

        while self.is_running:
            price = self.bot.get_price()

            price_binance, error = utils.get_binance_price( self.bot.contract[1]['SYMBOL'], 
                                                            self.bot.contract[2]['SYMBOL'], 
                                                            self.binance_config,
                                                            error)

            if type(price) != str:
                self.updatedPrice.emit(price, price_binance)
            else:
                self.errorStr = price
                self.updatedPrice.emit(-1, price_binance)

            time.sleep(1)