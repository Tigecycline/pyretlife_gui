from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QGroupBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QHeaderView,
    QAbstractItemView
)
from PySide6.QtGui import QIntValidator

from widgets.util_widgets import RangeEdit
from constants import PT_PARAMETERIZATIONS, UNITS




class RunSettingsEditor(QWidget):
    def __init__(self, config=None):
        super().__init__()

        outpath_bar = QHBoxLayout()

        outpath_bar.addWidget(QLabel('Output Folder:'))
        self.output_path = QLineEdit()
        outpath_bar.addWidget(self.output_path)
        self.output_browse_button = QPushButton('Browse')
        #self.output_browse_button.clicked.connect(self.browse_output)
        outpath_bar.addWidget(self.output_browse_button)
        self.output_browse_button.setEnabled(False)

        profile_bar = QHBoxLayout()

        profile_bar.addWidget(QLabel('Input Profile:'))
        self.input_profile = QLineEdit()
        profile_bar.addWidget(self.input_profile)
        self.profile_browse_button = QPushButton('Browse')
        #self.profile_browse_button.clicked.connect(self.browse_profile)
        profile_bar.addWidget(self.profile_browse_button)
        self.profile_browse_button.setEnabled(False)

        self.data_files = DataFileEditor()
        
        run_settings_bar = QHBoxLayout()
        run_settings_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.wl_range = RangeEdit('Wavelength Range:')
        self.wl_range.set_unit('μm')
        run_settings_bar.addWidget(self.wl_range)

        run_settings_bar.addWidget(QLabel('Number of Layers:'))
        self.n_layers = QLineEdit()
        self.n_layers.setValidator(QIntValidator())
        run_settings_bar.addWidget(self.n_layers)

        run_settings_bar.addWidget(QLabel('Live Points:'))
        self.live_points = QLineEdit()
        self.live_points.setValidator(QIntValidator())
        self.live_points.setFixedWidth(40)
        run_settings_bar.addWidget(self.live_points)
        
        self.cia = QCheckBox()
        run_settings_bar.addWidget(self.cia)
        run_settings_bar.addWidget(QLabel('CIA'))

        self.moon = QCheckBox()
        run_settings_bar.addWidget(self.moon)
        run_settings_bar.addWidget(QLabel('Moon'))

        self.scattering = ScatteringBox()

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(outpath_bar)
        main_vbox.addLayout(profile_bar)
        main_vbox.addWidget(QLabel('Input Spectra:'))
        main_vbox.addWidget(self.data_files)
        main_vbox.addLayout(run_settings_bar)
        main_vbox.addWidget(self.scattering)
        main_vbox.addStretch()
        self.setLayout(main_vbox)

        if config is not None:
            self.read_from_config(config)
    

    def read_from_config(self, config):
        self.input_profile.setText(config['GROUND TRUTH DATA']['input_profile'])
        self.data_files.read_from_dict(config['GROUND TRUTH DATA']['data_files'])

        wl_range = config['RUN SETTINGS']['wavelength_range']
        self.wl_range.set_values(wl_range[0], wl_range[1])

        self.output_path.setText(config['RUN SETTINGS']['output_folder'])

        self.scattering['Rayleigh'].setChecked(config['RUN SETTINGS']['include_scattering']['Rayleigh'])
        self.scattering['thermal'].setChecked(config['RUN SETTINGS']['include_scattering']['thermal'])
        self.scattering['direct light'].setChecked(config['RUN SETTINGS']['include_scattering']['direct_light'])
        self.scattering['clouds'].setChecked(config['RUN SETTINGS']['include_scattering']['clouds'])

        self.cia.setChecked(config['RUN SETTINGS']['include_CIA'])
        self.moon.setChecked(config['RUN SETTINGS']['include_moon'])

        self.n_layers.setText(str(config['RUN SETTINGS']['n_layers']))
        self.live_points.setText(str(config['RUN SETTINGS']['live_points']))
    

    def write_to_config(self, config):
        config['GROUND TRUTH DATA']['input_profile'] = self.input_profile.text()
        config['GROUND TRUTH DATA']['data_files'] = self.data_files.write_dict()

        wl_range = [self.wl_range.lb.value(), self.wl_range.ub.value()]
        config['RUN SETTINGS']['wavelength_range'] = wl_range

        config['RUN SETTINGS']['output_folder'] = self.output_path.text()

        config['RUN SETTINGS']['include_scattering']['Rayleigh'] = self.scattering['Rayleigh'].isChecked()
        config['RUN SETTINGS']['include_scattering']['thermal'] = self.scattering['thermal'].isChecked()
        config['RUN SETTINGS']['include_scattering']['direct_light'] = self.scattering['direct light'].isChecked()
        config['RUN SETTINGS']['include_scattering']['clouds'] = self.scattering['clouds'].isChecked()

        config['RUN SETTINGS']['include_CIA'] = self.cia.isChecked()
        config['RUN SETTINGS']['include_moon'] = self.moon.isChecked()

        config['RUN SETTINGS']['n_layers'] = int(self.live_points.text())
        config['RUN SETTINGS']['live_points'] = int(self.live_points.text())


    def browse_input_profile(self):
        print('Browse input profile')


    def browse_input_data(self):
        print('Browse input data')


    def browse_output_path(self):
        print('Browse output path')
    

    def check_valid(self):
        pass




class DataFileEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.table = DataFileTable()

        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.add_entry)
        self.remove_button = QPushButton('Remove')
        self.remove_button.clicked.connect(self.remove_current_entry)
        self.browse_button = QPushButton('Browse')
        self.browse_button.setEnabled(False)

        grid = QGridLayout()
        grid.addWidget(self.table, 0, 0, 5, 1)
        grid.addWidget(self.add_button, 1, 1, 1, 1)
        grid.addWidget(self.remove_button, 2, 1, 1, 1)
        grid.addWidget(self.browse_button, 3, 1, 1, 1)

        self.setLayout(grid)
    

    def read_from_dict(self, datafile_dict):
        self.table.remove_all()
        for inst_name in datafile_dict.keys():
            path = datafile_dict[inst_name]['path']
            wl_unit, flux_unit = datafile_dict[inst_name]['unit'].split(', ')
            self.table.add_row(inst_name, path, wl_unit, flux_unit)
    

    def write_dict(self):
        result = {}
        for i in range(self.table.rowCount()):
            result[self.table[i,0]] = {}
            result[self.table[i,0]]['path'] = self.table[i,1]
            result[self.table[i,0]]['unit'] = ', '.join((self.table.cellWidget(i, 2).currentText(), self.table.cellWidget(i, 3).currentText()))
        
        return result
    

    def add_entry(self):
        self.table.add_row()
    

    def remove_current_entry(self):
        self.table.removeRow(self.table.currentRow())




class DataFileTable(QTableWidget):
    COLUMNS = ['Name', 'Path', 'Wavelength Unit', 'Flux Unit']

    def __init__(self):
        super().__init__(0, len(DataFileTable.COLUMNS))

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setHorizontalHeaderLabels(DataFileTable.COLUMNS)
        header = self.horizontalHeader()
        #header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
    

    def __getitem__(self, key):
        # NB don't use itemAt since its coordinates are pixels
        return self.item(key[0], key[1]).text()


    def __setitem__(self, key, attr):
        self.setItem(key[0], key[1], QTableWidgetItem(attr))
    

    def add_row(self, name='', path='', wl_unit='', flux_unit=''):
        if wl_unit == '':
            wl_unit = UNITS['wavelength']['default']
        if flux_unit == '':
            flux_unit = UNITS['flux']['default']

        i = self.rowCount()
        self.insertRow(i)

        self[i,0] = name
        self[i,1] = path
        self.setCellWidget(i, 2, QComboBox())
        self.cellWidget(i, 2).addItems(UNITS['wavelength']['options'])
        self.cellWidget(i, 2).setCurrentText(wl_unit)
        self.setCellWidget(i, 3, QComboBox())
        self.cellWidget(i, 3).addItems(UNITS['flux']['options'])
        self.cellWidget(i, 3).setCurrentText(flux_unit)
    

    def remove_all(self):
        self.setRowCount(0)
    



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
        