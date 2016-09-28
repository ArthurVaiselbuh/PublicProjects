import sys
from PyQt4 import QtCore, QtGui
from ui import Ui_MainWindow


def read_xml():
    XML_PATH = ""
    # this is just a sample dict
    d = {"t1":"sample1", "t2":"Sample Data"}
    return d

class AppWindow(QtGui.QMainWindow, Ui_MainWindow):
    PERIODIC_INTERVAL = 5 * 1000

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.data = {}
        # Load data into the combobox
        self._load_data()
        #Connect onchange event
        self.comboBox.currentIndexChanged.connect(self._onCBIndexChanged)

        #Set timer for periodic calls
        self.timer = QtCore.QTimer()
        self.timer.setInterval(self.PERIODIC_INTERVAL)
        self.timer.timeout.connect(self._periodic_func)
        self.timer.start()

    def _load_data(self):
        self.data = read_xml()
        # set combobox items
        self.comboBox.addItems(list(self.data.keys()))

    def _onCBIndexChanged(self, event):
        key = self.comboBox.currentText()
        # set data accordingly
        self.le_0.setText(self.data[unicode(key)])

    def _periodic_func(self):
        print("Periodic call example")


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ui = AppWindow()
    ui.show()
    sys.exit(app.exec_())
