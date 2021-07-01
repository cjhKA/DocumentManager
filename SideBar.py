import os
import sys
import PyQt5.sip as sip
from PyQt5.QtWidgets import QDialog,QApplication,QListWidgetItem,QWidget,QHBoxLayout,\
    QLabel,QLineEdit,QPushButton,QSpacerItem,QSizePolicy,QMessageBox,QListWidget,QListView
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal


from ShareData import sharedata


class ShowListItem(QWidget):
    sg_showListItemDelete = pyqtSignal(str)
    def __init__(self, text, parent=None):
        super(ShowListItem, self).__init__(parent=parent)
        self.text = text
        self.setup()



    def setup(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        # self.label = QLabel()
        # self.label.setText(self.text)
        # self.layout.addWidget(self.label)
        self.linedit = QLineEdit()
        self.spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.deletebtn = QPushButton("×")
        self.deletebtn.setFixedWidth(20)
        self.deletebtn.clicked.connect(self.delete)

        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.deletebtn)

    def delete(self):
        self.sg_showListItemDelete.emit(self.text)


class MyLabelShowListWidget(QListWidget):
    sg_ShowListChange = pyqtSignal()
    def __init__(self, parent = None):
        super(MyLabelShowListWidget, self).__init__(parent=parent)
        self.labelShows = sharedata.getLabelShow()
        self.setup()
        # self.setMovement(QListView.InternalMove)
        self.setDragDropMode(QListWidget.InternalMove)



    def setup(self):
        # title_item = QListWidgetItem("标题")
        # self.addItem(title_item)
        for labelshow in self.labelShows:
            self.addOne(labelshow)

    def _reset(self):
        self.clear()
        self.labelShows = ["标题"] + sharedata.getLabels()
        self.setup()

    def addOne(self, labelshow):
        temp_item = ShowListItem(labelshow)
        temp_item.sg_showListItemDelete.connect(self.clickDelete)
        t_item = QListWidgetItem(labelshow)
        t_item.setSizeHint(QtCore.QSize(200, 20))
        if labelshow not in self.labelShows:
            self.labelShows.append(labelshow)
        self.addItem(t_item)
        self.setItemWidget(t_item, temp_item)

    def clickDelete(self, label):
        for i in range(self.count()):
            t_check = self.item(i)
            if t_check.text() == label:
                self.removeItemWidget(t_check)
                sip.delete(t_check)
                break
        self.labelShows.remove(label)
        sharedata.setLabelShow(self.labelShows)
        self.sg_ShowListChange.emit()



    def dropEvent(self, event) -> None:
        super(MyLabelShowListWidget, self).dropEvent(event)
        res_list = []
        for i in range(self.count()):
            t_check = self.item(i)
            res_list.append(t_check.text())
        self.labelShows = res_list
        sharedata.setLabelShow(self.labelShows)
        self.sg_ShowListChange.emit()





class CategoryItem(QListWidgetItem):
    def __init__(self):
        super(CategoryItem, self).__init__()
    #Todo:加checkbox

class MyCategoryListWidget(QListWidget):
    def __init__(self, parent = None):
        super(MyCategoryListWidget, self).__init__(parent=parent)
    #Todo:右键菜单栏（添加，修改，删除）
    #Todo:实现拖动显示