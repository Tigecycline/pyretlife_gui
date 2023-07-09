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
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout
)
from PySide6.QtGui import QDoubleValidator, QIntValidator

from widgets.util_widgets import RangeEdit, VPriorBox, HPriorBox
from constants import PT_PARAMETERIZATIONS




class PhysEditor(QWidget):
    def __init__(self, config=None):
        super().__init__()
        main_vbox = QVBoxLayout()

        # physical parameters of the planet
        planet_params_bar = QHBoxLayout()

        self.p0 = VPriorBox('Ground Pressure')
        planet_params_bar.addWidget(self.p0)
        self.rpl = VPriorBox('Planet Radius')
        planet_params_bar.addWidget(self.rpl)
        self.mpl = VPriorBox('Planet Mass')
        planet_params_bar.addWidget(self.mpl)

        main_vbox.addLayout(planet_params_bar)
        self.pt_params = PTParamBox()
        main_vbox.addWidget(self.pt_params)
        
        self.setLayout(main_vbox)

        if config is not None:
            self.read_from_config(config)
            self.pt_params.read_from_dict(config['TEMPERATURE PARAMETERS'])


    def read_from_config(self, config):
        self.p0.read_from_dict(config['PHYSICAL PARAMETERS']['P0'])
        self.rpl.read_from_dict(config['PHYSICAL PARAMETERS']['R_pl'])
        self.mpl.read_from_dict(config['PHYSICAL PARAMETERS']['M_pl'])
    

    def write_to_config(self, config):
        config['PHYSICAL PARAMETERS']['p0'] = self.p0.write_to_dict()
        config['PHYSICAL PARAMETERS']['R_pl'] = self.rpl.write_to_dict()
        config['PHYSICAL PARAMETERS']['M_pl'] = self.mpl.write_to_dict()

        config['TEMPERATURE PARAMETERS'] = self.pt_params.write_to_dict()




class PTParamBox(QGroupBox):
    def __init__(self):
        super().__init__('P-T Profile Approximation')

        parameterization_bar = QHBoxLayout()
        parameterization_bar.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        parameterization_bar.addWidget(QLabel('Parameterization:'))
        
        self.parameterization = QComboBox()
        for prmz in PT_PARAMETERIZATIONS:
            self.parameterization.addItem(prmz)
        self.parameterization.currentTextChanged.connect(self.update_params)
        parameterization_bar.addWidget(self.parameterization)

        self.param_area = QScrollArea()
        self.param_area.setWidgetResizable(True)

        self.vbox = QVBoxLayout()
        self.vbox.addLayout(parameterization_bar)
        self.vbox.addWidget(self.param_area)
        self.setLayout(self.vbox)

        self.params = {}
        self.update_params()
    

    def update_params(self):
        param_widget = QWidget()
        param_vbox = QVBoxLayout()

        self.params.clear()
        for param_name in PT_PARAMETERIZATIONS[self.parameterization.currentText()]:
            self.params[param_name] = HPriorBox(param_name)
            param_vbox.addWidget(self.params[param_name])

        param_widget.setLayout(param_vbox)
        self.param_area.setWidget(param_widget)
    

    def read_from_dict(self, pt_dict):
        self.parameterization.setCurrentText(pt_dict['parameterization'])
        for param_name in self.params.keys():
            self.params[param_name].read_from_dict(pt_dict[param_name])
    

    def write_to_dict(self):
        pt_dict = {}
        pt_dict['parameterization'] = self.parameterization.currentText()
        for param_name in self.params.keys():
            pt_dict[param_name] = self.params[param_name].write_to_dict()
        
        return pt_dict