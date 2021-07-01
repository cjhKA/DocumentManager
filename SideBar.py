import os
import sys
import PyQt5.sip as sip
from PyQt5.QtWidgets import QDialog,QApplication,QListWidgetItem,QWidget,QHBoxLayout,\
    QLabel,QLineEdit,QPushButton,QSpacerItem,QSizePolicy,QMessageBox,QListWidget, QCheckBox
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


class StaticItem(QWidget):
    def __init__(self, text, num, parent=None):
        super(StaticItem, self).__init__(parent=parent)
        self.text = text
        self.num = num
        self.setUp()

    def setNum(self, num):
        self.num = num
        self.label.setText(self.text + "({})".format(str(self.num)))

    def setUp(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.label = QLabel()
        self.label.setText(self.text + "({})".format(str(self.num)))
        self.layout.addWidget(self.label)
        self.linedit = QLineEdit()
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addItem(self.spacer)


class CategoryItem(StaticItem):
    editSig = pyqtSignal(str, str)
    deleteSig = pyqtSignal(str)

    def __init__(self, text, num, parent=None):
        super(CategoryItem, self).__init__(text, num, parent=parent)

    def setUp(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.label = QLabel()
        self.label.setText(self.text + "({})".format(str(self.num)))
        self.layout.addWidget(self.label)
        self.linedit = QLineEdit()
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editbtn = QPushButton("编辑")
        self.editbtn.setFixedWidth(40)
        self.editbtn.clicked.connect(self.edit)
        self.deletebtn = QPushButton("×")
        self.deletebtn.setFixedWidth(20)
        self.deletebtn.clicked.connect(self.delete)
        self.confirmbtn = QPushButton("确定")
        self.confirmbtn.setFixedWidth(40)
        self.confirmbtn.clicked.connect(self.confirm)
        self.layout.addItem(self.spacer)
        self.layout.addWidget(self.editbtn)
        self.layout.addWidget(self.deletebtn)

    def edit(self):
        self.layout.replaceWidget(self.label, self.linedit)
        self.layout.replaceWidget(self.editbtn, self.confirmbtn)
        self.label.setVisible(False)
        self.editbtn.setVisible(False)
        self.linedit.setVisible(True)
        self.confirmbtn.setVisible(True)
        self.deletebtn.setEnabled(False)
        self.linedit.setText(self.text)
        self.origlabel = self.text

    def confirm(self):
        t_label = self.linedit.text()
        if t_label != "" and (self.text == t_label or t_label not in sharedata.getCategory().keys()) and t_label not in ["全部","其他"]:

            self.layout.replaceWidget(self.linedit, self.label)
            self.layout.replaceWidget(self.confirmbtn, self.editbtn)
            self.label.setVisible(True)
            self.editbtn.setVisible(True)
            self.linedit.setVisible(False)
            self.confirmbtn.setVisible(False)
            self.deletebtn.setEnabled(True)
            self.text = t_label
            self.label.setText(t_label + "({})".format(str(self.num)))
            self.editSig.emit(self.origlabel, t_label)

    def delete(self):
        self.deleteSig.emit(self.text)


class MyCategoryListWidget(QListWidget):
    sg_showrow = pyqtSignal(str)
    def __init__(self, parent = None):
        super(MyCategoryListWidget, self).__init__(parent=parent)
        self.setup()
        self.setDragDropMode(QListWidget.InternalMove)
        self.itemClicked.connect(self.rowClicked)
        self.setCurrentRow(0)



    def setup(self):

        order = sharedata.getCategoryOrder()

        for key in order:
            if key == "全部" or key == "其他":
                temp_item = StaticItem(key, -1)
                t_item = QListWidgetItem()
                t_item.setSizeHint(QtCore.QSize(200, 20))
                self.addItem(t_item)
                self.setItemWidget(t_item, temp_item)
            else:
                self.addOne(key, -1)
        self.updateNum()

    def updateNum(self):
        all_category = sharedata.getCategory()
        for i in range(self.count()):
            t_check = self.item(i)
            widget = self.itemWidget(t_check)
            if widget.text == "全部":
                widget.setNum(len(list(sharedata.getAllLabelData().keys())))
            elif widget.text == "其他":
                t_list = []
                t_all = sharedata.getAllName2Category()
                for key in t_all:
                    if t_all[key] == "##OTHERS##":
                        t_list.append(key)
                widget.setNum(len(t_list))
            else:
                widget.setNum(len(all_category[widget.text]))


    def addOne(self, category, num=0):
        temp_item = CategoryItem(category, num)
        temp_item.deleteSig.connect(self._delete)
        temp_item.editSig.connect(self._edit)
        t_item = QListWidgetItem()
        t_item.setSizeHint(QtCore.QSize(200, 20))
        self.addItem(t_item)
        self.setItemWidget(t_item, temp_item)

    def _delete(self, category):
        t_category = sharedata.getCategory()

        for i in range(self.count()):
            t_check = self.item(i)
            if self.itemWidget(t_check).text == category:
                self.takeItem(i)
                sip.delete(t_check)
                break

        t_category.pop(category)
        sharedata.setCategory(t_category)
        self.rowClicked()
        self.updateNum()


    def _edit(self, orig, dist):
        n_category = sharedata.getCategory()
        if orig in n_category.keys():
            t_list = n_category[orig]
            del n_category[orig]
            n_category[dist] = t_list
            sharedata.setCategory(n_category)
        self.getNowOrder()


    def dropEvent(self, event) -> None:
        super(MyCategoryListWidget, self).dropEvent(event)
        self.getNowOrder()

    def getNowOrder(self):
        order = []
        for i in range(self.count()):
            t_check = self.item(i)
            order.append(self.itemWidget(t_check).text)

        sharedata.setCategoryOrder(order)

    def rowClicked(self):
        self.getNowOrder()
        self.sg_showrow.emit(sharedata.getCategoryOrder()[self.currentRow()])
