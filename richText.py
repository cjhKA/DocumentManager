# _*_ coding:utf-8 _*_
# @File  : richText.py
# @Time  : 2020-12-17 09:10
# @Author: zizle
import os
import sys
import shutil
import time

from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QTextEdit, QTextBrowser, QToolBar, QPushButton, QComboBox,
                             QFontComboBox, QAction, QColorDialog, QMenu, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt, QSize, QMargins, QFileInfo, QUrl
from PyQt5.QtGui import QFont, QBrush, QColor, QIcon, QPixmap, QPalette, QTextCharFormat, QTextCursor, QTextImageFormat, QImage, QImageReader
from functools import partial

from ShareData import sharedata

class MyTextEdit(QTextEdit):
    def __init__(self, parent):
        super(MyTextEdit, self).__init__(parent=parent)
        self.canUndo = False
        self.canRedo = False
        self.canCopy = False
        self.undoAvailable.connect(self.setUndo)
        self.redoAvailable.connect(self.setRedo)
        self.copyAvailable.connect(self.setCopy)
        self.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard|
                                     Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard|
                                     Qt.TextEditable)
        # self.linkActivated
        # self.anchorClicked.connect(self.openFile)
        # self.setOpenLinks(False)

    def mousePressEvent(self, e) -> None:
        self.anchor = self.anchorAt(e.pos())
        if self.anchor:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
        super(MyTextEdit, self).mousePressEvent(e)

    def mouseReleaseEvent(self, e) -> None:
        if self.anchor:
            self.openFile(QUrl(self.anchor))
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.anchor = None
        super(MyTextEdit, self).mouseReleaseEvent(e)


    def openFile(self, url):
        dest_path = os.path.join(os.getcwd(),url.url())
        if os.path.isfile(dest_path):
            os.startfile(dest_path)

    def setUndo(self, can):
        self.canUndo = can

    def setRedo(self, can):
        self.canRedo = can

    def setCopy(self, can):
        self.canCopy = can

    def canInsertFromMimeData(self, source) -> bool:
        return source.hasImage() or source.hasUrls() or QTextEdit.canInsertFromMimeData(source)

    def contextMenuEvent(self, e) -> None:
        # super(MyTextEdit, self).contextMenuEvent(e)
        menu = QMenu(self)
        Undo_action = menu.addAction("Undo")
        print(self.isUndoRedoEnabled())
        Undo_action.triggered.connect(self.undo)
        Undo_action.setEnabled(self.canUndo)

        Redo_action = menu.addAction("Redo")
        Redo_action.triggered.connect(self.redo)
        Redo_action.setEnabled(self.canRedo)
        menu.addSeparator()
        Cut_action = menu.addAction("Cut")
        Cut_action.triggered.connect(self.cut)
        Cut_action.setEnabled(self.canCopy)
        Copy_action = menu.addAction("Copy")
        Copy_action.triggered.connect(self.copy)
        Copy_action.setEnabled(self.canCopy)

        Paste_action = menu.addAction("Paste")
        Paste_action.triggered.connect(self.paste)
        menu.addSeparator()
        SelectAll_action = menu.addAction("Select All")
        SelectAll_action.triggered.connect(self.selectAll)
        menu.exec_(self.mapToGlobal(e.pos()))
        pass

    def insertFromMimeData(self, source) -> None:
        if source.hasImage():
            t_img = QImage(source.imageData())
            t_path = os.path.join(sharedata.getImageRoot(),str(time.time())+".jpg")
            t_img.save(t_path)
            self._InsertImage(t_path, False)
        elif source.hasUrls():
            flag = True
            for url in source.urls():
                info = QFileInfo(url.toLocalFile())
                if info.suffix().lower() in QImageReader.supportedImageFormats():
                    flag = False
                    self._InsertImage(info.filePath())
                else:
                    # QTextEdit.insertFromMimeData(self, source)
                    self._InsertDocument(info.filePath())
        else:
            QTextEdit.insertFromMimeData(self, source)



    def dragEnterEvent(self, a0) -> None:
        if a0.mimeData().hasText():
            if a0.mimeData().text().startswith('file:///'):
                a0.accept()
        else:
            a0.ignore()

    def dragMoveEvent(self, a0) -> None:
        a0.accept()

    def _InsertImage(self, path, copy = True):
        maxborder = sharedata.getMaxBorder()
        t_img = QTextImageFormat()
        # t_img.setName(path.strip()[8:])
        t_path = path

        if copy:
            d_path = os.path.join(sharedata.getImageRoot(), str(time.time()) + os.path.split(t_path)[1])
            shutil.copy(t_path, d_path)
            t_img.setName(d_path)
        else:
            t_img.setName(t_path)

        t = QImage(path)
        w = t.width()
        h = t.height()
        if w > h:
            if w > maxborder:
                t_img.setWidth(maxborder)
                t_img.setHeight(h * maxborder / w)
        else:
            if h > maxborder:
                t_img.setHeight(maxborder)
                t_img.setWidth(w * maxborder / h)
        self.textCursor().insertImage(t_img)


    def keyPressEvent(self, e) -> None:
        if e.key() == Qt.Key_Enter or e.key() == Qt.Key_Return:
            cursor = self.textCursor()
            fmt = cursor.charFormat()
            fmt.setAnchorHref(None)
            fmt.setFontUnderline(False)
            fmt.setForeground(QColor('black'))
            cursor.insertText("\n", fmt)
        else:
            super(MyTextEdit, self).keyPressEvent(e)


    def _InsertDocument(self, path):
        if os.path.isfile(path):
            t_path = sharedata.getDocumentRoot()+str(time.time())+'.'+path.split(".")[-1]
            shutil.copy(path, t_path)
            cursor = self.textCursor()
            fmt = cursor.charFormat()
            fmt.setForeground(QColor('blue'))
            fmt.setFontUnderline(True)
            address = t_path
            fmt.setAnchor(True)
            fmt.setAnchorHref(address)
            fmt.setToolTip(address)
            cursor.insertText(os.path.split(path)[1], fmt)

            fmt.setAnchorHref(None)
            fmt.setFontUnderline(False)
            fmt.setForeground(QColor('black'))
            cursor.insertText(" ", fmt)


            # self.textCursor().insertHtml("<a href='" + t_path + "'>" + os.path.split(path)[1] + "</a>")


    def dropEvent(self, a0) -> None:
        paths = a0.mimeData().text().split('\n')
        for path in paths:
            path = path.strip()
            if len(path) > 8:
                if os.path.split(path)[1].split('.')[-1].lower() in QImageReader.supportedImageFormats():
                    self._InsertImage(path.strip()[8:])
                else:
                    self._InsertDocument(path.strip()[8:])
                # self.insertFromMimeData()
        a0.accept()



    # def paste(self) -> None:
    #     print("fuck")



class RichTextWindow(QMainWindow):
    """ 富文本编辑控件 """
    # 字体大小字典
    FONT_SIZE = {
        '42.0': '初号', '36.0': '小初',
        '26.0': '一号', '24.0': '小一',
        '22.0': '二号', '18.0': '小二',
        '16.0': '三号', '15.0': '小三',
        '14.0': '四号', '12.0': '小四',
        '10.5': '五号', '9.0': '小五',
        '7.5': '六号', '6.5': '小六',
        '5.5': '七号', '5': '八号',
        '8': '8', '9': '9',
        '10': '10', '11': '11',
        '12': '12', '14': '14',
        '16': '16', '18': '18',
        '20': '20', '22': '22',
        '24': '24', '26': '26',
        '28': '28', '36': '36',
        '48': '48', '72': '72',
    }

    def __init__(self, *args, **kwargs):
        super(RichTextWindow, self).__init__(*args, **kwargs)
        self.current_font_size = 10.5   # 默认字体大小(小五)
        self.current_font_family = 'Arial'  # 默认字体
        self.recently_font_color = ['#000000', '#C00000', '#FFC000', '#FFFF00', '#92D050']   # 最近使用的字体颜色
        self.recently_font_bg_color = ['#FFFFFF', '#C00000', '#FFC000', '#FFFF00', '#92D050']         # 最近使用的字体背景色

        self.setWindowTitle('富文本编辑器')
        self.resize(800, 600)

        """ 工具栏 """
        self.tool_bar = QToolBar(self)
        self.tool_bar.setMovable(False)
        first_separator = self.tool_bar.addSeparator()
        # 加粗
        self.font_bold_action = self.tool_bar.addAction(QIcon(QIcon('media/rich_text/bold.png')), '')
        self.font_bold_action.triggered.connect(self.change_font_bold)
        # 斜体
        self.font_italic_action = self.tool_bar.addAction(QIcon('media/rich_text/italic.png'), '')
        self.font_italic_action.triggered.connect(self.change_font_italic)
        # 下划线
        self.font_underline_action = self.tool_bar.addAction(QIcon('media/rich_text/underline.png'), '')
        self.font_underline_action.triggered.connect(self.change_font_underline)
        # 左对齐
        self.left_action = self.tool_bar.addAction(QIcon('media/rich_text/left.png'), '')
        self.left_action.triggered.connect(lambda: self.change_row_alignment('left'))
        # 中间对齐
        self.center_action = self.tool_bar.addAction(QIcon('media/rich_text/center.png'), '')
        self.center_action.triggered.connect(lambda: self.change_row_alignment('center'))
        # 右对齐
        self.right_action = self.tool_bar.addAction(QIcon('media/rich_text/right.png'), '')
        self.right_action.triggered.connect(lambda: self.change_row_alignment('right'))



        # # 两边对齐
        # self.left_right_action = self.tool_bar.addAction(QIcon('icons/left_right.png'), '')
        # self.left_right_action.triggered.connect(lambda: self.change_row_alignment('left_right'))

        # 字体选择
        self.font_selector = QFontComboBox(self)
        self.font_selector.setMaximumWidth(60)
        self.tool_bar.insertWidget(first_separator, self.font_selector)
        # 字体大小选择
        self.font_size_selector = QComboBox(self)
        [self.font_size_selector.addItem(self.FONT_SIZE[key], key) for key in self.FONT_SIZE.keys()]  # 添加选项
        self.font_size_selector.setCurrentText('五号')  # 默认五号
        self.font_size_selector.currentIndexChanged.connect(self.change_font_size)  # 字体选择信号
        self.tool_bar.insertWidget(first_separator, self.font_size_selector)
        # 字体颜色控制
        self.font_color_selector = QPushButton('A', self)
        self.font_color_selector.setToolTip('字体颜色')
        self.font_color_selector.setFixedSize(30, 21)
        self.update_recently_colors(color_type='font_color')

        self.tool_bar.insertWidget(first_separator, self.font_color_selector)
        # 字体背景色控制
        self.font_bg_color_selector = QPushButton('A', self)
        self.font_bg_color_selector.setToolTip('字体背景色')
        self.font_bg_color_selector.setFixedSize(30, 21)
        self.update_recently_colors(color_type='font_bg_color')
        self.tool_bar.insertWidget(first_separator, self.font_bg_color_selector)

        self.addToolBar(Qt.TopToolBarArea, self.tool_bar)

        # 编辑框
        self.text_edit = MyTextEdit(self)
        self.setCentralWidget(self.text_edit)

        self.tool_bar.setObjectName('toolBar')
        self.setStyleSheet(
            "#toolBar{spacing:2px}"
        )
        # 设置初始字体和大小
        init_font = QFont()
        font = QFont()
        font.setFamily('Arial')
        font.setPointSize(self.current_font_size)
        font.setFamily(self.current_font_family)
        self.text_edit.setFont(init_font)
        # 字体选择改变的信号
        self.font_selector.activated.connect(self.change_font)

    def update_recently_colors(self, color_type):
        """ 更新最近使用颜色 """
        if color_type == 'font_color':
            # 更新最近使用字体色
            colors = self.recently_font_color
            color_button = self.font_color_selector
            button_style = 'border:1px solid rgb(220,220,220);'
            if colors:
                button_style = 'border:1px solid rgb(220,220,220);color:{}'.format(colors[0])
        elif color_type == 'font_bg_color':
            # 更新最近使用字体背景色
            colors = self.recently_font_bg_color
            color_button = self.font_bg_color_selector
            button_style = 'border:1px solid rgb(220,220,220);'
            if colors:
                button_style = 'border:1px solid rgb(220,220,220);background-color:{}'.format(colors[0])
        else:
            return
        old_menu = color_button.menu()
        if old_menu:
            old_menu.deleteLater()  # 删除原按钮
        menu = QMenu()
        for color_item in colors:
            pix = QPixmap('media/rich_text/color_icon.png')
            # bitmap = pix.createMaskFromColor(QColor(210,120,100))
            pix.fill(QColor(color_item))
            # pix.setMask(bitmap)
            ico = QIcon(pix)
            action = menu.addAction(ico, color_item)
            action.triggered.connect(lambda: self.change_current_color(color_type))
        # 添加更多选项
        more_action = menu.addAction(QIcon('media/rich_text/more.png'), '更多颜色')
        more_action.triggered.connect(lambda: self.select_more_color(color_type))
        color_button.setStyleSheet(button_style)
        color_button.setMenu(menu)

    def select_more_color(self, color_type):
        """ 选择更多的颜色 """
        color = QColorDialog.getColor(parent=self, title='选择颜色')  # 不选默认为黑色
        color_str = color.name()
        # 改变对应颜色情况
        self.set_current_color(color_str.upper(), color_type)

    def change_current_color(self, color_type):
        """ 改变当前字体或字体背景的颜色 """
        action = self.sender()
        color = action.text()
        self.set_current_color(color, color_type)

    def set_current_color(self, color, color_type):

        if color_type == 'font_color':
            colors = self.recently_font_color
        elif color_type == 'font_bg_color':
            colors = self.recently_font_bg_color
        else:
            return
        if color in colors:
            color_index = colors.index(color)
            colors.insert(0, colors.pop(color_index))  # 将颜色插入到起始
        else:
            # 将颜色第一个替换掉
            colors[0] = color
        # 更新当前颜色
        self.update_recently_colors(color_type)

        if color_type == 'font_color':
            # 改变字体颜色
            self.change_font_color(colors[0])
        if color_type == 'font_bg_color':
            # 改变字体背景颜色
            self.change_font_bg_color(colors[0])

    def update_font(self):
        """ 改变字体 """
        current_font = QFont()
        current_font.setFamily(self.current_font_family)
        current_font.setPointSize(self.current_font_size)
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setFont(current_font)
        tc.mergeCharFormat(font_format)

    def change_font(self, index):
        """ 字体选择改变 """
        self.current_font_family = self.font_selector.currentFont().family()
        self.update_font()

    def change_font_size(self):
        """ 字体大小选择信号 """
        self.current_font_size = float(self.font_size_selector.currentData())
        self.update_font()

    def change_font_color(self, color):
        """ 改变字体颜色 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setForeground(QBrush(QColor(color)))
        tc.mergeCharFormat(font_format)

    def change_font_bg_color(self, color):
        """ 改变字体背景颜色 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setBackground(QBrush(QColor(color)))
        tc.mergeCharFormat(font_format)

    def change_font_italic(self):
        """ toggle斜体 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setFontItalic(not font_format.fontItalic())
        tc.mergeCharFormat(font_format)

    def change_font_bold(self):
        """ toggle粗体 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        current_font = font_format.font()
        current_font.setBold(not current_font.bold())
        current_font.setFamily(self.current_font_family)
        current_font.setPointSize(self.current_font_size)
        font_format.setFont(current_font)
        tc.mergeCharFormat(font_format)

    def change_font_underline(self):
        """ toggle下划线 """
        tc = self.text_edit.textCursor()
        font_format = self.text_edit.currentCharFormat()
        font_format.setFontUnderline(not font_format.fontUnderline())
        tc.mergeCharFormat(font_format)

    def change_row_alignment(self, alignment: str):
        """ toggle对齐方式 """
        if alignment == 'left':
            self.text_edit.setAlignment(Qt.AlignLeft)
        elif alignment == 'right':
            self.text_edit.setAlignment(Qt.AlignRight)
        elif alignment == 'center':
            self.text_edit.setAlignment(Qt.AlignHCenter)
        # elif alignment == 'left_right':
        #     self.text_edit.setAlignment(Qt.AlignAbsolute)
        else:
            return

    def toHtml(self):
        return self.text_edit.toHtml()

    def toPlainText(self):
        return self.text_edit.toPlainText()

    def loadHtml(self, html):
        self.text_edit.setHtml(html)

    def loadPlainText(self, txt):
        self.text_edit.setPlainText(txt)




if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily('Arial')
    app.setFont(font)
    r = RichTextWindow()
    r.show()
    sys.exit(app.exec_())
