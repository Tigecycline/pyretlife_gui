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
    def __init__(self, config=None):
        super().__init__()

        outpath_bar = QHBoxLayout()

        outpath_bar.addWidget(QLabel('Output Path:'))

        self.output_path = QLineEdit()
        outpath_bar.addWidget(self.output_path)

        self.output_browse_button = QPushButton('Browse')
        outpath_bar.addWidget(self.output_browse_button)
        self.output_browse_button.setEnabled(False)

        self.data_files = DataFileArea()
        
        run_settings_bar = QHBoxLayout()

        run_settings_bar.addWidget(QLabel('Wavelength Range:'))
        self.wl_range = RangeEdit()
        self.wl_range.set_unit('μm')
        run_settings_bar.addWidget(self.wl_range)
        run_settings_bar.addSpacing(40)

        run_settings_bar.addWidget(QLabel('Live Points:'))
        self.live_points = QLineEdit()
        self.live_points.setValidator(QIntValidator())
        run_settings_bar.addWidget(self.live_points)
        run_settings_bar.addSpacing(40)
        
        self.cia = QCheckBox()
        run_settings_bar.addWidget(self.cia)
        run_settings_bar.addWidget(QLabel('CIA'))
        run_settings_bar.addSpacing(20)

        self.moon = QCheckBox()
        run_settings_bar.addWidget(self.moon)
        run_settings_bar.addWidget(QLabel('Moon'))
        run_settings_bar.addStretch()

        self.scattering = ScatteringBox()

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(outpath_bar)
        main_vbox.addWidget(QLabel('Input Spectra:'))
        main_vbox.addWidget(self.data_files)
        main_vbox.addLayout(run_settings_bar)
        main_vbox.addWidget(self.scattering)
        main_vbox.addStretch()
        self.setLayout(main_vbox)

        if config is not None:
            self.read_from_config(config)
    

    def read_from_config(self, config):
        wl_range = config['RUN SETTINGS']['wavelength_range']
        self.wl_range.set_values(wl_range[0], wl_range[1])

        self.output_path.setText(config['RUN SETTINGS']['output_folder'])

        self.live_points.setText(str(config['RUN SETTINGS']['live_points']))

        self.cia.setChecked(config['RUN SETTINGS']['include_CIA'])

        self.moon.setChecked(config['RUN SETTINGS']['include_moon'])

        self.scattering['Rayleigh'].setChecked(config['RUN SETTINGS']['include_scattering']['Rayleigh'])
        self.scattering['thermal'].setChecked(config['RUN SETTINGS']['include_scattering']['thermal'])
        self.scattering['direct light'].setChecked(config['RUN SETTINGS']['include_scattering']['direct_light'])
        self.scattering['clouds'].setChecked(config['RUN SETTINGS']['include_scattering']['clouds'])
    

    def write_to_config(self, config):
        wl_range = [self.wl_range.lb.value(), self.wl_range.ub.value()]
        config['RUN SETTINGS']['wavelength_range'] = wl_range

        config['RUN SETTINGS']['output_folder'] = self.output_path.text()

        config['RUN SETTINGS']['live_points'] = float(self.live_points.text())

        config['RUN SETTINGS']['include_CIA'] = self.cia.isChecked()

        config['RUN SETTINGS']['include_moon'] = self.moon.isChecked()

        config['RUN SETTINGS']['include_scattering']['Rayleigh'] = self.scattering['Rayleigh'].isChecked()
        config['RUN SETTINGS']['include_scattering']['thermal'] = self.scattering['thermal'].isChecked()
        config['RUN SETTINGS']['include_scattering']['direct_light'] = self.scattering['direct light'].isChecked()
        config['RUN SETTINGS']['include_scattering']['clouds'] = self.scattering['clouds'].isChecked()


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
        