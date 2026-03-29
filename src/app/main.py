from PySide6 import QtCore, QtWidgets
from app.main_window import MainWindow

def main():
    app = QtWidgets.QApplication()
    window = MainWindow()
    window.show()
    app.exec_()
    
    
if __name__ == "__main__":
    main()
    