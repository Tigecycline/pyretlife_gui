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
    QGridLayout
)
from PySide6.QtGui import QDoubleValidator

from constants import PRIOR_PARAM_NAMES




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
    



class PriorBox(QGroupBox):
    def __init__(self):
        super().__init__('Prior')
        
        self.grid = QGridLayout()

        self.kind = QComboBox()
        self.kind.addItems(PRIOR_PARAM_NAMES)
        self.kind.currentTextChanged.connect(self.update_params)
        self.grid.addWidget(self.kind, 0, 0, 1, 2)
        
        self.params = []

        self.setLayout(self.grid)
    

    def __getitem__(self, key):
        return self.params[key]


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
        for i in range(len(self.params)):
            for j in range(2):
                item = self.grid.itemAtPosition(i+1, j)
                item.widget().deleteLater()
                self.grid.removeItem(item)
        
        # remove old parameters
        self.params.clear()
        # create new parameters according to current prior
        new_prior = self.kind.currentText()
        if new_prior != '(known)':
            for i, param_name in enumerate(PRIOR_PARAM_NAMES[new_prior]):
                self.grid.addWidget(QLabel(param_name + ':'), i+1, 0)
                param_edit = QLineEdit()
                param_edit.setValidator(QDoubleValidator())
                self.params.append(param_edit)
                self.grid.addWidget(param_edit, i+1, 1)




class RangeEdit(QWidget):
    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout()
        
        self.lb = QDoubleSpinBox()
        self.lb.setRange(1.0, 20.0)
        self.lb.setSingleStep(0.5)
        self.lb.setDecimals(1)
        #self.lb.valueChanged.connect(self.check_lower_bound)
        hbox.addWidget(self.lb)

        hbox.addWidget(QLabel('-'))

        self.ub = QDoubleSpinBox()
        self.ub.setRange(1.0, 20.0)
        self.ub.setSingleStep(0.5)
        self.ub.setDecimals(1)
        #self.ub.valueChanged.connect(self.check_upper_bound)
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
    

    def check_lower_bound(self):
        if self.unbalanced:
            self.lb.setValue(self.ub.value())
    

    def check_upper_bound(self):
        if self.unbalanced:
            self.ub.setValue(self.lb.value())
    

    def set_values(self, lb, ub):
        # NB This is incompatible with check_lower_bound
        # because changing value of lb can make it temporarily larger than ub, which is prevented by check_lower_bound
        self.lb.setValue(lb)
        self.ub.setValue(ub)
    

    def set_unit(self, unit):
        self.lb.setSuffix(' ' + unit)
        self.ub.setSuffix(' ' + unit)