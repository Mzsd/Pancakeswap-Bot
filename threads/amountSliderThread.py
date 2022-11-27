from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QCursor

# Amount Change Thread Class
class AmountSlider(QThread):

    any_signal = pyqtSignal(str, str)

    def __init__(self, bal_labels, amountLineEdit, progressbar, price_label, bot, parent=None, index=202) -> None:
        super(AmountSlider, self).__init__(parent)
        self.amountLineEdit = amountLineEdit
        self.progressbar = progressbar
        self.price_label = price_label
        self.bal_labels = bal_labels
        self.index = index
        self.bot = bot

    def _fetch_amount(self):
        from_token = self.bot.contract[1]['SYMBOL']
        amount_in_str = self.bal_labels[from_token][1].text()
        price = 1 / float(self.price_label.text()) if self.price_label.text() != '-' else 0.0
        return float('0' if amount_in_str == '-' else amount_in_str) * price
        
    def _amount_changed(self):
        
        amount = self._fetch_amount()

        self.amountLineEdit.setText(''
                                    if self.amountLineEdit.text() == ''
                                    else
                                    str(amount)
                                    if float(self.amountLineEdit.text()) > amount
                                    else "0.0"
                                    if float(self.amountLineEdit.text()) < 0
                                    else self.amountLineEdit.text())
                                    
        if self.amountLineEdit.text() != '':
            try:
                self.progressbar.setValue(((float(self.amountLineEdit.text()) / amount) * 100))
            except ZeroDivisionError:
                self.progressbar.setValue(0.0)

    def _value_changed(self):
        tip = QToolTip
        tip.showText(QCursor.pos(), str(self.progressbar.value()), self.progressbar)

        self.amountLineEdit.setText(str(self._fetch_amount() * (self.progressbar.value() / 100)))

    def stop(self):
        print('Stopping thread...', self.index)
        self.terminate()

    def run(self):
        print('Starting thread...', self.index)

        self.amountLineEdit.textEdited.connect(self._amount_changed)
        self.progressbar.sliderMoved.connect(self._value_changed)
