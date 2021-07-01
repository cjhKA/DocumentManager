import os
import sys
import PyQt5.sip as sip
from PyQt5.QtWidgets import QDialog,QApplication,QListWidgetItem,QWidget,QHBoxLayout,\
    QLabel,QLineEdit,QPushButton,QSpacerItem,QSizePolicy,QMessageBox
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal


from UI.Details import Ui_Dialog
from ShareData import sharedata


class MyListItem(QWidget):
    editSig = pyqtSignal(str,str)
    deleteSig = pyqtSignal(str)

    def __init__(self, text,parent=None):
        super(MyListItem, self).__init__(parent=parent)
        self.text = text
        self.setUp()




    def setUp(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.label = QLabel()
        self.label.setText(self.text)
        self.layout.addWidget(self.label)
        self.linedit = QLineEdit()
        self.spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.editbtn = QPushButton("编辑")
        self.editbtn.setFixedWidth(40)
        self.editbtn.clicked.connect(self.edit)
        self.deletebtn = QPushButton("删除")
        self.deletebtn.setFixedWidth(40)
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
        self.linedit.setText(self.label.text())
        self.origlabel = self.label.text()

    def confirm(self):
        t_label = self.linedit.text()
        if t_label != "" and (self.label.text() == t_label or t_label not in sharedata.getLabels()):
            self.editSig.emit(self.origlabel, t_label)
            self.layout.replaceWidget(self.linedit, self.label)
            self.layout.replaceWidget(self.confirmbtn, self.editbtn)
            self.label.setVisible(True)
            self.editbtn.setVisible(True)
            self.linedit.setVisible(False)
            self.confirmbtn.setVisible(False)
            self.text = t_label
            self.label.setText(t_label)


    def delete(self):
        self.deleteSig.emit(self.label.text())



class DetailDialog(QDialog,Ui_Dialog):

    labelChange = pyqtSignal()

    def __init__(self,parent=None):
        super(DetailDialog,self).__init__(parent)
        self.setupUi(self)
        self.layoutList = []
        self.name = ""

        self.t_layout = QHBoxLayout()
        self.t_label = QLabel("标题:")
        self.t_linedit = QLineEdit()
        self.t_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.t_linedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.t_layout.addWidget(self.t_label)
        self.t_layout.addWidget(self.t_linedit)
        self.verticalLayout.insertLayout(len(self.layoutList), self.t_layout)
        self.layoutList.append(self.t_layout)


        self.loadLabel()
        self.setWindowTitle("文献详情")
        self.setWindowIcon(QIcon("./media/ustb.ico"))

        # self.setUp("Name")



    def setUp(self, name):
        self.name = name
        self.layoutList[0].itemAt(1).widget().setText(name)
        self.path = os.path.join(sharedata.getRichTextRoot(),self.name+".html")
        self.loadRichText(self.path)
        self.loadLabelData()


    @QtCore.pyqtSlot()
    def on_btn_newLabel_clicked(self):
        t_label = self.ledit_newLabel.text()
        t_labels = sharedata.getLabels()
        if t_label != "" and t_label not in t_labels:
            t_labels.append(t_label)
            sharedata.setLabels(t_labels)
            self.newLabel(t_label)
            self.labelChange.emit()




    def newLabel(self, t_label):
        #更新左侧列表
        mylistitem = MyListItem(t_label)
        mylistitem.editSig.connect(self.editLabel)
        mylistitem.deleteSig.connect(self.deleteLabel)
        t_item = QListWidgetItem()
        t_item.setSizeHint(QtCore.QSize(200, 30))
        self.listwgt_labelList.addItem(t_item)
        self.listwgt_labelList.setItemWidget(t_item, mylistitem)

        #更新右侧键值对形式的行
        self.t_layout = QHBoxLayout()
        self.t_label = QLabel(t_label + ":")
        self.t_linedit = QLineEdit()
        self.t_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.t_linedit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.t_layout.addWidget(self.t_label)
        self.t_layout.addWidget(self.t_linedit)
        self.verticalLayout.insertLayout(len(self.layoutList), self.t_layout)
        self.layoutList.append(self.t_layout)



    def editLabel(self, orig, new):
        t_labels = sharedata.getLabels()
        i = t_labels.index(orig)
        t_labels[i] = new
        sharedata.setLabels(t_labels)

        for layout in self.layoutList:
            if layout.itemAt(0).widget().text()[:-1] == orig:
                layout.itemAt(0).widget().setText(new+":")
                break

        self.labelChange.emit()



    def deleteLabel(self, target):
        t_labels = sharedata.getLabels()
        i = t_labels.index(target)
        t_labels.pop(i)
        sharedata.setLabels(t_labels)


        self.listwgt_labelList.takeItem(i)


        for i in range(len(self.layoutList)):
            if self.layoutList[i].itemAt(0).widget().text()[:-1] == target:
                # self.layoutList[i].delete()
                label = self.verticalLayout.itemAt(i).layout().itemAt(0).widget()
                edit = self.verticalLayout.itemAt(i).layout().itemAt(1).widget()

                self.verticalLayout.removeItem(self.layoutList[i])
                sip.delete(label)
                sip.delete(edit)


                self.layoutList.pop(i)
                break


        self.labelChange.emit()

    # def dontEdit(self):
    #     sip.delete(self.verticalLayout_2)
    #     self.listwgt_labelList.setVisible(False)
    #     self.btn_newLabel.setVisible(False)
    #     self.ledit_newLabel.setVisible(False)
    #     for layout in self.layoutList:
    #         layout.itemAt(1).widget().setReadOnly(True)
    #     self.richTextWindow.text_edit.setReadOnly(True)

    def loadLabel(self):
        t_labels = sharedata.getLabels()
        for label in t_labels:
            self.newLabel(label)

    def loadLabelData(self):
        t_dict = sharedata.getLabelData(self.name)
        for key in t_dict:
            for layout in self.layoutList:
                if layout.itemAt(0).widget().text()[:-1] == key:
                    layout.itemAt(1).widget().setText(t_dict[key])

    def loadRichText(self, path):
        if os.path.isfile(path):
            with open(path, "r") as f:
                text = f.readlines()
                cache = ""
                for line in text:
                    cache += line
                self.richTextWindow.loadHtml(cache)
                f.close()

    def saveData(self):
        new_name = self.layoutList[0].itemAt(1).widget().text()
        if new_name == "":
            QMessageBox().warning(self,"警告","标题不能为空！",QMessageBox.Ok)
            return False
        if new_name != self.name and new_name in sharedata.getAllLabelData().keys():
            QMessageBox().warning(self,"警告","标题不能重复！",QMessageBox.Ok)
            return False

        if os.path.isfile(os.path.join(sharedata.getRichTextRoot(), self.name + ".html")):
            os.remove(os.path.join(sharedata.getRichTextRoot(), self.name + ".html"))
        self.path = os.path.join(sharedata.getRichTextRoot(), new_name + ".html")
        text = self.richTextWindow.toHtml()
        with open(self.path, "w") as f:
            f.write(text)
            f.close()

        t_dict = {}
        for layout in self.layoutList[1:]:
            key = layout.itemAt(0).widget().text()[:-1]
            value = layout.itemAt(1).widget().text()
            t_dict[key] = value
        sharedata.removeLabelData(self.name)
        sharedata.setLabelData(new_name, t_dict)
        self.name = new_name
        sharedata.saveShareData()

        self.labelChange.emit()

        return True


    def closeEvent(self, a0) -> None:
        if self.saveData():
            a0.accept()
            self.labelChange.emit()
        else:
            reply = QMessageBox().warning(self, "警告", "是否放弃修改！", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.Yes:
                a0.accept()
                self.labelChange.emit()
            else:
                a0.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myshow = DetailDialog()
    myshow.show()
    sys.exit(app.exec_())