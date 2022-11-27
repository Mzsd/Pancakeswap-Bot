from PyQt5.QtCore import QThread, pyqtSignal
from bots import utils

import time

# Amount Change Thread Class
class SwapTokens(QThread):

    any_signal = pyqtSignal(str, str, str)

    def __init__(self, token0, token1, amount, bot, parent=None, index=89) -> None:
        super(SwapTokens, self).__init__(parent)
        self.complete = False
        self.token0 = token0
        self.token1 = token1
        self.amount = amount
        self.index = index
        self.bot = bot

    def stop(self):
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)

        tx_hash = ''
        # Counters
        status_counter = 0
        swap_counter = 0

        if self.token0['ADDRESS'] == self.token1['ADDRESS']:
            
            # If token swap is eth to weth or vice versa <- if condition
            if self.token0['MAIN_TOKEN']:
                tx_hash = self.bot.deposit_withdraw(self.amount, self.token1['SYMBOL'])
            elif self.token1['MAIN_TOKEN']:
                tx_hash = self.bot.deposit_withdraw(self.amount, self.token0['SYMBOL'], False)
            else:
                # Print cant swap if both address are same and not weth to eth or vice versa
                print("Both address are same")

            print('tx:', tx_hash)

        else:
            if self.bot.token_approval(self.token0):

                now = time.time()
                approve_tx_hash = self.bot.approve_token(self.token0)
                print('approve_tx:', approve_tx_hash)
                while True:

                    if status_counter > 1000:
                        print("Approval Transaction Failed:  Counter Exceeded!")
                        break

                    try:
                        status_counter += 1
                        transaction_rec = self.bot.w3.eth.getTransactionReceipt(approve_tx_hash)
                    except Exception as e:
                        continue

                    status = dict(transaction_rec)['status']
                    print('status:', dict(transaction_rec)['status'])
                    if status:
                        break

                print(f"It took {time.time() - now}s to approve the token!")

            print("Sleeping for 1 sec....")
            time.sleep(1)
            tx_hash = self.bot.swap_tokens( self.token0,
                                            self.token1,
                                            self.amount,
                                            float(self.token0['SLIPPAGE']) / 100)

            print('tx:', tx_hash)

        # Logging to check if transaction succeeded or not
        if tx_hash:
            while True:
                if swap_counter > 1000:
                    print("Transaction Failed: Counter Exceeded!")
                    break

                try:
                    swap_counter += 1
                    transaction_rec = self.bot.w3.eth.getTransactionReceipt(tx_hash)
                except Exception as e:
                    continue

                status = dict(transaction_rec)['status']
                print('status:', dict(transaction_rec)['status'])

                tx_status = "Successful Transaction" if status else "Failed Transaction"
                print(tx_status)
                break
        
        self.any_signal.emit(tx_hash, self.bot.address, tx_status)