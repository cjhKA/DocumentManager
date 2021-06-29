import glob
import re
import os
import shutil
import sys

import xlwt
import xlrd
from bs4 import BeautifulSoup as bs
from PyQt5.QtWidgets import QMainWindow,QApplication,QTableWidgetItem, QAbstractItemView, QMessageBox, QFileDialog
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

from UI.MainWindow import Ui_MainWindow
from DetailWindow import DetailDialog

from ShareData import sharedata

#Todo:写侧边栏，用于对不同的文档进行分类
#Todo:写label选择栏，用于显示、隐藏、排序标签

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
        self.table_document.doubleClicked.connect(self.showDetail)
        self.loadLabelList()



    def loadLabelList(self, name_list = None):
        all_labelData = sharedata.getAllLabelData()
        labels = sharedata.getLabels()


        self.table_document.setColumnCount(len(["标题"]+labels))
        self.table_document.setHorizontalHeaderLabels(["标题"] + labels)
        self.cbbox_searchTerm.clear()
        self.cbbox_searchTerm.addItems(["标题"]+labels)


        if name_list == None:
            self.table_document.setRowCount(len(all_labelData))
            for i in range(len(all_labelData)):
                name = list(all_labelData.keys())[i]
                t_dict = all_labelData[name]
                name_item = QTableWidgetItem(name)
                self.table_document.setItem(i, 0, name_item)
                for key in t_dict:
                    t_item = QTableWidgetItem(t_dict[key])
                    self.table_document.setItem(i, labels.index(key)+1,t_item)
        else:
            self.table_document.setRowCount(len(name_list))
            for i in range(len(name_list)):
                name = name_list[i]
                t_dict = all_labelData[name]
                name_item = QTableWidgetItem(name)
                self.table_document.setItem(i, 0, name_item)
                for key in t_dict:
                    t_item = QTableWidgetItem(t_dict[key])
                    self.table_document.setItem(i, labels.index(key) + 1, t_item)


    @QtCore.pyqtSlot()
    def on_btn_newDocument_clicked(self):
        self.DetailWindow = DetailDialog()
        self.DetailWindow.labelChange.connect(self.on_btn_search_clicked)
        self.DetailWindow.show()


    @QtCore.pyqtSlot()
    def on_btn_editDocument_clicked(self):
        if self.table_document.currentRow() != -1:
            self.DetailWindow = DetailDialog()
            self.DetailWindow.setUp(self.table_document.item(self.table_document.currentRow(), 0).text())
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
        keylist = list(labeldata.keys())
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
                value = str(sheet.cell(i,j).value)
                t_dict[key] = value
            sharedata.setLabelData(str(sheet.cell(i,0).value), t_dict)
            sharedata.saveShareData()

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
            self.table_document.clear()
            self.loadLabelList(accept_names)
        elif t_text == "":
            self.table_document.clear()
            self.loadLabelList()
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
            self.table_document.clear()
            self.loadLabelList(accept_names)


    def showDetail(self):
        self.on_btn_editDocument_clicked()






    def closeEvent(self, a0) -> None:
        sharedata.saveShareData()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myshow = DocumentManagerMainWindow()
    myshow.show()
    sys.exit(app.exec_())