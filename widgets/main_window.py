import sys
from time import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDialogButtonBox,
    QLabel,
    QTabWidget,
    QDialog,
    QFileDialog,
    QMainWindow
)

from widgets.species_editor import SpeciesEditor
from widgets.physical_editor import PhysEditor
from widgets.run_settings_editor import RunSettingsEditor
from config_handler import ConfigHandler




class MainWindow(QMainWindow):
    def __init__(self, title='Config Editor (test)', width=640, height=480, fixed_size=True):
        start_time = time()

        super().__init__()
        self.setWindowTitle(title)

        if fixed_size:
            self.setFixedSize(width, height)
        else:
            self.resize(width, height)
        
        self.current_file = None
        self.config = ConfigHandler()
        self.config.read_yaml('default.yaml')

        self.file_menu = self.menuBar().addMenu('File') # NB can use "&" to emphasize a letter
        
        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save)
        self.file_menu.addAction(save_action)

        load_action = QAction('Load YAML', self)
        load_action.triggered.connect(self.load_yaml)
        self.file_menu.addAction(load_action)

        preview_action = QAction('Preview (dummy)', self)
        #preview_action.triggered.connect(self.preview)
        self.file_menu.addAction(preview_action)

        reset_action = QAction('Reset (dummy)', self)
        #reset_action.triggered.connect(self.reset)
        self.file_menu.addAction(reset_action)

        central_tab = QTabWidget()
        central_tab.setTabPosition(QTabWidget.North)

        self.pt_editor = RunSettingsEditor(self.config)
        central_tab.addTab(self.pt_editor, 'Run Settings')

        self.phys_editor = PhysEditor(self.config)
        central_tab.addTab(self.phys_editor, 'Physical Parameters')

        self.species_editor = SpeciesEditor(self.config)
        central_tab.addTab(self.species_editor, 'Species')
        
        central_tab.addTab(QLabel('To be implemented'), 'Clouds')

        self.setCentralWidget(central_tab)

        init_time = (time() - start_time) * 1000
        print('Init time: %.3f ms' % init_time)

    
    def save(self, fname=None):
        self.pt_editor.write_to_config(self.config)
        self.species_editor.write_to_config(self.config)
        self.phys_editor.write_to_config(self.config)
        
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