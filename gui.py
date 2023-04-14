import sys

from PySide6.QtWidgets import QApplication

from widgets.main_window import MainWindow




app = QApplication(sys.argv) # application handler, sys.argv is list of command line arguments

window = MainWindow()
window.show() # top level widgets must be shown manually

print('Running event loop...')
app.exec()
print('Application exited.')