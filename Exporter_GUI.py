# -*- coding:utf-8 -*-
import sys

from UI import Ui_main_window
from Exporter import get_dir_of_db, get_playlist
from PySide2.QtWidgets import QWidget, QApplication, QFileDialog, QTableWidgetItem
from PySide2.QtCore import Qt


class Window(QWidget, Ui_main_window):
    def __init__(self):
        super(Window, self).__init__()
        self.setup()
        self.items = []
        self.playlists = dict()
        self.column2playlist = []

    def setup(self):
        self.setupUi(self)
        self.select_folder.clicked.connect(self.view_folder)
        self.list_button.clicked.connect(self.show_playlists)
        self.tableWidget.setColumnWidth(0, 400)
        self.tableWidget.doubleClicked.connect(self.view_songs)

    def view_folder(self):
        file_path = QFileDialog().getExistingDirectory().replace('/', '\\')
        self.folder_path.setText(file_path)

    def show_playlists(self):
        dirs = get_dir_of_db()
        webdb_dat = dirs['webdb.dat']
        self.playlists = get_playlist(webdb_dat)
        i = 0
        for pid, playlist in self.playlists.items():
            self.tableWidget.insertRow(i)
            item1 = QTableWidgetItem(playlist['playlist_name'])
            item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item1.setCheckState(Qt.Unchecked)
            self.tableWidget.setItem(i, 0, item1)

            item2 = QTableWidgetItem(str(len(playlist['songs'])))
            item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tableWidget.setItem(i, 1, item2)

            self.column2playlist.append(pid)

            i += 1

    def view_songs(self):
        column = self.tableWidget.currentRow()
        print(self.playlists[self.column2playlist[column]])

    def cancel_choice(self):
        pass

    def reverse_choice(self):
        pass

    def select_all(self):
        pass


if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = Window()
        window.show()
        sys.exit(app.exec_())
