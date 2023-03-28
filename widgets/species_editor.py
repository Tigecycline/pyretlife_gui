from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QDialog,
    QMessageBox,
    QLabel,
    QCheckBox,
    QLineEdit,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QHeaderView,
    QGroupBox
)
from PySide6.QtGui import QDoubleValidator

from widgets.util_widgets import PriorBox
from config_handler import param_dict
from constants import SPECIES_NAMES, PRIOR_PARAM_NAMES, LINE_SPECS




class SpeciesEditor(QWidget):
    def __init__(self, species_dict=None):
        super().__init__()
        self.table = SpeciesTable(species_dict)

        self.buttons = {name: QPushButton(name) for name in ['Add', 'Edit', 'Remove', 'Clear']}
        self.buttons['Add'].clicked.connect(self.table.addEntry)
        self.buttons['Edit'].clicked.connect(self.table.editCurrentEntry)
        self.buttons['Remove'].clicked.connect(self.table.removeCurrentEntry)
        self.buttons['Clear'].clicked.connect(self.table.confirmClear)
        
        button_column = QVBoxLayout()
        button_column.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for b in self.buttons.values():
            button_column.addWidget(b)

        layout = QHBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_column)
        self.setLayout(layout)




class SpeciesTable(QTableWidget):
    COLUMNS = {name: i for i, name in enumerate(['Formula', 'Name', 'Lines', 'Prior', 'Truth'])}

    def __init__(self, species_dict=None):
        super().__init__(0, len(SpeciesTable.COLUMNS))
        self.species_dict = species_dict
        if species_dict is not None:
            self.refresh()
        
        #self.setSortingEnabled(True) # leads to problems when refreshing the table!
        #self.setShowGrid(False)

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # diable direct editing

        self.setHorizontalHeaderLabels(SpeciesTable.COLUMNS)
        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)


    def __getitem__(self, key):
        # NB don't use itemAt since its coordinates are pixels
        return self.item(key[0], key[1]).text()


    def refresh(self):
        self.removeAll()
        #assert(self.species_dict is not None)
        for species in self.species_dict:
            if species == 'settings':
                continue
            
            attributes = [species, SPECIES_NAMES[species]]
            lines = self.species_dict[species].get('lines', [])
            attributes.append('; '.join(lines))
            prior = self.species_dict[species].get('prior')
            if prior is None:
                attributes.append('(known)')
            else:
                attributes.append('%s(%s)' % (prior['kind'], ', '.join(str(p) for p in prior['prior_specs'].values())))
            truth = self.species_dict[species].get('truth')
            attributes.append('' if truth is None else str(truth))

            new_row = self.rowCount()
            self.insertRow(new_row)
            self.setEntry(new_row, attributes)

    
    def setEntry(self, row, attributes):
        for col, attr in enumerate(attributes):
            self.setItem(row, col, QTableWidgetItem(attr))

    
    def mouseDoubleClickEvent(self, event):
        self.editCurrentEntry()
    

    def addEntry(self):
        add_dialog = SpeciesEditDialog(self)
        add_dialog.truth.setText('0')
        add_dialog.exec()
        self.refresh()
    

    def editCurrentEntry(self):
        if self.currentRow() < 0: # currentRow returns -1 when no row is selected
            return
        edit_dialog = SpeciesEditDialog(self, self[self.currentRow(), 0])
        edit_dialog.exec()
        self.refresh()
        '''
        row = self.currentRow()
        for col, attr in enumerate(attributes):
            self.item(row, col).setText(attr)
        '''
    

    def confirmClear(self):
        clear_dialog = QMessageBox(self)
        clear_dialog.setText('Are you sure you want to clear all species?')
        clear_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        clear_dialog.accepted.connect(self.removeAll)
        clear_dialog.exec()


    def removeAll(self):
        self.setRowCount(0)


    def removeCurrentEntry(self):
        self.removeRow(self.currentRow())
    

    #def sort(self, ascending):
    #    if ascending:
    #        self.sortItems(0, Qt.SortOrder.AscendingOrder)
    #    else:
    #        self.sortItems(0, Qt.SortOrder.DescendingOrder)




class LineSpecGroup(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle('Line Specifications')
        grid = QGridLayout()
        self.labels = [QLabel(spec_name) for spec_name in LINE_SPECS]
        self.specs = {}

        for i, spec_name in enumerate(LINE_SPECS):
            grid.addWidget(self.labels[i], i, 0)
            self[spec_name] = QComboBox()
            for option in LINE_SPECS[spec_name]['options']:
                self[spec_name].addItem(option)
            default_value = LINE_SPECS[spec_name].get('default')
            if default_value is not None:
                self[spec_name].setCurrentText(default_value)
            grid.addWidget(self[spec_name], i, 1)
        
        self['UV'] = QCheckBox('UV')
        grid.addWidget(self['UV'], len(LINE_SPECS), 0)

        self.noline = QCheckBox('No Line')
        self.noline.stateChanged.connect(self.adapt_noline)
        grid.addWidget(self.noline, len(LINE_SPECS), 1)

        self.setLayout(grid)


    def __getitem__(self, key):
        return self.specs[key]
    

    def __setitem__(self, key, value):
        self.specs[key] = value
    

    def adapt_noline(self, state):
        enable = Qt.CheckState(state) == Qt.CheckState.Unchecked
        for spec_widget in self.specs.values():
            spec_widget.setEnabled(enable)
        for label in self.labels:
            label.setEnabled(enable)





class SpeciesEditDialog(QDialog):
    def __init__(self, parent, original_species=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Species')
        self.parent = parent
        self.species_dict = self.parent.species_dict
        self.original_species = original_species

        editor_grid = QGridLayout()

        editor_grid.addWidget(QLabel('Species:'), 0, 0, 1, 2)
        editor_grid.addWidget(QLabel('Truth:'), 2, 0, 1, 1)
        
        self.species = QComboBox()
        for formula in SPECIES_NAMES:
            fullname = ' - '.join([formula, SPECIES_NAMES[formula]])
            # ignore species that already exist
            if formula not in self.species_dict:
                self.species.addItem(fullname)
            elif formula == self.original_species:
                self.species.addItem(fullname)
                self.species.setCurrentText(fullname)
        editor_grid.addWidget(self.species, 1, 0, 1, 2)
        
        self.line_specs = LineSpecGroup()
        editor_grid.addWidget(self.line_specs, 0, 2, 6, 4)

        self.truth = QLineEdit()
        self.truth.setValidator(QDoubleValidator())
        editor_grid.addWidget(self.truth, 2, 1, 1, 1)

        self.prior = PriorBox()
        editor_grid.addWidget(self.prior, 3, 0, 1, 2)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Abort | QDialogButtonBox.Save)
        self.button_box.button(QDialogButtonBox.Abort).setText('Discard')
        self.button_box.setCenterButtons(True)
        self.button_box.accepted.connect(self.apply)
        self.button_box.rejected.connect(self.close)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(editor_grid)
        main_layout.addWidget(self.button_box)

        if self.original_species is not None:
            self.readOriginalSpecies()


    def readOriginalSpecies(self):
        truth = self.species_dict[self.original_species].get('truth')
        if truth is not None:
            self.truth.setText(str(truth))

        prior_dict =  self.species_dict[self.original_species].get('prior', '(known)')
        if prior_dict != '(known)':
            self.prior.kind.setCurrentText(prior_dict['kind'])
            for param_name in self.prior.params:
                self.prior.params[param_name].setText(str(prior_dict['prior_specs'][param_name]))
        
        lines = self.species_dict[self.original_species].get('lines')
        if lines is None:
            self.line_specs.noline.setChecked(True)
        else:
            for line_name in lines:
                if 'UV' in line_name:
                    self.line_specs['UV'].setCheckState(Qt.CheckState.Checked)
                else:
                    specs = line_name.split('_')[1:]
                    for spec_name, spec_value in zip(LINE_SPECS, specs):
                        self.line_specs[spec_name].setCurrentText(spec_value)
    

    def apply(self):
        current_species = self.species.currentText().split(' - ')[0]
        if self.original_species is not None and self.original_species != current_species:
            del self.species_dict[self.original_species]
        
        truth = float(self.truth.text())
        prior = self.prior.kind.currentText()
        params = None if prior == '(known)' else [float(param.text()) for param in self.prior.params.values()]
        
        if self.line_specs.noline.isChecked():
            lines = None
        else:
            lines = []
            line_name_tokens = [current_species] + [self.line_specs[spec_name].currentText() for spec_name in LINE_SPECS]
            line_name = '_'.join(line_name_tokens[:-1])
            if line_name_tokens[-1] != LINE_SPECS['Resolution']['default']:
                # remove resolution token if it's same as default
                line_name += '_R_%s' % line_name_tokens[-1]
            lines.append(line_name)
            if self.line_specs['UV'].isChecked():
                lines.append(current_species + '_UV')

        self.species_dict[current_species] = param_dict(prior, params, truth, lines)
        self.close()