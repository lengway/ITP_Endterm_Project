import os
import shutil
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QSlider, QWidget, QLabel,
    QMessageBox, QFileDialog, QStyleFactory
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from pygame import mixer


def show_warning(message):
    warning_box = QMessageBox()
    warning_box.setWindowTitle("Warning")
    warning_box.setIcon(QMessageBox.Warning)
    warning_box.setText(message)
    warning_box.setStandardButtons(QMessageBox.Ok)
    warning_box.exec_()


class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.initialize_player()

    # две функции которые являются мозгом плеера: setup_ui отвечает за создание интерфейса
    # initialize_player отвечает за воспроизведение музыки
    def setup_ui(self):
        self.setWindowTitle("Music Player")
        self.setGeometry(200, 200, 720, 480)
        self.setWindowIcon(QIcon("resources/icons/icon.svg"))
        self.setStyle(QStyleFactory.create("Fusion"))

        # Основное окно и лейаут
        main_widget = QWidget()
        self.main_layout = QVBoxLayout()
        main_widget.setStyleSheet("background-color: #505050;")

        self.create_track_label()
        self.create_controls()
        self.create_playlist()
        self.create_volume_slider()

        main_widget.setLayout(self.main_layout)
        self.setCentralWidget(main_widget)

    def initialize_player(self):
        mixer.init()
        self.playlist = []
        self.current_song = None
        self.is_playing = False

        music_directory = os.path.join(os.getcwd(), "music")

        if not os.path.exists(music_directory):
            os.makedirs(music_directory)

        for file in os.listdir(music_directory):
            if file.endswith(".mp3"):
                self.playlist.append(os.path.join(music_directory, file))
                self.playlist_box.addItem(os.path.basename(file))

    # дальше по сути идет все тот же интерфейс, просто разбитый на функции
    def create_track_label(self):
        self.track_name_widget = QLabel("Track Name")
        self.track_name_widget.setAlignment(Qt.AlignCenter)
        self.track_name_widget.setStyleSheet(
            """
            color: gray;
            background-color: #303030;
            font: bold 14px;
            border-radius: 6px;
            padding: 3px;
            """
        )
        self.main_layout.addWidget(self.track_name_widget)

    def create_controls(self):
        button_layout = QHBoxLayout()

        self.previous_button = self.create_button("resources/icons/previous.svg", self.previous_button_clicked)
        self.play_button = self.create_button("resources/icons/play.svg", self.play_or_pause_button_clicked)
        self.stop_button = self.create_button("resources/icons/stop.svg", self.stop_song_button_clicked)
        self.next_button = self.create_button("resources/icons/next.svg", self.next_button_clicked)
        self.add_button = self.create_button("resources/icons/plus.svg", self.add_button_clicked)

        button_layout.addWidget(self.previous_button)
        button_layout.addWidget(self.play_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.next_button)
        button_layout.addWidget(self.add_button)

        self.main_layout.addLayout(button_layout)

    def create_playlist(self):
        self.playlist_box = QListWidget()
        self.playlist_box.setStyleSheet("""
        background-color: #272727;
        color: white;
        font: bold 14px;
        border-radius: 6px;
        padding: 3px;
        """)
        self.main_layout.addWidget(self.playlist_box)

    def create_volume_slider(self):
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setStyleSheet(
            """
            QSlider::groove:horizontal {
                height: 8px;
                background-color: #303030;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #999999;
                border: 1px solid #161616;
                width: 10px;
                height: 10px;
                border-radius: 3px;
                margin: -4px 0;
            }
            QSlider::handle:hover {
                background: #505050;
            }
            QSlider::sub-page:horizontal {
                background: #ffffff;
                height: 8px;
                border-radius: 4px;
            }
            QSlider::add-page:horizontal {
                background: #909090;
                height: 8px;
                border-radius: 4px;
            }
            """
        )
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.main_layout.addWidget(self.volume_slider)

    def create_button(self, icon_path, callback):
        button = QPushButton()
        button.setIcon(QIcon(icon_path))
        button.setStyleSheet(
            """
            QPushButton {
                background-color: #303030;
                padding: 4px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #202020;
            }
            QPushButton:pressed {
                background-color: #151515;
            }
            """
        )
        button.clicked.connect(callback)
        return button

    # функции контроллера плеера
    def previous_button_clicked(self):
        if not self.playlist:
            show_warning("The playlist is empty.")
            return

        current_index = self.playlist.index(self.current_song) if self.current_song else 0
        previous_index = (current_index - 1) % len(self.playlist)
        self.play_song(previous_index)

    def play_or_pause_button_clicked(self):
        if not self.current_song:
            if self.playlist_box.currentRow() < 0:
                show_warning("Please select a song first.")
                return
            self.play_song(self.playlist_box.currentRow())
        else:
            if self.is_playing:
                mixer.music.pause()
                self.is_playing = False
                self.play_button.setIcon(QIcon("resources/icons/play.svg"))
                self.track_name_widget.setStyleSheet(
                    """
                    color: gray;
                    background-color: #303030;
                    font: bold 14px;
                    border-radius: 6px;
                    padding: 3px;
                    """
                )
            else:
                mixer.music.unpause()
                self.is_playing = True
                self.play_button.setIcon(QIcon("resources/icons/pause.svg"))
                self.track_name_widget.setStyleSheet(
                    """
                    color: white;
                    background-color: #303030;
                    font: bold 14px;
                    border-radius: 6px;
                    padding: 3px;
                    """
                )

    def stop_song_button_clicked(self):
        mixer.music.stop()
        self.reset_player_state()

    def next_button_clicked(self):
        if not self.playlist:
            show_warning("The playlist is empty.")
            return

        current_index = self.playlist.index(self.current_song) if self.current_song else -1
        next_index = (current_index + 1) % len(self.playlist)
        self.play_song(next_index)

    def add_button_clicked(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Songs", "", "Audio Files (*.mp3 *.wav)")

        target_directory = os.path.join(os.getcwd(), "music")

        os.makedirs(target_directory, exist_ok=True)

        if files:
            for file in files:
                self.playlist.append(file)
                self.playlist_box.addItem(os.path.basename(file))
                try:
                    destination = os.path.join(target_directory, os.path.basename(file))
                    shutil.copy(file, destination)
                except Exception as e:
                    show_warning(f"Failed to copy {file}: {e}")

    def set_volume(self, value):
        mixer.music.set_volume(value / 100)

    def play_song(self, index):
        self.current_song = self.playlist[index]
        mixer.music.load(self.current_song)
        mixer.music.play()

        self.is_playing = True
        self.play_button.setIcon(QIcon("resources/icons/pause.svg"))
        self.track_name_widget.setText(os.path.basename(self.current_song))
        self.track_name_widget.setStyleSheet("""
            color: white;
            background-color: #303030;
            font: bold 14px;
            border-radius: 6px;
            padding: 3px;
            """
        )

    def reset_player_state(self):
        self.current_song = None
        self.is_playing = False
        self.track_name_widget.setText("Track Name")
        self.play_button.setIcon(QIcon("resources/icons/play.svg"))


if __name__ == "__main__":
    app = QApplication([])
    window = MusicPlayer()
    window.show()
    app.exec()
