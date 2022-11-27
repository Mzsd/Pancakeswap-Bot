import styleSheet
import time
import json
import sys
import os

# PyQt5 Imports
from PyQt5.QtWidgets import (
    QApplication,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QGridLayout,
    QHBoxLayout,
    QPushButton,
    QSpacerItem,
    QMainWindow,
    QSizePolicy,
    QComboBox,
    QToolTip,
    QLayout,
    QDialog, 
    QWidget,
    QLabel,
)

from PyQt5.QtGui import (
    # QStyleOptionSlider,
    QDoubleValidator,
    QCloseEvent,
    QCursor,
    # QStyle,
)

from PyQt5.uic import loadUi

# PyQT5 Thread Imports
from threads.accountConnectionThread import AccountConnection
from threads.balanceUpdaterThread import BalanceUpdater
from threads.amountChangeThread import AmountChange
from threads.amountSliderThread import AmountSlider
from threads.priceUpdaterThread import PriceUpdater
from threads.recordPricesThread import RecordPrices
from threads.swapTokensThread import SwapTokens
from threads.messageBoxThread import MessageBox
from threads.maxValueThread import MaxValue
from threads.runBotThread import RunBot

# Thread Connectors -- For reusabilty
from threads.threadConnectors import (
    AccountConnectionThreadConnector,
    BalanceUpdaterThreadConnector,
    AmountSliderThreadConnector,
    RecordPricesThreadConnector,
    AmountChangeTheadConnector,
    MessageBoxThreadConnector,
    SwapTokensThreadConnector,
    MaxValueThreadConnector,
    RunBotThreadConnector
)

# Bot imports
from bots import utils
from bots.cake_bot import Bot


EXCHANGE = "pancakeswap"
PATH = os.path.join(os.getcwd(), 'gui_design')
BOTS = 5 # + 1 # 1 <- is for only swapping tokens
TOKENS_LIST = []


def helper_func():
    with open(utils.get_path(['assets', 'pancakeswap', 'tokens.json'])) as fp:
        global TOKENS_LIST
        TOKENS_LIST += [t['SYMBOL'] for t in json.load(fp)]


class MainForm(QMainWindow):

    def __init__(self):
        super(MainForm, self).__init__()

        loadUi(PATH + '\main.ui', self)
        self.set_variables()
        self.show()

    def open_form(self, name):
        
        self.hide()
        ExchangeForm(self).show()

    def set_variables(self):
        
        # PancakeSwap
        self.exchangeButton_1.clicked.connect(lambda name="pancakeswap" :self.open_form(name))

        # ParaSwap
        self.exchangeButton_2.clicked.connect(lambda name="paraswap" :self.open_form(name))


class ExchangeForm(QMainWindow):

    def __init__(self, parent=None):

        super(ExchangeForm, self).__init__(parent)
        loadUi(PATH + f'\{EXCHANGE.lower()}.ui', self)
        self.setFixedSize(self.size().width(), self.size().height())

        # Stub list of bot objects and threads
        self.bots = []
        self.threads = [None] * BOTS
        self.exchangethread = None

        self.set_variables()
    
    def set_variables(self):
        # self.set_tokens_groupBox() Depracated
        self.set_widgets()
        self.set_bots()
        self.set_combo_boxes()

        ### Group Boxes and there features
        #
        #
        self.set_bots_groupBox()
        self.set_exchange_groupBox()
        self.set_balance_groupBox()
        self.set_accounts_groupBox()
        self.set_prices_record_groupBox()
        #
        #
        ### END
        self.set_menu_bar()

    def set_widgets(self):

        # lists of Widgets
        self.combo_boxes = [(getattr(self, f"comboBox_{i*2+1}"), 
                            getattr(self, f"comboBox_{i*2+2}")) for i in range(BOTS)]
        self.price_labels = [getattr(self, f"priceLabel_{i+1}") for i in range(BOTS)]
        self.price_bin_labels = [getattr(self, f"priceBinLabel_{i+1}") for i in range(BOTS)]
        self.pair_labels = [getattr(self, f"pairLabel_{i+1}") for i in range(BOTS)]
        self.amount_labels = [getattr(self, f"amountLabel_{i+1}") for i in range(BOTS)]
        self.progressbar = [getattr(self, f"horizontalSlider_{i+1}") for i in range(BOTS)]
        self.amountLineEdit = [getattr(self, f"amountLineEdit_{i+1}") for i in range(BOTS)]
        self.startBotButton = [getattr(self, f"startBotButton_{i+1}") for i in range(BOTS)]
        self.stoplossLineEdit = [getattr(self, f"stoplossLineEdit_{i+1}") for i in range(BOTS)]
        self.buyLineEdit = [getattr(self, f"buyLineEdit_{i+1}") for i in range(BOTS)]
        self.sellLineEdit = [getattr(self, f"sellLineEdit_{i+1}") for i in range(BOTS)]
        self.walletLineEdit = [getattr(self, f"walletLineEdit_{i+1}") for i in range(BOTS)]
        self.profitSpinBox = [getattr(self, f"profitSpinBox_{i+1}") for i in range(BOTS)]

        # List of progress bar buttons
        self.oneFourthButton = [getattr(self, f"oneFourthButton_{i+1}") for i in range(BOTS)]
        self.twoFourthButton = [getattr(self, f"twoFourthButton_{i+1}") for i in range(BOTS)]
        self.threeFourthButton = [getattr(self, f"threeFourthButton_{i+1}") for i in range(BOTS)]
        self.fourFourthButton = [getattr(self, f"fourFourthButton_{i+1}") for i in range(BOTS)]

        # Set validators
        for i in range(BOTS):
            self.stoplossLineEdit[i].setValidator(QDoubleValidator())
            self.amountLineEdit[i].setValidator(QDoubleValidator())
            self.sellLineEdit[i].setValidator(QDoubleValidator())
            self.buyLineEdit[i].setValidator(QDoubleValidator())


    # To open other windows
    def open_form(self, form):
        self.actionConnect.setEnabled(False)
        form.show()

    def set_menu_bar(self):
        self.actionConnect.triggered.connect(lambda: self.open_form(ConnectForm(self)))

    ### Message Boxes
    #
    #
    def create_swap_message_box(self):

        self.exchange_message_box = QMessageBox(self)
        self.exchange_message_box.setStyleSheet(styleSheet.message_box_styleSheet)

        self.exchange_message_box.setIcon(QMessageBox.Question)
        self.exchange_message_box.setText(  f"Are you sure you want to swap {self.exchangeBuyLineEdit.text()} " + \
                                            f"{self.exchangeComboBox_1.currentText()} " + \
                                            f"for {self.exchangeSellLineEdit.text()} " + \
                                            f"{self.exchangeComboBox_2.currentText()}?")

        yes_button = self.exchange_message_box.addButton(QMessageBox.Yes)
        yes_button.setMinimumWidth(50)
        yes_button.setMinimumHeight(25)

        no_button = self.exchange_message_box.addButton(QMessageBox.No)
        no_button.setMinimumWidth(50)
        no_button.setMinimumHeight(25)

        self.exchange_message_box.layout().setSizeConstraint(QLayout.SetFixedSize)

    def create_bot_message_box(self, message):
        self.bot_message_box = QMessageBox(self)
        self.bot_message_box.setStyleSheet(styleSheet.message_box_styleSheet)
        self.bot_message_box.setIcon(QMessageBox.Critical)
        self.bot_message_box.setText(message)

        ok_button = self.bot_message_box.addButton(QMessageBox.Ok)
        ok_button.setMinimumWidth(50)
        ok_button.setMinimumHeight(25)
    #
    #
    ### END
    
    # Get binance api key from config.json
    def get_binance_config(self):
        path = utils.get_path(['assets', 'binance', 'config.json'])
        with open(path) as f:
            config = json.load(f)

        return config

    # SETS PRICES IN GUI -- BE CAREFUL WHEN EDITING
    # Threading error - they are not closing as parent class is alive
    def set_bots_groupBox(self):

        #--------------------------- Set Prices ---------------------------#

        def update_price_label(price, price_binance):
            index = self.sender().index

            # Flip price for display purposes only
            if price >= 0:
                self.price_labels[index].setText(str(1 / price))
            else:
                self.price_labels[index].setText(str(self.sender().errorStr))

            self.price_bin_labels[index].setText(price_binance)

            if price_binance == '-':
                self.price_labels[index].setStyleSheet("color: rgb(255, 255, 255);")
                self.price_bin_labels[index].setStyleSheet("color: rgb(255, 255, 255);")
            if price == '-':
                self.price_labels[index].setStyleSheet("color: rgb(255, 255, 255);")
                self.price_bin_labels[index].setStyleSheet("color: rgb(255, 255, 255);")

            if not price == '-' and not price_binance == '-':
                if float(price_binance) > (1 / price):
                    self.price_labels[index].setStyleSheet("color: rgb(0, 185, 0);") # Green
                    self.price_bin_labels[index].setStyleSheet("color: rgb(255, 10, 10);") # Red
                elif float(price_binance) < (1 / price):
                    self.price_labels[index].setStyleSheet("color: rgb(255, 10, 10);") # Red
                    self.price_bin_labels[index].setStyleSheet("color: rgb(0, 185, 0);") # Green

        def update(index, first):
            print("Update value...", index)
            print(index)

            self.bots[index].set_contract_get_price_func(str(self.combo_boxes[index][1].currentText()), 
                                                            str(self.combo_boxes[index][0].currentText())
                                                            )

            if first[index]:
                self.threads[index] = PriceUpdater(parent=None, index=index)
                self.threads[index].set_binance_config(self.binance_config)
                self.threads[index].set_object_id(id(self.threads[index]))
                self.threads[index].start()

                # AmountSliderConnectorThread and AmountSlider thread Initialization 
                # for each slider and amount textbox.
                self.amountSliderThreadConnector[index].start_thread(AmountSlider(  self.bal_labels,
                                                                                    self.amountLineEdit[index],
                                                                                    self.progressbar[index],
                                                                                    self.price_labels[index],
                                                                                    self.bots[index]))

                # Enable progress bar 
                self.progressbar[index].setEnabled(True)
                first[index] = False

            self.threads[index].set_bot(self.bots[index])
            self.threads[index].updatedPrice.connect(update_price_label)

            amount_in_str = self.bal_labels[str(self.combo_boxes[index][1].currentText())][1].text()
            amount = float('0' if amount_in_str == '-' else amount_in_str)
            self.amount_labels[index].setText(f'{amount} {str(self.combo_boxes[index][1].currentText()).upper()}')

        #--------------------------- END ---------------------------#

        #--------------------------- Run Bot ---------------------------#

        def start_bot(index):

            if self.startBotButton[index].text() == 'Start Bot':
                
                # Creates a messagebox if any textbox is left empty
                # could be further optimized
                message = " is missing!"
                if self.amountLineEdit[index].text() == '':
                    self.create_bot_message_box(f"Amount{message}")
                    self.bot_message_box.exec_()
                    return
                elif self.stoplossLineEdit[index].text() == '':
                    self.create_bot_message_box(f"Stop loss{message}")
                    self.bot_message_box.exec_()
                    return
                elif self.buyLineEdit[index].text() == '':
                    self.create_bot_message_box(f"Buy price{message}")
                    self.bot_message_box.exec_()
                    return
                elif self.sellLineEdit[index].text() == '':
                    self.create_bot_message_box(f"Sell price{message}")
                    self.bot_message_box.exec_()
                    return
                    
                self.runBotThreadConnector = RunBotThreadConnector()

                self.runBotThreadConnector.start_thread(RunBot  (
                                                                    [
                                                                        self.amountLineEdit[index],
                                                                        self.stoplossLineEdit[index],
                                                                        self.buyLineEdit[index],
                                                                        self.sellLineEdit[index],
                                                                        self.walletLineEdit[index],
                                                                        self.profitSpinBox[index],
                                                                    ],
                                                                    str(self.combo_boxes[index][1].currentText()),  # Token1
                                                                    str(self.combo_boxes[index][0].currentText()),  # Token0
                                                                    self.bots[index],
                                                                    index,
                                                                )
                                                        )

                # Changes text to stop bot
                self.startBotButton[index].setText('Stop Bot')
                self.startBotButton[index].setStyleSheet(styleSheet.stop_bot_styleSheet)

                # Disables all the textbox so they cant be interacted with while
                # bot is running.
                self.stoplossLineEdit[index].setEnabled(False)
                self.walletLineEdit[index].setEnabled(False)
                self.amountLineEdit[index].setEnabled(False)
                self.profitSpinBox[index].setEnabled(False)
                self.sellLineEdit[index].setEnabled(False)
                self.progressbar[index].setEnabled(False)
                self.buyLineEdit[index].setEnabled(False)

                self.combo_boxes[index][0].setEnabled(False)
                self.combo_boxes[index][1].setEnabled(False)
            else:
                
                self.runBotThreadConnector.stop_thread()

                # Changes text to start bot
                self.startBotButton[index].setText('Start Bot')
                self.startBotButton[index].setStyleSheet(styleSheet.start_bot_styleSheet)

                # Enables all the textbox
                self.stoplossLineEdit[index].setEnabled(True)
                self.walletLineEdit[index].setEnabled(True)
                self.amountLineEdit[index].setEnabled(True)
                self.profitSpinBox[index].setEnabled(True)
                self.sellLineEdit[index].setEnabled(True)
                self.progressbar[index].setEnabled(True)
                self.buyLineEdit[index].setEnabled(True)

                self.combo_boxes[index][0].setEnabled(True)
                self.combo_boxes[index][1].setEnabled(True)

        #--------------------------- END ---------------------------#

        #--------------------------- Progress Bar | Set Prices | Run Bot ---------------------------#

        def update_amount_progressbar(index, value):
            self.progressbar[index].setValue(value)

            from_token = self.bots[index].contract[1]['SYMBOL']
            amount_in_str = self.bal_labels[from_token][1].text()
            price = 1 / float(self.price_labels[index].text()) if self.price_labels[index].text() != '-' else 0.0
            amount = float('0' if amount_in_str == '-' else amount_in_str) * price

            try:
                self.amountLineEdit[index].setText(str(amount * (value / 100)))
            except ZeroDivisionError:
                self.amountLineEdit[index].setText(str(0))

        # Variable for prices - First time change in prices -> To start the
        first = [True] * BOTS

        self.amountSliderThreadConnector = list()
        
        self.binance_config = self.get_binance_config()

        for i in range(3):
            
            # Create progressbar thread and thread connector
            self.amountSliderThreadConnector.append(AmountSliderThreadConnector())

            # Set progress bar buttons to set progress bar to 25, 50, 75 or 100
            self.oneFourthButton[i].clicked.connect(lambda checked, i=i:    update_amount_progressbar(i, 25)
                                                                            if self.progressbar[i].isEnabled() == True 
                                                                            else None)
            self.twoFourthButton[i].clicked.connect(lambda checked, i=i:    update_amount_progressbar(i, 50) 
                                                                            if self.progressbar[i].isEnabled() == True 
                                                                            else None)
            self.threeFourthButton[i].clicked.connect(lambda checked, i=i:  update_amount_progressbar(i, 75)
                                                                            if self.progressbar[i].isEnabled() == True 
                                                                            else None)
            self.fourFourthButton[i].clicked.connect(lambda checked, i=i:   update_amount_progressbar(i, 100)
                                                                            if self.progressbar[i].isEnabled() == True 
                                                                            else None)

            self.combo_boxes[i][0].currentIndexChanged.connect(lambda checked, index=i: update(index, first))
            self.combo_boxes[i][1].currentIndexChanged.connect(lambda checked, index=i: update(index, first))
            
            # Start/Stop bot
            self.startBotButton[i].clicked.connect(lambda checked, i=i: start_bot(i))

        #--------------------------- END ---------------------------#

    def set_exchange_groupBox(self):
        
        #--------------------------- Exchange ---------------------------#

        # For exchange only
        # Declaring exchange bot (No botting here, just plain old swapping)
        self.exchange_bot = Bot(utils.load_setting('pancakeswap'))
        
        # To allow only double
        self.exchangeBuyLineEdit.setValidator(QDoubleValidator())
        self.exchangeSellLineEdit.setValidator(QDoubleValidator())

        self.exchangeComboBox_1.clear()
        self.exchangeComboBox_2.clear()
        self.exchangeComboBox_1.addItems(TOKENS_LIST)
        self.exchangeComboBox_2.addItems(TOKENS_LIST)

        def update_price_label(price, price_binance):
            index = self.sender().index
            if price >= 0: 
                self.exchangePriceLabel.setText(str(price) + 
                                                " " +
                                                str(self.exchangeComboBox_2.currentText()).upper() +
                                                " per " +
                                                str(self.exchangeComboBox_1.currentText()).upper())
                
            else:
                self.exchangePriceLabel.setText(str(self.sender().errorStr))


        def update(index, first):
            print("Update value...", index)

            # Enable both buy and sell textboxes
            self.exchangeBuyLineEdit.setEnabled(True)
            self.exchangeSellLineEdit.setEnabled(True)

            # Chane buy and sell edit textbox if there is now value
            if self.exchangeBuyLineEdit.text() == '': 
                self.exchangeBuyLineEdit.setText("0.0")

            if self.exchangeSellLineEdit.text() == '':    
                self.exchangeSellLineEdit.setText("0.0")

            # Enable swap button if both tokens are different
            if self.exchangeComboBox_1.currentIndex() != self.exchangeComboBox_2.currentIndex():
                self.swapButton.setEnabled(True)
            else:
                self.swapButton.setEnabled(False)

            self.exchange_bot.set_contract_get_price_func(  str(self.exchangeComboBox_1.currentText()), 
                                                            str(self.exchangeComboBox_2.currentText())
                                                            )
            print("Before first:", first[0])
            if first[0]:
                self.exchangethread = PriceUpdater(parent=None, index=index)
                self.exchangethread.set_object_id(id(self.exchangethread))
                self.exchangethread.start()
                first[0] = False
            print("After first:", first[0])
            self.exchangethread.set_bot(self.exchange_bot)
            self.exchangethread.updatedPrice.connect(update_price_label)

        first = [True]

        self.exchangeComboBox_1.currentIndexChanged.connect(lambda: update(5, first))
        self.exchangeComboBox_2.currentIndexChanged.connect(lambda: update(5, first))

        #--------------------------- END ---------------------------#

        #--------------------------- Amount Change ---------------------------#

        self.amountChangeTheadConnector = AmountChangeTheadConnector(self.exchangeSellLineEdit)

        self.amountChangeTheadConnector.start_thread(AmountChange(  self.exchangeBuyLineEdit,
                                                                    self.exchange_bot))
        
        #--------------------------- Setting up Max button ---------------------------#

        def set_max_button(threadConnector):

            if threadConnector.is_max_button_unlocked():
                threadConnector.start_thread(MaxValue(  self.exchangeComboBox_1, 
                                                        self.exchange_bot))

        self.maxValueThreadConnector = MaxValueThreadConnector(self.exchangeBuyLineEdit)

        self.maxButton.clicked.connect(lambda: set_max_button(self.maxValueThreadConnector))

        #--------------------------- END ---------------------------#

        #--------------------------- Switch Pairs ---------------------------#

        def switch_token_pair():

            exchangeCB_1_index = self.exchangeComboBox_1.currentIndex()
            exchangeCB_2_index = self.exchangeComboBox_2.currentIndex() 
            sell_amount = self.exchangeSellLineEdit.text() if not self.exchangeSellLineEdit.text() == '' else '0.0'

            # Switching both comboboxes index values
            self.exchangeComboBox_1.setCurrentIndex(exchangeCB_2_index)
            self.exchangeComboBox_2.setCurrentIndex(exchangeCB_1_index)

            self.exchange_bot.set_contract_get_price_func(  str(self.exchangeComboBox_1.currentText()), 
                                                            str(self.exchangeComboBox_2.currentText()))
            price = self.exchange_bot.get_price()

            if price >= 0: 
                self.exchangePriceLabel.setText(str(price) + 
                                                " " +
                                                str(self.exchangeComboBox_2.currentText()).upper() +
                                                " per " +
                                                str(self.exchangeComboBox_1.currentText()).upper())
                
                self.exchangeSellLineEdit.setText(str(float(sell_amount) / price))

            else:
                self.exchangePriceLabel.setText(str(self.sender().errorStr))
                self.exchangeSellLineEdit.setText("0.0")

            # price = float(str(self.exchangePriceLabel.text()).split(' ')[0])

            # Switching both LineEdit values
            self.exchangeBuyLineEdit.setText(sell_amount)


        # Setting up switch button to efficiently switch comboboxes values
        self.switchButton.clicked.connect(switch_token_pair)

        #--------------------------- END ---------------------------#

        #--------------------------- Measuring Amount ---------------------------#

        def set_measured_amount(lineEdit_1, lineEdit_2, label_1, label_2, buy:bool):
    
            # Check if label_1 was changed or not
            # label_1_str = str(label_1.text())
            # if 'est' in label_1_str:
            #     label_1.setText(label_1_str[:len(label_1_str)-12]) # 12 is the length of: (estimated)

            price = float(str(self.exchangePriceLabel.text()).split(' ')[0])

            if str(lineEdit_1.text()) != '':
                lineEdit_2.setText( str(float(lineEdit_1.text()) * price)
                                    if buy else
                                    str(float(lineEdit_1.text()) / price))

        self.exchangeBuyLineEdit.textEdited.connect(    lambda: 
                                                        set_measured_amount(
                                                            self.exchangeBuyLineEdit,
                                                            self.exchangeSellLineEdit,
                                                            self.fromLabel,
                                                            self.toLabel,
                                                            True # True that it is buy textbox
                                                        ))

        self.exchangeSellLineEdit.textEdited.connect(   lambda: 
                                                        set_measured_amount(
                                                            self.exchangeSellLineEdit,
                                                            self.exchangeBuyLineEdit,
                                                            self.toLabel,
                                                            self.fromLabel,
                                                            False # False that it is sell textbox
                                                        ))

        #--------------------------- END ---------------------------#

        #--------------------------- Swapping ---------------------------#

        # Final part where swapping is done
        #
        # Enables the swap button if connected
        def toggle_swap_button():
            if  self.connectionMainLabel.text() == 'Connected!' and \
                self.exchangeComboBox_1.currentIndex() != self.exchangeComboBox_2.currentIndex():
                self.swapButton.setEnabled(True)
            else:
                self.swapButton.setEnabled(False)

        self.connectionMainLabel.textChanged.connect(toggle_swap_button)

        # Implementing Swap Button Functionality
        def swap():

            # Using message to confirm
            self.create_swap_message_box()

            self.messageBoxThreadConnector = MessageBoxThreadConnector( self.exchange_message_box,
                                                                        self.exchangeComboBox_1,
                                                                        self.exchangeComboBox_2)

            self.messageBoxThreadConnector.start_thread(MessageBox( self.exchangeBuyLineEdit,
                                                                    self.exchangeSellLineEdit))

            msgbox_result = self.exchange_message_box.exec_()

            if msgbox_result == self.exchange_message_box.No:
                print("closing exchange box")

            # Swap if Yes is pressed
            if msgbox_result == self.exchange_message_box.Yes:
                token0 = utils.search_token(self.exchangeComboBox_1.currentText(), self.exchange_bot.tokens)
                token1 = utils.search_token(self.exchangeComboBox_2.currentText(), self.exchange_bot.tokens)

                self.swapTokensThreadConnector = SwapTokensThreadConnector()

                self.swapTokensThreadConnector.start_thread(SwapTokens( token0,
                                                                        token1,
                                                                        float(self.exchangeSellLineEdit.text()),
                                                                        self.exchange_bot))

            self.messageBoxThreadConnector.stop_thread()

        self.swapButton.clicked.connect(swap)

        #--------------------------- END ---------------------------#

    # Set Main Bot interface
    def set_bots(self):
        self.bots = [Bot(utils.load_setting('pancakeswap')) for i in range(BOTS)]
        self.record_bot = Bot(utils.load_setting('pancakeswap'))

    def set_combo_boxes(self):
    
        # Fill combo boxes 
        for i in range(BOTS):

            # Fill two combo boxes in each token slot
            for c in range(2):
                self.combo_boxes[i][c].clear()
                self.combo_boxes[i][c].addItems(TOKENS_LIST)

    # Set account details group box and establish a connection with a thread
    def set_accounts_groupBox(self):
        
        # Fetch stored account address and pkey
        self.config_path = utils.get_path(['assets', 'pancakeswap', 'config.dat'])

        # config = None
        address = None
        privateKey = None
        if os.path.exists(self.config_path) and os.path.getsize(self.config_path):
            self.autoConnectCheckBox.setEnabled(True)
            with open(self.config_path) as f:
                config = f.read().split('\n')
                address = config[0]
                self.addrLabel.setText(address)
                privateKey = config[1]

        self.accountConnectionThreadConnector = AccountConnectionThreadConnector(   addressLabel=self.addrLabel,
                                                                                    statusLabel=self.connectionMainLabel,
                                                                                    checkBox=self.autoConnectCheckBox)

        if self.autoConnectCheckBox.isChecked():
            self.accountConnectionThreadConnector.start_thread( AccountConnection
                                                                                (   index=1, 
                                                                                    bots=self.bots + [self.exchange_bot],
                                                                                    addr=address,
                                                                                    pkey=privateKey
                                                                                )
                                                                )
        
        self.autoConnectCheckBox.stateChanged.connect(  lambda: self.accountConnectionThreadConnector.start_thread(
                                                                AccountConnection(  index=1, 
                                                                                    bots=self.bots + [self.exchange_bot],
                                                                                    addr=address,
                                                                                    pkey=privateKey
                                                                )
                                                            )
                                                        )

    # Fetch and display the wallet token's balance
    def set_balance_groupBox(self):
        
        self.bal_labels = dict()

        self.scrollArea.setWidgetResizable(True)

        self.balGridLayout = QGridLayout(self.scrollAreaWidgetContents_2)
        self.scrollAreaWidgetContents_2.setLayout(self.balGridLayout)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents_2)

        # label generation based on number of tokens
        for i, token in enumerate(TOKENS_LIST):
            symbolLabel = QLabel(token)
            symbolLabel.setMinimumSize(60, 20)
            symbolLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            balLabel = QLabel("-") 
            balLabel.setMinimumSize(60, 20)
            balLabel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            self.bal_labels[token] = (symbolLabel, balLabel)
            self.balGridLayout.addWidget(symbolLabel, i, 0)
            self.balGridLayout.addWidget(balLabel, i, 1)

        # ---------- Get token balances ---------- #
        #        
        self.balanceUpdaterThreadConnector = BalanceUpdaterThreadConnector( labels=self.bal_labels, 
                                                                            checkBox=self.autoConnectCheckBox)

        # If auto connect selected then start balance thread
        if self.autoConnectCheckBox.isChecked():
            self.balanceUpdaterThreadConnector.start_thread(BalanceUpdater(index=2, bot=self.exchange_bot))
        
        self.autoConnectCheckBox.stateChanged.connect(  lambda: self.balanceUpdaterThreadConnector.start_thread(
                                                                BalanceUpdater(index=2, bot=self.exchange_bot)
                                                            )
                                                        )
        #
        # ---------- END ---------- #

    def set_prices_record_groupBox(self):

        # Fill the list with all tokens
        self.listWidget.addItems(TOKENS_LIST)

        # Maximum selection is limited to 5
        self.listWidget.itemSelectionChanged.connect(lambda:self.listWidget.selectedItems()[-1].setSelected(False)
                                                            if len(self.listWidget.selectedItems()) == 6
                                                            else
                                                            None)

        # Start recording price and save it in csv file
        def start_price_recording():
            self.recordButton.setEnabled(False)

            typeTime = self.timeComboBox.currentText()

            seconds =   self.timeSpinBox.value() \
                        if typeTime == "secs" else self.timeSpinBox.value() * 60 \
                        if typeTime == "mins" else self.timeSpinBox.value() * 3600

            # Record prices thread and thread connector
            self.recordPrices = RecordPrices(self.listWidget.selectedItems(), self.record_bot, seconds)
            self.recordPrices.set_binance_config(self.binance_config)
            self.recordPricesThreadConnector = RecordPricesThreadConnector(self.recordButton, seconds)
            self.recordPricesThreadConnector.start_thread(self.recordPrices)

        self.recordButton.clicked.connect(start_price_recording)

class ConnectForm(QDialog):
    
    def __init__(self, parent=None):

        super(ConnectForm, self).__init__(parent)
        self.parent = parent
        loadUi(PATH + '\connect.ui', self)
        self.setFixedSize(self.size().width(), self.size().height())
        self.fill_textboxes()
        self.connectButton.clicked.connect(self.connect_event)
        self.exchange_bot = self.parent.exchange_bot
        self.bots = self.parent.bots


    # Fills the address and key editlabel from stored config.dat file
    def fill_textboxes(self):

        # self.config_path = utils.get_path(['assets', 'pancakeswap', 'config.dat'])
        
        config = None
        if os.path.exists(self.parent.config_path) and os.path.getsize(self.parent.config_path):
            with open(self.parent.config_path) as f:
                config = f.read().split('\n')
                self.addressLineEdit.setText(config[0])
                self.privateKeyLineEdit.setText(config[1])

    # Fetches Address and Private Key and stores them in a text file
    def connect_event(self):

        # ----- Save Address and Pvt Key in config.dat ----- #
        #
        self.address = self.addressLineEdit.text()
        privateKey = self.privateKeyLineEdit.text()

        self.parent.autoConnectCheckBox.setEnabled(True)
        #
        # ----- Ends ----- #

        # ----- Set each Bot address values and verify them against blockchain ----- #
        #
        for i in range(BOTS):
            connection = self.bots[i].set_address(self.address, privateKey)
            if connection != True:
                break

        if connection == True:
            connection = 'Connected!'
            self.connectionLabel.setStyleSheet("color: rgb(0, 185, 0);")

            if self.rememberCheckBox.isChecked():
                with open(self.parent.config_path, 'w') as f:
                    print('printing to file...')
                    f.write(self.addressLineEdit.text() + '\n')
                    f.write(self.privateKeyLineEdit.text())

            print(connection)
            self.connectionLabel.setText(connection)

            # Execute parent set accounts function to start connector thread
            if self.parent.autoConnectCheckBox.isChecked():
                self.parent.balanceUpdaterThreadConnector.start_thread(BalanceUpdater(index=20, bot=self.exchange_bot))
                self.parent.accountConnectionThreadConnector.start_thread(AccountConnection(index=10, 
                                                                                            bots=self.bots + [self.exchange_bot],
                                                                                            addr=self.address,
                                                                                            pkey=privateKey))

            # Close the Connect Dialog Box
            self.closeEvent(QCloseEvent())
        #
        # ----- Ends ----- #

    def closeEvent(self, evnt):
        self.parent.actionConnect.setEnabled(True)
        super(ConnectForm, self).closeEvent(evnt)

if __name__ == '__main__':

    helper_func()
    app = QApplication(sys.argv)
    window = MainForm()
    app.exec_()
