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
    QAbstractItemView,
    QHBoxLayout,
    QGridLayout
)
#from PySide6.QtGui import QDoubleValidator

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
    def __init__(self, title='Prior'):
        super().__init__(title)
        
        self.grid = QGridLayout()

        self.kind = QComboBox()
        self.kind.addItems(PRIOR_PARAM_NAMES)
        self.kind.currentTextChanged.connect(self.adapt_param_names)
        self.grid.addWidget(self.kind, 0, 0, 1, 2)
        
        self.params = {}

        self.setLayout(self.grid)
    

    def __getitem__(self, key):
        return self.params[key]


    def adapt_param_names(self):
        # remove old parameter widgets
        # On deleting widgets from layout:
        # - For unknown reason, deleteLater alone works for MainWindow, but not for Dialogs
        # - For dialogs, removeWidget (or removeItem) has to be performed as well to make the widget disappear
        # - Widgets other than MainWindow and Dialog were not tested
        # - Using only removeWidget seems to move the widget out of the layout, but the widget remains in the window, at the lower left corner
        # - Using removeWidget before applying the layout (with setLayout) crashes the program ("segmentation fault (core dumped)")
        for i in range(len(self.params)):
            for j in range(2):
                item = self.grid.itemAtPosition(i+1, j)
                item.widget().deleteLater()
                self.grid.removeItem(item)
        
        # remove old parameters (or keep them)
        self.params = {}

        new_prior = self.kind.currentText()
        if new_prior == '(known)':
            return
        for i, param_name in enumerate(PRIOR_PARAM_NAMES[new_prior]):
            self.grid.addWidget(QLabel(param_name + ':'), i+1, 0)
            self.params[param_name] = QLineEdit()
            self.grid.addWidget(self.params[param_name], i+1, 1)




class RangeEdit(QWidget):
    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout()
        
        self.lb = QDoubleSpinBox()
        self.lb.setRange(1.0, 20.0)
        self.lb.setSingleStep(0.5)
        self.lb.valueChanged.connect(self.check_lower_bound)
        hbox.addWidget(self.lb)

        hbox.addWidget(QLabel('-'))

        self.ub = QDoubleSpinBox()
        self.ub.setRange(1.0, 20.0)
        self.ub.setSingleStep(0.5)
        self.ub.valueChanged.connect(self.check_upper_bound)
        hbox.addWidget(self.ub)

        self.setLayout(hbox)
    

    @property
    def unbalanced(self):
        return self.lb.value() > self.ub.value()
    

    def check_lower_bound(self):
        if self.unbalanced:
            self.lb.setValue(self.ub.value())
    

    def check_upper_bound(self):
        if self.unbalanced:
            self.ub.setValue(self.lb.value())