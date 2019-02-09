# -*- coding:utf-8 -*-
import os
import sys
import json

from main_ui import Ui_main_window
from sub_ui import Ui_sub_window
from Exporter import get_dir_of_db, get_playlist, tid2dir_offline, playlist_dict_to_m3u, save_m3u
from PySide2.QtWidgets import QWidget, QApplication, QFileDialog, QTableWidgetItem, QHeaderView, QMessageBox
from PySide2.QtCore import Qt


class MainWindow(QWidget, Ui_main_window):
    def __init__(self):
        super(MainWindow, self).__init__()
        # variables setting
        self.playlists = dict()
        self.all_song_info = dict()
        self.column2playlist = []
        self.config = dict(folder='',
                           pids=[])

        # window setting
        self.sub_window = None
        self.setup()
        self.show_playlists()

    def setup(self):
        self.setupUi(self)

        # set button slot
        self.select_folder_button.clicked.connect(self.select_folder)
        self.all_select_button.clicked.connect(self.select_all)
        self.reverse_button.clicked.connect(self.reverse_choice)
        self.cancel_button.clicked.connect(self.cancel_choice)
        self.export_button.clicked.connect(self.export_playlist)

        # set table
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableWidget.doubleClicked.connect(self.view_songs)

        # load config file
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                self.config = json.loads(f.read())
        if self.config['folder']:
            self.folder_path.setText(self.config['folder'])

    def select_folder(self):
        folder = QFileDialog().getExistingDirectory().replace('/', '\\')

        self.config['folder'] = folder
        self.folder_path.setText(folder)

    def clear_table(self):
        for i in range(self.tableWidget.rowCount()):
            self.tableWidget.removeRow(0)

    def show_playlists(self):
        dirs = get_dir_of_db()
        webdb_dat = dirs['webdb.dat']
        self.playlists = get_playlist(webdb_dat)

        self.clear_table()
        i = 0
        for pid, playlist in self.playlists.items():
            if len(playlist['songs']) == 0:
                continue
            self.tableWidget.insertRow(i)
            item1 = QTableWidgetItem(playlist['playlist_name'])
            item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item1.setCheckState(Qt.Unchecked)
            self.tableWidget.setItem(i, 0, item1)

            item2 = QTableWidgetItem(str(len(playlist['songs'])))
            item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tableWidget.setItem(i, 1, item2)

            item3 = QTableWidgetItem(playlist['username'])
            item3.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.tableWidget.setItem(i, 2, item3)

            self.column2playlist.append(pid)
            i += 1

        # bellows are songs info
        library_dat = dirs['library.dat']
        self.all_song_info = tid2dir_offline(library_dat, webdb_dat)

        # bellows are selecting the playlists which are selected last time
        if self.config['pids']:
            for element in self.get_all_playlist_element():
                pid = self.column2playlist[element.row()]
                if pid in self.config['pids']:
                    element.setCheckState(Qt.Checked)

    def view_songs(self):
        column = self.tableWidget.currentRow()
        playlist = self.playlists[self.column2playlist[column]]
        self.sub_window = SubWindow()
        self.sub_window.playlist_name_label.setText(playlist['playlist_name'] + ' :')
        for tid in playlist['songs']:
            if tid in self.all_song_info:
                self.sub_window.songs_info[tid] = self.all_song_info[tid]

        self.sub_window.show_songs()

    def get_all_playlist_element(self):
        for i in range(self.tableWidget.rowCount()):
            yield self.tableWidget.item(i, 0)

    def cancel_choice(self):
        for element in self.get_all_playlist_element():
            element.setCheckState(Qt.Unchecked)

    def reverse_choice(self):
        for element in self.get_all_playlist_element():
            element.setCheckState(Qt.Unchecked if element.checkState() == Qt.Checked else Qt.Checked)

    def select_all(self):
        for element in self.get_all_playlist_element():
            element.setCheckState(Qt.Checked)

    def config_selected_pids(self):
        self.config['pids'] = []
        for element in self.get_all_playlist_element():
            pid = self.column2playlist[element.row()]
            if element.checkState() == Qt.Checked:
                self.config['pids'].append(pid)

    def export_playlist(self):
        if not self.folder_path.text():
            QMessageBox.warning(self, '警告', '你还没有指定目录!')
        else:
            self.config_selected_pids()
            m3u_content = playlist_dict_to_m3u(self.playlists, self.all_song_info, self.config['pids'])
            save_path = self.folder_path.text()
            save_m3u(m3u_content, save_path)

            QMessageBox.information(self, '成功', '导出歌单成功!')

    def closeEvent(self, event):
        if self.sub_window:
            self.sub_window.close()

        self.config_selected_pids()
        with open('config.json', 'w', encoding='utf-8') as f:
            f.write(json.dumps(self.config))

        event.accept()


class SubWindow(QWidget, Ui_sub_window):
    def __init__(self):
        super(SubWindow, self).__init__()
        self.songs_info = dict()
        self.setup()

    def setup(self):
        self.setupUi(self)
        self.songs_table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.songs_table_widget.setColumnWidth(1, 350)

    def show_songs(self):
        i = 0
        for tid, info in self.songs_info.items():
            self.songs_table_widget.insertRow(i)
            item1 = QTableWidgetItem(info['name'])
            item1.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.songs_table_widget.setItem(i, 0, item1)

            item2 = QTableWidgetItem(info['file_path'])
            item2.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
            self.songs_table_widget.setItem(i, 1, item2)

        self.show()


if __name__ == '__main__':
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec_())
