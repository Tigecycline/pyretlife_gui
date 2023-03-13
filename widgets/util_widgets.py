from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QAbstractItemView
)




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
    


