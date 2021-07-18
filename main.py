import glob
import re
import os
import shutil
import sys

import xlwt
import xlrd
from bs4 import BeautifulSoup as bs
from PyQt5.QtWidgets import QMainWindow,QApplication,QTableWidgetItem,\
    QAbstractItemView, QMessageBox, QFileDialog, QMenu
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon, QCursor

from UI.MainWindow import Ui_MainWindow
from DetailWindow import DetailDialog

from ShareData import sharedata


class DocumentManagerMainWindow(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super(DocumentManagerMainWindow,self).__init__(parent)
        self.setupUi(self)
        self.setUp()
        self.setWindowTitle("文献管理")
        self.setWindowIcon(QIcon("./media/ustb.ico"))

        # self.setWindowIcon(sharedata.icon)

    def setUp(self):
        self.table_document.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table_document.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_document.setSortingEnabled(True)
        self.table_document.doubleClicked.connect(self.on_btn_editDocument_clicked)
        self.table_document.setContextMenuPolicy(3)
        self.table_document.customContextMenuRequested[QtCore.QPoint].connect(self.createMenu)

        self.listWidget_labelshow.sg_ShowListChange.connect(self.on_btn_search_clicked)
        self.listWidget_category.sg_showrow.connect(self.showCategory)


        self.n_category = list(sharedata.getAllLabelData().keys())
        self.loadLabelList(list(sharedata.getAllLabelData().keys()))
        self.table_document.horizontalHeader().sectionClicked.connect(self.getHeaderClicked)
        self.headclicked = ""

    def getHeaderClicked(self, index):
        self.headclicked = sharedata.getLabelShow()[index]
        pass

    def loadLabelList(self, name_list):

        sortColumnName = "标题"
        sortColumnState = QtCore.Qt.AscendingOrder
        sortColumnNum = self.table_document.horizontalHeader().sortIndicatorSection()
        if sortColumnNum < self.table_document.columnCount():
            sortColumnNum = self.headclicked
            sortColumnState = self.table_document.horizontalHeader().sortIndicatorOrder()

        self.table_document.clear()
        self.table_document.setSortingEnabled(False)
        dist_list = []
        for name in name_list:
            if name in self.n_category:
                dist_list.append(name)
        name_list = dist_list
        self.name_list = dist_list
        all_labelData = sharedata.getAllLabelData()
        # labels = sharedata.getLabels()
        labels = sharedata.getLabelShow()

        self.table_document.setColumnCount(len(labels))
        self.table_document.setHorizontalHeaderLabels(labels)
        self.cbbox_searchTerm.clear()
        self.cbbox_searchTerm.addItems(labels)

        self.comboBox_selectlabel.clear()
        for label in ["标题"]+sharedata.getLabels():
            if label not in sharedata.getLabelShow():
                self.comboBox_selectlabel.addItem(label)



        self.table_document.setRowCount(len(name_list))
        for i in range(len(name_list)):
            name = name_list[i]
            t_dict = all_labelData[name]
            name_item = QTableWidgetItem(name)
            if "标题" in labels:
                self.table_document.setItem(i, labels.index("标题"), name_item)
            for key in t_dict:
                if key not in labels:
                    continue
                if key == "标题":
                    continue
                t_item = QTableWidgetItem(t_dict[key])
                self.table_document.setItem(i, labels.index(key), t_item)

        print(self.table_document.horizontalHeaderItem(0).text())
        self.table_document.setSortingEnabled(True)
        if sortColumnName != "" and sortColumnName in labels:
            self.table_document.sortByColumn(labels.index(sortColumnName), sortColumnState)



    @QtCore.pyqtSlot()
    def on_btn_newDocument_clicked(self):
        self.DetailWindow = DetailDialog()
        self.DetailWindow.labelChange.connect(self.on_btn_search_clicked)
        self.DetailWindow.show()


    @QtCore.pyqtSlot()
    def on_btn_editDocument_clicked(self):
        if self.table_document.currentRow() != -1:
            self.DetailWindow = DetailDialog()
            self.DetailWindow.setUp(self.table_document.item(self.table_document.currentRow(), sharedata.getLabelShow().index("标题")).text())
            self.DetailWindow.labelChange.connect(self.on_btn_search_clicked)
            self.DetailWindow.show()

    @QtCore.pyqtSlot()
    def on_btn_deleteDocument_clicked(self):
        if self.table_document.currentRow() != -1:
            reply = QMessageBox().warning(self, "警告", "是否确定删除该文档！", QMessageBox.Yes|QMessageBox.No)
            if reply == QMessageBox.Yes:
                name = self.table_document.item(self.table_document.currentRow(), 0).text()
                self.table_document.removeRow(self.table_document.currentRow())
                sharedata.removeLabelData(name)
                sharedata.saveShareData()
                t_path = os.path.join(sharedata.getRichTextRoot(),name+".html")
                if os.path.isfile(t_path):
                    with open(t_path, "r") as f:
                        cache = ""
                        for line in f.readlines():
                            cache += line

                        soup = bs(cache, "html.parser")
                        img_list = soup.find_all("img")
                        for img in img_list:
                            url = img.get("src")
                            if os.path.isfile(url):
                                os.remove(url)
                        document_list = soup.find_all("a")
                        for a in document_list:
                            url = a.get("href")
                            if os.path.isfile(url):
                                os.remove(url)
                        f.close()
                    os.remove(t_path)


    @QtCore.pyqtSlot()
    def on_btn_exportDocument_clicked(self):
        dist_dir = QFileDialog.getExistingDirectory()
        if dist_dir == "":
            return
        labels = ["标题"] + sharedata.getLabels()
        f = xlwt.Workbook()
        sheet = f.add_sheet("sheet1", cell_overwrite_ok= True)
        for i in range(len(labels)):
            sheet.write(0,i,labels[i])

        labeldata = sharedata.getAllLabelData()
        # keylist = list(labeldata.keys())
        keylist = self.on_btn_search_clicked()
        #导出到excel中
        for i in range(len(keylist)):
            name = keylist[i]
            sheet.write(i+1,0,name)
            data = labeldata[name]
            datakeys = list(data.keys())
            for j in range(len(datakeys)):
                key = datakeys[j]
                if key in labels:
                    sheet.write(i+1,labels.index(key),data[key])
        f.save(os.path.join(dist_dir,"导出统计.xls"))


        #导出到html中

        for filename in keylist:
            file = os.path.join(sharedata.getRichTextRoot(),filename+".html")
            filename = os.path.split(file)[1].split(".")[0]
            if filename not in keylist:
                continue
            data = labeldata[filename]
            if os.path.isfile(file):
                with open(file, "r") as sf:
                    with open(os.path.join(dist_dir,filename+".html"),"w") as df:
                        count = 0
                        for line in sf.readlines():
                            df.write(line)
                            if count == 3:
                                df.write("<p>{}:{}</p>".format("标题",filename))
                                for label in labels[1:]:
                                    value = ""
                                    if label in data.keys():
                                        value = data[label]
                                    df.write("<p>{}:{}</p>".format(label,value))
                                df.write("<p>{}</p>".format("-" * 20))


                            count += 1
                        df.close()
                    sf.close()
            else:
                with open(os.path.join(dist_dir, filename + ".html"), "w") as df:
                    head = """
                    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
                    <html><head><meta name="qrichtext" content="1" /><style type="text/css">
                    p, li { white-space: pre-wrap; }
                    </style></head><body style=" font-family:'SimSun'; font-size:9pt; font-weight:400; font-style:normal;">
                    """
                    df.write(head)
                    df.write("<p>{}:{}</p>".format("标题", filename))
                    for label in labels[1:]:
                        value = ""
                        if label in data.keys():
                            value = data[label]
                        df.write("<p>{}:{}</p>".format(label, value))
                    df.write("<p>{}</p>".format("-"*20))
                    tail = """
                    </body></html>
                    """
                    df.write(tail)
                    df.close()

        #补充html中的图片和文件
        os.makedirs(os.path.join(dist_dir,"Data/Image"), exist_ok=True)
        os.makedirs(os.path.join(dist_dir,"Data/Document"), exist_ok=True)

        fileList = glob.glob(sharedata.getRichTextRoot()+"*.html")
        for file in fileList:
            if os.path.split(file)[-1].split('.')[0] not in keylist:
                continue
            with open(file, "r") as f:
                cache = ""
                for line in f.readlines():
                    cache += line

                soup = bs(cache, "html.parser")
                img_list = soup.find_all("img")
                for img in img_list:
                    url = img.get("src")
                    if os.path.isfile(url):
                        shutil.copy(url, os.path.join(dist_dir,"Data/Image"))
                document_list = soup.find_all("a")
                for a in document_list:
                    url = a.get("href")
                    if os.path.isfile(url):
                        shutil.copy(url, os.path.join(dist_dir,"Data/Document"))
                f.close()







        os.system("explorer.exe %s" % dist_dir.replace("/","\\"))


    @QtCore.pyqtSlot()
    def on_btn_inportDocument_clicked(self):
        excel_file,_ = QFileDialog.getOpenFileName(filter="EXCEL File(*.xls *.xlsx)")
        if excel_file == "":
            return
        book = xlrd.open_workbook(excel_file)

        sheet = book.sheets()[0]
        nrows = sheet.nrows
        ncols = sheet.ncols

        all_label_data = sharedata.getAllLabelData()
        names = list(all_label_data.keys())


        repeat_names = []
        for name in sheet.col_values(0)[1:]:
            if name in names:
                repeat_names.append(name)

        if "" in sheet.col_values(0)[1:]:
            reply = QMessageBox().warning(self, "警告", "标题不能为空！", QMessageBox.Yes)
            return

        if repeat_names != []:
            reply = QMessageBox().warning(self, "警告", "存在文件名重复！\n{}".format(";".join(repeat_names)), QMessageBox.Yes)
            return

        for i in range(nrows)[1:]:
            t_dict = {}
            for j in range(ncols)[1:]:
                key = str(sheet.cell(0,j).value)
                n_labels = sharedata.getLabels()
                if key not in n_labels:
                    sharedata.setLabels(n_labels+[key])
                value = str(sheet.cell(i,j).value)
                t_dict[key] = value
            sharedata.setLabelData(str(sheet.cell(i,0).value), t_dict)
            sharedata.saveShareData()


        self.on_btn_search_clicked()

        # excel_dir = os.path.split(excel_file)[0]
        # data_dir = os.path.join(excel_dir, "Data")
        # html_paths = glob.glob(os.path.join(excel_dir,"*.html"))
        # if os.path.isdir(data_dir) and html_paths != []:
        #     reply = QMessageBox().information(self, "提示", "已检测到文本及数据是否同时导入？", QMessageBox.Yes|QMessageBox.No)
        #     if reply == QMessageBox.Yes:
        #         shutil.copytree(data_dir, './Data')
        #         for html_path in html_paths:
        #             shutil.copy(html_path, os.path.join(sharedata.getRichTextRoot(),os.path.split(html_path)[-1]))




    @QtCore.pyqtSlot()
    def on_btn_newTerm_clicked(self):
        t_label = self.cbbox_searchTerm.currentText()
        t_text = self.lineedit_searchText.text()
        if t_text != "":
            d_text = t_text + "; "+t_label+":"
        else:
            d_text = t_label+":"
        self.lineedit_searchText.setText(d_text)

    @QtCore.pyqtSlot()
    def on_btn_clearTerm_clicked(self):
        self.lineedit_searchText.setText("")

    @QtCore.pyqtSlot()
    def on_btn_search_clicked(self):
        allLabelData = sharedata.getAllLabelData()
        t_text = self.lineedit_searchText.text()
        accept_names = []

        if ":" in t_text:
            search_dict = {}
            for text in t_text.split(";"):
                try:
                    key,value = text.strip().split(":")
                    search_dict[key] = value
                except Exception:
                    pass
            for name in allLabelData:
                t_labelData = allLabelData[name]
                search_keys = list(search_dict.keys())

                accept = True
                if "标题" in search_keys:
                    search_keys.remove("标题")
                    if search_dict["标题"] not in name:
                        accept = False
                        continue

                for key in search_keys:
                    if search_dict[key] not in t_labelData[key]:
                        accept = False
                        break
                if accept:
                    accept_names.append(name)
            accept_names = list(set(accept_names))
            self.loadLabelList(accept_names)
        elif t_text == "":
            accept_names = list(sharedata.getAllLabelData().keys())
            self.loadLabelList(accept_names)
        else:
            for name in allLabelData:
                if t_text in name:
                    accept_names.append(name)
                    continue

                t_labelData = allLabelData[name]
                for key in t_labelData:
                    if t_text in t_labelData[key]:
                        accept_names.append(name)
                        break

            accept_names = list(set(accept_names))
            self.loadLabelList(accept_names)

        return accept_names


    @QtCore.pyqtSlot()
    def on_pushButton_showlabel_clicked(self):
        index = self.comboBox_selectlabel.currentIndex()
        c_text = self.comboBox_selectlabel.currentText()
        t_show = sharedata.getLabelShow()
        if index != -1:
            self.listWidget_labelshow.addOne(c_text)
            sharedata.setLabelShow(t_show + [c_text])
            self.on_btn_search_clicked()


    @QtCore.pyqtSlot()
    def on_pushButton_clearlabel_clicked(self):
        self.listWidget_labelshow._reset()
        sharedata.setLabelShow(["标题"]+sharedata.getLabels())
        self.on_btn_search_clicked()


    @QtCore.pyqtSlot()
    def on_pushButton_newcategory_clicked(self):
        c_text = self.lineEdit_newcategory.text()

        if c_text in sharedata.getCategory().keys():
            reply = QMessageBox().warning(self, "警告", "类别不能重复！", QMessageBox.Yes)
            return

        if c_text.strip() == "":
            reply = QMessageBox().warning(self, "警告", "类别不能为空！", QMessageBox.Yes)
            return

        if c_text.strip() in ["全部","其他"]:
            reply = QMessageBox().warning(self, "警告", "不能使用预置类别！", QMessageBox.Yes)
            return

        self.listWidget_category.addOne(c_text)

        n_category = sharedata.getCategory()
        n_category[c_text] = []
        sharedata.setCategory(n_category)
        self.listWidget_category.getNowOrder()
        self.lineEdit_newcategory.setText("")


    def createMenu(self, cursor_point):
        if self.table_document.currentRow() == -1:
            return
        self.contextMenu = QMenu(self.table_document)
        self.changeCategoryActionList = []

        t_category = sharedata.getCategory()

        other_action = self.contextMenu.addAction("放入\"{}\"类别中".format("其他"))
        other_action.triggered.connect(lambda :self.changeCategory(self.table_document.currentRow(),"##OTHERS##"))
        self.changeCategoryActionList.append(other_action)

        for name in list(t_category.keys()):
            self.changeCategoryActionList.append(self.createMenuAction(name))

        for aciton in self.changeCategoryActionList:
            self.contextMenu.addAction(aciton)

        self.contextMenu.exec_(QCursor.pos())

    def createMenuAction(self, name):
        t_action = self.contextMenu.addAction("放入\"{}\"类别中".format(name))
        t_action.triggered.connect(lambda: self.changeCategory(self.table_document.selectedItems(), name))
        return t_action

    def changeCategory(self, selecteditems, dist):
        rowList = []
        for item in selecteditems:
            if item.row() not in rowList:
                rowList.append(item.row())

        for row in rowList:
            name = self.name_list[row]
            CategoryDictionary = sharedata.getAllName2Category()
            orig_category = CategoryDictionary[name]
            t_category = sharedata.getCategory()
            if orig_category != "##OTHERS##":
                t_category[orig_category].remove(name)
            if dist != "##OTHERS##":
                t_category[dist].append(name)
        self.listWidget_category.rowClicked()
        self.listWidget_category.updateNum()

    def showCategory(self, type):
        if type == "全部":
            self.n_category = list(sharedata.getAllLabelData().keys())
        elif type == "其他":
            t_list = []
            CategoryDictionary = sharedata.getAllName2Category()
            for name in CategoryDictionary:
                if CategoryDictionary[name] == "##OTHERS##":
                    t_list.append(name)
            self.n_category = t_list
        else:
            self.n_category = sharedata.getCategory()[type]

        self.on_btn_search_clicked()



    def closeEvent(self, a0) -> None:
        sharedata.saveShareData()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myshow = DocumentManagerMainWindow()
    myshow.show()
    sys.exit(app.exec_())