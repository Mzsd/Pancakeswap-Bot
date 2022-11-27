from datetime import datetime
import pandas as pd
import os

class ThreadConnector():

    # Stub Function
    def update(self, any_signal):
        pass
    
    # Stops running thread
    def stop_thread(self):
        self.thread.stop()


class SimpleThreadConnector(ThreadConnector):

    def start_thread(self, thread):
    
        self.thread = thread
        self.thread.setTerminationEnabled(True)
        self.thread.start()
        self.thread.any_signal.connect(self.update)


class ComplexThreadConnector(ThreadConnector):

    def start_thread(self, thread):
        if self.checkBox.isChecked():
                
            # Terminate thread if it is running already
            try:
                if self.thread.isRunning():
                    print("Thread stopping...............", self.thread.index)
                    self.thread.stop()
            except Exception:
                pass
            
            self.thread = thread
            self.thread.setTerminationEnabled(True)
            self.thread.start()
            self.thread.any_signal.connect(self.update)
        
        else:
            self.thread.stop()


class AmountSliderThreadConnector(SimpleThreadConnector):
    
    def update(self):
        pass


# Grab prices of stated prices
class RecordPricesThreadConnector(SimpleThreadConnector):

    def __init__(self, recordButton, seconds):
        self.recordButton = recordButton
        self.seconds = seconds

    def update(self, prices):
        
        prices_df = pd.DataFrame(prices)
        # time_string = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")

        folder = 'price_records'
        folder_path = os.path.join(os.getcwd(), folder)
        record_folder = f"{prices_df['Datetime'].iloc[0].strftime('%Y-%m-%d')}"
        record_folder_path = os.path.join(folder_path, record_folder)
        filename = f"{prices_df['Datetime'].iloc[0].strftime('%Y-%m-%dT%H%M%S')}_{self.seconds}_seconds.csv"
        filename_path = os.path.join(record_folder_path, filename)

        if not os.path.exists(folder_path):
            os.mkdir(folder)

        if not os.path.exists(record_folder_path):
            os.mkdir(record_folder_path)

        prices_df.to_csv(filename_path, index=None)
        self.recordButton.setEnabled(True)
        self.stop_thread()


# Connects with swap exchange thread
# Might run multiple threads for transfer of profit
class RunBotThreadConnector(SimpleThreadConnector):
    
    def __init__(self):
        pass
        

class LineEditThreadConnector(SimpleThreadConnector):
    def __init__(self, lineEdit):
        self.lineEdit = lineEdit

    def update(self, amount):
        self.lineEdit.setText(str(amount))


class MessageBoxThreadConnector(SimpleThreadConnector):

    def __init__(self, messageBox, comboBox_1, comboBox_2):
        self.messageBox = messageBox
        self.comboBox_1 = comboBox_1
        self.comboBox_2 = comboBox_2

    def update(self, buyLineEdit, sellLineEdit):
        self.messageBox.setText(    f"Are you sure you want to swap {buyLineEdit} " + \
                                    f"{self.comboBox_1.currentText()} " + \
                                    f"for {sellLineEdit} " + \
                                    f"{self.comboBox_2.currentText()}?")


class SwapTokensThreadConnector(SimpleThreadConnector):
    
    # WIP
    # Add transaction to account log file
    def update(self, amount, address, tx_status):
        
        # WIP

        self.stop_thread()
    

class BalanceUpdaterThreadConnector(ComplexThreadConnector):

    def __init__(self, labels, checkBox):
        super().__init__()
        self.labels = labels
        self.checkBox = checkBox

    def update(self, balances):
        for k, bal_label in enumerate(self.labels):
            self.labels[bal_label][1].setText(  "{:.8f}".format(round(balances[k], 8))
                                                if type(balances[k]) != str else balances[k])


class AccountConnectionThreadConnector(ComplexThreadConnector):

    def __init__(self, addressLabel, statusLabel, checkBox):
        super().__init__()
        self.addressLabel = addressLabel
        self.statusLabel = statusLabel
        self.checkBox = checkBox

    # Update connection label with connector thread
    def update(self, style, status, address):
        # print(style, status, address)
        self.statusLabel.setText(str(status))
        self.statusLabel.setStyleSheet(style)
        self.addressLabel.setText(str(address))


class AmountChangeTheadConnector(LineEditThreadConnector):

    def update(self, amount):
        self.lineEdit.setText(str(amount))
        

class MaxValueThreadConnector(LineEditThreadConnector):

    def is_max_button_unlocked(self):
        return True if self.lineEdit.isEnabled() else False
            
    def update(self, amount):
        self.lineEdit.setText(str(amount))
        self.stop_thread()