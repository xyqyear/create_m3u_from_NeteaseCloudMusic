# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sub_ui.ui',
# licensing of 'sub_ui.ui' applies.
#
# Created: Sat Feb  9 12:59:00 2019
#      by: pyside2-uic  running on PySide2 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PySide2 import QtCore, QtGui, QtWidgets

class Ui_sub_window(object):
    def setupUi(self, sub_window):
        sub_window.setObjectName("sub_window")
        sub_window.resize(597, 710)
        self.gridLayout = QtWidgets.QGridLayout(sub_window)
        self.gridLayout.setContentsMargins(0, -1, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.songs_table_widget = QtWidgets.QTableWidget(sub_window)
        self.songs_table_widget.setObjectName("songs_table_widget")
        self.songs_table_widget.setColumnCount(2)
        self.songs_table_widget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.songs_table_widget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.songs_table_widget.setHorizontalHeaderItem(1, item)
        self.songs_table_widget.horizontalHeader().setDefaultSectionSize(150)
        self.songs_table_widget.horizontalHeader().setStretchLastSection(True)
        self.songs_table_widget.verticalHeader().setDefaultSectionSize(20)
        self.songs_table_widget.verticalHeader().setMinimumSectionSize(20)
        self.gridLayout.addWidget(self.songs_table_widget, 1, 0, 1, 1)
        self.playlist_name_label = QtWidgets.QLabel(sub_window)
        self.playlist_name_label.setObjectName("playlist_name_label")
        self.gridLayout.addWidget(self.playlist_name_label, 0, 0, 1, 1)

        self.retranslateUi(sub_window)
        QtCore.QMetaObject.connectSlotsByName(sub_window)

    def retranslateUi(self, sub_window):
        sub_window.setWindowTitle(QtWidgets.QApplication.translate("sub_window", "歌单详情", None, -1))
        self.songs_table_widget.horizontalHeaderItem(0).setText(QtWidgets.QApplication.translate("sub_window", "歌曲名", None, -1))
        self.songs_table_widget.horizontalHeaderItem(1).setText(QtWidgets.QApplication.translate("sub_window", "歌曲路径", None, -1))
        self.playlist_name_label.setText(QtWidgets.QApplication.translate("sub_window", "TextLabel", None, -1))

