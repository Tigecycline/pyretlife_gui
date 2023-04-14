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
from constants import SPECIES_NAMES, LINE_SPECS




class SpeciesEditor(QWidget):
    def __init__(self, config=None):
        super().__init__()
        self.table = SpeciesTable(config)

        self.buttons = {name: QPushButton(name) for name in ['Add', 'Edit', 'Remove', 'Clear']}
        self.buttons['Add'].clicked.connect(self.table.add_entry)
        self.buttons['Edit'].clicked.connect(self.table.edit_current_entry)
        self.buttons['Remove'].clicked.connect(self.table.remove_current_entry)
        self.buttons['Clear'].clicked.connect(self.table.confirm_clear)
        
        button_column = QVBoxLayout()
        button_column.setAlignment(Qt.AlignmentFlag.AlignCenter)
        for b in self.buttons.values():
            button_column.addWidget(b)

        layout = QHBoxLayout()
        layout.addWidget(self.table)
        layout.addLayout(button_column)
        self.setLayout(layout)
    

    def read_from_config(self, config):
        self.table.read_from_config(config)
    

    def write_to_config(self, config):
        self.table.write_to_config(config)




class SpeciesTable(QTableWidget):
    COLUMNS = ['Formula', 'Name', 'Lines', 'Prior', 'Truth'] #{name: i for i, name in enumerate(['Formula', 'Name', 'Lines', 'Prior', 'Truth'])}

    def __init__(self, config):
        super().__init__(0, len(SpeciesTable.COLUMNS))
        self.setDragEnabled(True) # todo?: allow reordering via drag & drop

        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers) # diable direct editing

        self.setHorizontalHeaderLabels(SpeciesTable.COLUMNS)
        header = self.horizontalHeader()
        #header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        
        #self.setSortingEnabled(True) # leads to problems when refreshing the table
        #self.setShowGrid(False)

        self.read_from_config(config)


    def __getitem__(self, key):
        # NB don't use itemAt since its coordinates are pixels
        return self.item(key[0], key[1]).text()
    

    def __setitem__(self, key, attr):
        self.setItem(key[0], key[1], QTableWidgetItem(attr))


    def refresh(self):
        self.setRowCount(0)
        #assert(self.species_dict is not None)
        for i, species in enumerate(self.species_list):
            self.insertRow(i)
            self[i,0] = species.formula
            self[i,1] = SPECIES_NAMES[species.formula]
            self[i,2] = '' if species.lines is None else '; '.join(species.lines)
            if species.prior_name != '(known)':
                self[i,3] = '%s(%s)' % (species.prior_name, ', '.join(species.prior_params))
            self[i,4] = species.truth
    

    def read_from_config(self, config):
        self.species_list = []
        
        for formula, info in config['CHEMICAL COMPOSITION PARAMETERS'].items():
            if formula == 'mmw_inert':
                continue
            
            prior = info.get('prior')
            if prior is None:
                prior_name = '(known)'
                prior_params = []
            else:
                prior_name = prior['kind']
                prior_params = [str(value) for value in prior['prior_specs'].values()]
            truth = str(info.get('truth', ''))
            lines = info.get('lines', [])

            species_info = SpeciesInfo()
            species_info.set_info(formula, prior_name, prior_params, truth, lines)
            self.species_list.append(species_info)
        
        self.refresh()
    

    def write_to_config(self, config):
        # Remove old species
        config['CHEMICAL COMPOSITION PARAMETERS'] = {'mmw_inert': config['CHEMICAL COMPOSITION PARAMETERS']['mmw_inert']}
        
        # Write species shown in GUI
        for species in self.species_list:
            config['CHEMICAL COMPOSITION PARAMETERS'][species.formula] = species.to_dict()

    
    def mouseDoubleClickEvent(self, event):
        self.edit_current_entry()
    

    def add_entry(self):
        add_dialog = SpeciesEditDialog(self)
        add_dialog.truth.setText('0')
        add_dialog.exec()
    

    def edit_current_entry(self):
        if self.currentRow() < 0: # currentRow returns -1 when no row is selected
            return
        edit_dialog = SpeciesEditDialog(self, self.species_list[self.currentRow()])
        edit_dialog.exec()
    

    def confirm_clear(self):
        clear_dialog = QMessageBox(self)
        clear_dialog.setText('Are you sure you want to clear all species?')
        clear_dialog.setStandardButtons(QMessageBox.No | QMessageBox.Yes)
        clear_dialog.accepted.connect(self.remove_all)
        clear_dialog.exec()


    def remove_all(self):
        self.species_list.clear()
        self.setRowCount(0)


    def remove_current_entry(self):
        self.species_list.pop(self.currentRow())
        self.removeRow(self.currentRow())




class SpeciesInfo:
    def __init__(self):
        pass
    

    def set_info(self, formula: str, prior_name: str, prior_params: list, truth: str, lines: list):
        '''
        All values should be strings (or list of strings)
        When writing to dictionary, strings are converted to other types (e.g. float) if necessary

        [Args]
            formula: chemical formula of the species
            prior_name: name of the prior distribution, use '(known)' if there is no prior
            prior_params: list of parameters in a specific order, use empty list ([]) if there is no prior
            truth: true abundance value, use empty string ('') if no truth is specified
            lines: list of corresponding line files, use empty list ([]) if no line file is used for this species
        '''
        self.formula = formula
        self.prior_name = prior_name
        self.prior_params = prior_params
        self.truth = truth
        self.lines = lines
    

    def to_dict(self):
        param_values = [float(p) for p in self.prior_params]
        truth_value = float(self.truth)
        return param_dict(self.prior_name, param_values, truth_value, self.lines)




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
    def __init__(self, parent, target=None):
        super().__init__(parent)
        self.setWindowTitle('Edit Species')
        self.parent = parent
        self.target = target

        editor_grid = QGridLayout()

        editor_grid.addWidget(QLabel('Species:'), 0, 0, 1, 2)
        editor_grid.addWidget(QLabel('Truth:'), 2, 0, 1, 1)
        
        self.formula_name = QComboBox()
        editor_grid.addWidget(self.formula_name, 1, 0, 1, 2)
        
        self.line_specs = LineSpecGroup()
        editor_grid.addWidget(self.line_specs, 0, 2, 6, 4)

        self.truth = QLineEdit()
        self.truth.setValidator(QDoubleValidator())
        editor_grid.addWidget(self.truth, 2, 1, 1, 1)

        self.prior = PriorBox()
        editor_grid.addWidget(self.prior, 3, 0, 1, 2)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        self.button_box.button(QDialogButtonBox.Ok).setText('Accept')
        self.button_box.button(QDialogButtonBox.Cancel).setText('Discard')
        self.button_box.setCenterButtons(True)
        self.button_box.accepted.connect(self.apply)
        self.button_box.rejected.connect(self.close)

        main_layout = QVBoxLayout(self)
        main_layout.addLayout(editor_grid)
        main_layout.addWidget(self.button_box)

        self.read_target_info()


    def read_target_info(self):
        # if no target, it means we are introducing a new species
        if self.target is None:
            existing_formulae = [species.formula for species in self.parent.species_list]
            # ignore species that already exist
            for formula in SPECIES_NAMES:
                if formula in existing_formulae:
                    continue
                self.formula_name.addItem(' - '.join([formula, SPECIES_NAMES[formula]]))
            self.formula_name.setCurrentIndex(-1)
            return
        
        # otherwise, we are editting an existing species, so we read its current settings
        self.formula_name.addItem(' - '.join([self.target.formula, SPECIES_NAMES[self.target.formula]]))
        self.formula_name.setCurrentIndex(0)
        self.formula_name.setEnabled(False) # the user is not allowed to change the species itself

        self.truth.setText(self.target.truth)

        if self.target.prior_name != '(known)':
            self.prior.kind.setCurrentText(self.target.prior_name)
            for i, param_value in enumerate(self.target.prior_params):
                self.prior.params[i].setText(param_value)
        
        if len(self.target.lines) == 0:
            self.line_specs.noline.setChecked(True)
        else:
            assert(len(self.target.lines) <= 2)
            for file_name in self.target.lines:
                if 'UV' in file_name:
                    self.line_specs['UV'].setCheckState(Qt.CheckState.Checked)
                else:
                    specs = file_name.split('_')[1:]
                    for spec_name, spec_value in zip(LINE_SPECS, specs):
                        self.line_specs[spec_name].setCurrentText(spec_value)
    

    def apply(self):
        formula = self.formula_name.currentText().split(' - ')[0]
        prior_name = self.prior.kind.currentText()
        prior_params = [param.text() for param in self.prior.params]
        truth = self.truth.text()
        if self.line_specs.noline.isChecked():
            lines = None
        else:
            lines = []
            line_name_tokens = [formula] + [self.line_specs[spec_name].currentText() for spec_name in LINE_SPECS]
            line_name = '_'.join(line_name_tokens[:-1])
            if line_name_tokens[-1] != LINE_SPECS['Resolution']['default']:
                # remove resolution token if it's same as default
                line_name += '_R_%s' % line_name_tokens[-1]
            lines.append(line_name)
            if self.line_specs['UV'].isChecked():
                lines.append(formula + '_UV')

        if self.target is None:
            new_species = SpeciesInfo()
            new_species.set_info(formula, prior_name, prior_params, truth, lines)
            self.parent.species_list.append(new_species)
        else:
            self.target.set_info(formula, prior_name, prior_params, truth, lines)

        self.close()
        self.parent.refresh()