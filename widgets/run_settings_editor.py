from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QScrollArea,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout
)
from PySide6.QtGui import QDoubleValidator, QIntValidator

from widgets.util_widgets import RangeEdit
from constants import PT_PARAMETERIZATIONS




class RunSettingsEditor(QWidget):
    def __init__(self, input_files, run_settings):
        super().__init__()
        self.input_files = input_files
        self.run_settings = run_settings

        outpath_bar = QHBoxLayout()

        outpath_bar.addWidget(QLabel('Output Path:'))

        self.output_path = QLineEdit()
        outpath_bar.addWidget(self.output_path)

        self.output_browse_button = QPushButton('Browse')
        outpath_bar.addWidget(self.output_browse_button)

        self.data_files = DataFileArea()
        
        run_settings_bar = QHBoxLayout()
        run_settings_bar.addWidget(QLabel('Wavelength Range:'))
        self.wl_range = RangeEdit()
        run_settings_bar.addWidget(self.wl_range)

        run_settings_bar.addWidget(QLabel('Live Points:'))
        self.live_points = QLineEdit()
        self.live_points.setValidator(QDoubleValidator())
        run_settings_bar.addWidget(self.live_points)
        
        self.cia = QCheckBox()
        run_settings_bar.addWidget(self.cia)
        run_settings_bar.addWidget(QLabel('CIA'))

        self.moon = QCheckBox()
        run_settings_bar.addWidget(self.moon)
        run_settings_bar.addWidget(QLabel('Moon'))

        run_settings_bar.addStretch()

        self.scattering = ScatteringBox()

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(outpath_bar)
        main_vbox.addWidget(self.data_files)
        main_vbox.addLayout(run_settings_bar)
        main_vbox.addWidget(self.scattering)
        main_vbox.addStretch()
        self.setLayout(main_vbox)
    

    def browse_input_profile(self):
        print('Browse input profile')


    def browse_input_data(self):
        print('Browse input data')


    def browse_output_path(self):
        print('Browse output path')
    

    def check_valid(self):
        pass




class DataFileArea(QScrollArea):
    def __init__(self):
        super().__init__()
        self.addScrollBarWidget(DataFileEntry(), Qt.AlignTop)




class DataFileEntry(QWidget):
    def __init__(self):
        super().__init__()
        main_grid = QGridLayout()

        for i, label in enumerate(['Instrument', 'Data File', 'Wavelength Unit', 'Flux Unit']):
            main_grid.addWidget(QLabel(label), 0, i)




class ScatteringBox(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Scattering')

        main_bar = QHBoxLayout()

        self.types = {}
        scattering_types = ['Rayleigh', 'thermal', 'direct light', 'clouds']
        for sctype in scattering_types:
            self.types[sctype] = QCheckBox()
            main_bar.addWidget(self.types[sctype])
            main_bar.addWidget(QLabel(sctype))
            main_bar.addSpacing(10)
        
        main_bar.addStretch()
        
        self.setLayout(main_bar)
    

    def __getitem__(self, key):
        return self.types[key]
        