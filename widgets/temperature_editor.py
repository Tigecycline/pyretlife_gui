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

from widgets.util_widgets import RangeEdit, PriorBox
from constants import PT_PARAMETERIZATIONS




class TempEditor(QWidget):
    def __init__(self):
        super().__init__()
        main_vbox = QVBoxLayout()

        profile_bar = QHBoxLayout()
        
        profile_bar.addWidget(QLabel('Input Profile:'))
        self.input_profile = QLineEdit()
        profile_bar.addWidget(self.input_profile)
        profile_bar.addWidget(QPushButton('Browse'))

        temp_settings_bar = QHBoxLayout()
        
        temp_settings_bar.addWidget(QLabel('Top Pressure (log):'))
        self.top_pressure = QLineEdit()
        self.top_pressure.setValidator(QDoubleValidator())
        temp_settings_bar.addWidget(self.top_pressure)

        temp_settings_bar.addWidget(QLabel('Number of Layers:'))
        self.n_layers = QLineEdit()
        self.n_layers.setValidator(QIntValidator())
        temp_settings_bar.addWidget(self.n_layers)

        temp_settings_bar.addWidget(QLabel('vae_net:'))
        self.vae_net = QComboBox()
        self.vae_net.addItem('decoder.onx')
        temp_settings_bar.addWidget(self.vae_net)

        main_vbox.addLayout(profile_bar)
        main_vbox.addLayout(temp_settings_bar)
        main_vbox.addWidget(TempParamBox())
        self.setLayout(main_vbox)




class TempParamBox(QGroupBox):
    def __init__(self):
        super().__init__('Temperature Parameters')

        parameterization_bar = QHBoxLayout()
        parameterization_bar.addWidget(QLabel('Parameterization:'))
        
        self.parameterization = QComboBox()
        for prmz in PT_PARAMETERIZATIONS:
            self.parameterization.addItem(prmz)
        parameterization_bar.addWidget(self.parameterization)
        
        parameterization_bar.addStretch()

        self.params = QScrollArea()
        self.params.addScrollBarWidget(PriorBox(), Qt.AlignRight)

        main_vbox = QVBoxLayout()
        main_vbox.addLayout(parameterization_bar)
        main_vbox.addWidget(self.params)
        self.setLayout(main_vbox)
