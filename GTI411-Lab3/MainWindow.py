from Lab3.controllers import Lab3Controller
from PyQt5 import QtWidgets



if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    controller = Lab3Controller()
    sys.exit(app.exec_())
