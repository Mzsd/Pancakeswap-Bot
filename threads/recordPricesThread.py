from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
from bots import utils
import time

# Record Prices Thread Class some functionalities of price updater thread
class RecordPrices(QThread):

    any_signal = pyqtSignal(dict)

    def __init__(self, items, bot, seconds, parent=None, index=837) -> None:
        super(RecordPrices, self).__init__(parent)
        self.is_running = True
        self.seconds = seconds
        self.index = index
        self.items = items
        self.bot = bot

    def set_binance_config(self, config):
        self.binance_config = config

    def stop(self):
        self.is_running = False
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)

        self.prices =    {
                            'Datetime': [],
                            'Tokens': [],
                            'Price': [],
                            'Binance_Price': [],
                        }

        start = time.time()

        while self.is_running:
            
            self.items
            for item in self.items:
                now = time.time()

                self.bot.set_contract_get_price_func(item.text(), 'BUSD')
                price = self.bot.get_price()

                price_binance, error = utils.get_binance_price( self.bot.contract[2]['SYMBOL'], 
                                                                self.bot.contract[1]['SYMBOL'], 
                                                                self.binance_config)
                    
                while time.time() <= now + 1:
                    True

                self.prices['Datetime'].append(datetime.now())
                self.prices['Tokens'].append(item.text())
                self.prices['Price'].append(price)
                self.prices['Binance_Price'].append(price_binance)
                
                print(f"{datetime.now()}\t{item.text()}\t{price_binance}")

            if time.time() > start + self.seconds:
                self.is_running = False
        
        self.any_signal.emit(self.prices)