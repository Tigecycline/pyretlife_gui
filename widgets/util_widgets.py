from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QListWidget,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    QComboBox,
    QGroupBox,
    QListWidgetItem,
    QTableWidgetItem,
    QAbstractItemView,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy
)
from PySide6.QtGui import QDoubleValidator

from abc import abstractmethod

from constants import PRIOR_PARAM_NAMES
from config_handler import param_dict




class EditableList(QListWidget):
    def __init__(self):
        super().__init__()
        self.setEditTriggers(QAbstractItemView.DoubleClicked)


    def __getitem__(self, idx):
        return self.item(idx).text().rstrip()
    

    #def __setitem__(self, idx, new_text):
    #    self.item(idx).setText(new_text)


    @property
    def texts(self):
        return [self[i] for i in range(self.count())]


    def addItem(self, label):
        item = QListWidgetItem(label)
        item.setFlags(item.flags() | Qt.ItemIsEditable)
        super().addItem(item)
    

    def addItems(self, labels: list):
        for label in labels:
            self.addItem(label)


    def removeCurrentItem(self):
        row = self.currentRow()
        if row < 0:
            print('hi')
            return
        else:
            print('hi2')
            self.takeItem(row)
    



class AbstractPriorBox(QGroupBox):
    '''
    Group box widget for editing true value, prior and prior parameters.
    '''
    def __init__(self, title):
        super().__init__(title)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        
        self.grid = QGridLayout()

        # the truth
        self.grid.addWidget(QLabel('Truth:'), *self.widget_loc(0, 0))
        self.truth = QLineEdit()
        self.truth.setValidator(QDoubleValidator())
        self.grid.addWidget(self.truth, *self.widget_loc(0, 1))

        # the prior
        self.grid.addWidget(QLabel('Prior:'), *self.widget_loc(1, 0))
        self.kind = QComboBox()
        self.kind.addItems(PRIOR_PARAM_NAMES)
        self.kind.currentTextChanged.connect(self.update_params)
        self.grid.addWidget(self.kind, *self.widget_loc(1, 1))

        self.setLayout(self.grid)

        self.prior_params = {}
        self.update_params()
    

    def __getitem__(self, key):
        return self.prior_params[key]
    

    @abstractmethod
    def widget_loc(self, a, b):
        '''
        a: int, element number
        b: int, 0 (label) or 1 (edit)
        '''
        pass


    def update_params(self):
        # remove old parameter widgets
        # On deleting widgets from layout:
        # - For unknown reason, deleteLater alone works for MainWindow, but not for Dialogs
        # - For dialogs, removeWidget (or removeItem) has to be performed as well to make the widget disappear
        # - Widgets other than MainWindow and Dialog were not tested
        # - Using only removeWidget seems to move the widget out of the layout, but the widget remains in the window, at the lower left corner
        # - Using removeWidget before applying the layout (with setLayout) crashes the program ("segmentation fault (core dumped)")
        # TODO?: use stack layout instead
        
        # remove old widgets
        for i in range(len(self.prior_params)):
            for j in range(2):
                item = self.grid.itemAtPosition(*self.widget_loc(i+2, j))
                item.widget().deleteLater()
                self.grid.removeItem(item)
        
        # remove all old parameters
        self.prior_params.clear()
        # create new parameters according to current prior
        new_prior = self.kind.currentText()
        for i, param_name in enumerate(PRIOR_PARAM_NAMES[new_prior]):
            self.grid.addWidget(QLabel(param_name + ':'), *self.widget_loc(i+2, 0))
            param_edit = QLineEdit()
            param_edit.setValidator(QDoubleValidator())
            self.grid.addWidget(param_edit, *self.widget_loc(i+2, 1))
            self.prior_params[param_name] = param_edit
    

    def read_from_dict(self, prior):
        self.truth.setText(str(prior['truth']))
        self.kind.setCurrentText(prior['prior']['kind'])
        prior_params = prior['prior']['prior_specs']
        for param_name in prior_params.keys():
            self.prior_params[param_name].setText(str(prior_params[param_name]))
    

    def write_to_dict(self):
        truth = float(self.truth.text())
        kind = self.kind.currentText()
        prior_params = [float(prior_param.text()) for prior_param in self.prior_params.values()]
        return param_dict(kind, prior_params, truth)




class VPriorBox(AbstractPriorBox):
    def __init__(self, title='Prior'):
        super().__init__(title)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        

    def widget_loc(self, a, b):
        return a, b




class HPriorBox(AbstractPriorBox):
    def __init__(self, title='Prior'):
        super().__init__(title)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignLeft)


    def widget_loc(self, a, b):
        return 0, 2*a + b




class RangeEdit(QWidget):
    def __init__(self, name=None):
        super().__init__()
        hbox = QHBoxLayout()
        hbox.setAlignment(Qt.AlignmentFlag.AlignLeft)

        if name is not None:
            hbox.addWidget(QLabel(name))
        
        self.lb = QDoubleSpinBox()
        self.lb.setRange(1.0, 20.0)
        self.lb.setSingleStep(0.5)
        self.lb.setDecimals(1)
        self.lb.valueChanged.connect(self.check_upper_bound)
        hbox.addWidget(self.lb)

        hbox.addWidget(QLabel('-'))

        self.ub = QDoubleSpinBox()
        self.ub.setRange(1.0, 20.0)
        self.ub.setSingleStep(0.5)
        self.ub.setDecimals(1)
        self.ub.valueChanged.connect(self.check_lower_bound)
        hbox.addWidget(self.ub)

        self.setLayout(hbox)
    

    @property
    def lower(self):
        return float(self.lb.text())
    

    @property
    def upper(self):
        return float(self.ub.text())


    @property
    def unbalanced(self):
        return self.lb.value() > self.ub.value()
    

    def check_upper_bound(self):
        # keep upper bound greater equal lower bound
        if self.unbalanced:
            self.ub.setValue(self.lb.value())
    

    def check_lower_bound(self):
        # keep lower bound less equal upper bound
        if self.unbalanced:
            self.lb.setValue(self.ub.value())
    

    def set_values(self, lb, ub):
        self.lb.setValue(lb)
        self.ub.setValue(ub)
    

    def set_unit(self, unit):
        self.lb.setSuffix(' ' + unit)
        self.ub.setSuffix(' ' + unit)