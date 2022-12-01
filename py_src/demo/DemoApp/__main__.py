if __name__ == '__main__':
    from PyQt5 import QtWidgets
    from demoApp import MainWindow

    app = QtWidgets.QApplication([])
    w = MainWindow()
    app.exec_()
