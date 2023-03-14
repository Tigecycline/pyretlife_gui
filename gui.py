import sys
from time import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QDialogButtonBox,
    QLabel,
    QTabWidget,
    QDialog,
    QFileDialog,
    QMainWindow
)

from widgets.species_editor import SpeciesEditor
from config_handler import ConfigHandler
        



class MainWindow(QMainWindow):
    def __init__(self, title='Config Editor for pyretlife (test)', width=900, height=600, fixed_size=True):
        
        super().__init__()
        start_time = time()
        self.setWindowTitle(title)

        if fixed_size:
            self.setFixedSize(width, height)
        else:
            self.resize(width, height)
        
        self.current_file = None
        self.config = ConfigHandler()

        self.file_menu = self.menuBar().addMenu('File') # NB can use "&" to emphasize a letter
        
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save)
        self.file_menu.addAction(save_action)

        load_action = QAction('Load YAML', self)
        load_action.triggered.connect(self.load_yaml)
        self.file_menu.addAction(load_action)

        central_tab = QTabWidget()
        central_tab.setTabPosition(QTabWidget.West)
        self.species_editor = SpeciesEditor(self.config['CHEMICAL COMPOSITION PARAMETERS'])
        central_tab.addTab(self.species_editor, 'Species')
        central_tab.addTab(QLabel('Tab2'), 'Tab2')
        central_tab.addTab(QLabel('Tab3'), 'Tab3')

        self.setCentralWidget(central_tab)

        init_time = (time() - start_time) * 1000
        print('Init time: %.3f ms' % init_time)

    
    def save(self, fname=None):
        self.config.write_yaml()
        self.close()
    

    def load_yaml(self, fname=None):
        # TODO?: create the dialog in __init__ and reuse it
        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        fname = dialog.getOpenFileName(filter='*.yaml')[0]
        if fname != '':
            self.config.read_yaml(fname)
            self.species_editor.table.species_dict = self.config['CHEMICAL COMPOSITION PARAMETERS']
            self.species_editor.table.refresh()




app = QApplication(sys.argv) # application handler, sys.argv is list of command line arguments

window = MainWindow()
window.show() # top level widgets must be shown manually

print('Running event loop...')
app.exec()
print('Application exited.')