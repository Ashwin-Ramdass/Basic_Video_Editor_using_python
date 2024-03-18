# Importing required Variables
import sys
import cv2
import logging
import os
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QHBoxLayout, QFileDialog, QCheckBox, QScrollArea, QGridLayout, QMessageBox, QFrame, QSlider
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, Qt

# Creating a class for the video player and initializing required varibles
class VideoPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.threshold_slider = QSlider(Qt.Horizontal)
        self.setup_ui()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.cap = None
        self.is_webcam_running = False
        self.is_grayscale = False
        self.is_edge_detection = False
        self.total_frames = 0
        self.is_video_uploaded = False
        self.is_playing = True
        self.is_blurring = False
        self.edge_detection_threshold = 1
        self.blurring_intensity = 1

    # Defining UI Structure, Here I have mentioned left and right panels to do required operations
    def setup_ui(self):
        layout = QHBoxLayout()
        # In the Left layout, I added Start_webcam, Upload_Video, Start/Stop, Grayscale and other video processing parameters 
        left_layout = QVBoxLayout()

        self.start_webcam_button = QPushButton("Start Webcam")
        self.start_webcam_button.clicked.connect(self.start_stop_webcam)
        self.upload_video_button = QPushButton("Upload Video")
        self.upload_video_button.clicked.connect(self.upload_video)
        left_layout.addWidget(self.start_webcam_button)
        left_layout.addWidget(self.upload_video_button)
        self.video_frame = QLabel()
        left_layout.addWidget(self.video_frame)

        self.start_stop_button = QPushButton("Start / Stop")
        self.start_stop_button.clicked.connect(self.toggle_start_stop)
        left_layout.addWidget(self.start_stop_button)

        self.grayscale_checkbox = QCheckBox("Grayscale")
        self.grayscale_checkbox.stateChanged.connect(self.toggle_grayscale)
        left_layout.addWidget(self.grayscale_checkbox)

        self.edge_detection_checkbox = QCheckBox("Edge Detection")
        self.edge_detection_checkbox.stateChanged.connect(self.toggle_edge_detection)
        left_layout.addWidget(self.edge_detection_checkbox)

        self.edge_detection_slider = QSlider(Qt.Horizontal)
        self.edge_detection_slider.setRange(-10000,400)
        self.edge_detection_slider.setValue(-10000)
        self.edge_detection_slider.setTickInterval(10)
        self.edge_detection_slider.setTickPosition(QSlider.TicksBelow)
        self.edge_detection_slider.valueChanged.connect(self.edge_detection_threshold)
        left_layout.addWidget(self.edge_detection_slider)

        self.blurring_checkbox = QCheckBox("Blurring")
        self.blurring_checkbox.stateChanged.connect(self.toggle_blurring)
        left_layout.addWidget(self.blurring_checkbox)

        self.blurring_slider = QSlider(Qt.Horizontal)
        self.blurring_slider.setRange(-1000, 1000)
        self.blurring_slider.setValue(0)
        self.blurring_slider.setTickInterval(10)
        self.blurring_slider.setTickPosition(QSlider.TicksBelow)
        self.blurring_slider.valueChanged.connect(self.blurring_intensity)
        left_layout.addWidget(self.blurring_slider)

        layout.addLayout(left_layout)

        # In the Right layout I added fully for visualizing frames and save / clear the visualization.
        right_layout = QVBoxLayout()
        self.frame_gallery = QWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.frame_gallery)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        frame_gallery_layout = QGridLayout()
        self.frame_gallery.setLayout(frame_gallery_layout)

        right_layout.addWidget(self.scroll_area)

        self.total_frames_label = QLabel("Total Frames: 0")
        right_layout.addWidget(self.total_frames_label)

        self.save_frames_button = QPushButton("Save Frames")
        self.save_frames_button.clicked.connect(self.save_frames)
        right_layout.addWidget(self.save_frames_button)

        self.clear_frames_button = QPushButton("Clear Frames")
        self.clear_frames_button.clicked.connect(self.clear_frames)
        right_layout.addWidget(self.clear_frames_button)

        layout.addLayout(right_layout)

        self.setLayout(layout)

    # I have defined the functions which helps me to start or stop webcam
    def start_stop_webcam(self):
        if not self.is_webcam_running:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)
            self.is_webcam_running = True
            self.start_webcam_button.setText("Stop Webcam")
        else:
            self.cap.release()
            self.timer.stop()
            self.is_webcam_running = False
            self.start_webcam_button.setText("Start Webcam")
            self.video_frame.clear()
    
    # This functions helps us to upload video from a custom location
    def upload_video(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv)")
        if filename:
            self.cap = cv2.VideoCapture(filename)
            self.timer.start(30)
            self.is_video_uploaded = True

    # Here I created this function to toggle start/stop,
    # for pausing when the video is uploaded and start or stop webcam if webcam is on
    def toggle_start_stop(self):
        if self.is_webcam_running:
            if self.is_playing:
                self.cap.release()
                self.is_playing = False
            else:
                self.cap = cv2.VideoCapture(0)
                self.timer.start(30)
                self.is_playing = True
        elif self.is_video_uploaded:
            if self.is_playing:
                self.timer.stop()
                self.is_playing = False
            else:
                self.timer.start(30)
                self.is_playing = True

    # I defined the function which turns on grayscale when the checkbox is checked
    def toggle_grayscale(self, state):
        self.is_grayscale = state == Qt.Checked

    # I defined the function which turns on edge detection when the checkbox is checked
    def toggle_edge_detection(self, state):
        self.is_edge_detection = state == Qt.Checked

    # Here the threshold for edge_detection is updated as per the value (I have given -10000 to 400)
    def edge_detection_threshold(self, value):
        self.edge_detection_threshold = value

    # I defined the function which turns on blur when the checkbox is checked
    def toggle_blurring(self, state):
        self.is_blurring = state == Qt.Checked

    # Here the threshold for edge_detection is updated as per the value (I have given -1000 to 1000)
    def blurring_intensity(self, value):
        self.blurring_intensity = value

    # Here the frame gets updates as per the number of frames and 4 x n,
    # The Data Visiblity for webcam runnng, grayscale BGR2Gray, Thershold variations.
    # Count of total frames.
    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            if self.is_webcam_running:
                self.total_frames += 1
            if self.is_grayscale:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if self.is_edge_detection:
                threshold1 = min(0, self.edge_detection_threshold - 200)
                threshold2 = max(200, self.edge_detection_threshold + 200)
                frame = cv2.Canny(frame, threshold1, threshold2)
            if self.is_blurring:
                frame = cv2.GaussianBlur(frame, (15, 15), self.blurring_intensity)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_rgb.shape
            bytes_per_line = ch * w
            q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img.scaled(self.video_frame.size(), aspectRatioMode=Qt.KeepAspectRatio, transformMode=Qt.SmoothTransformation))
            self.video_frame.setPixmap(pixmap)

            frame_label = QLabel()
            frame_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))

            layout = self.frame_gallery.layout()
            num_widgets = layout.count()

            row = num_widgets // 4
            col = num_widgets % 4

            layout.addWidget(frame_label, row, col)

            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)) if not self.is_webcam_running else self.total_frames
            self.total_frames_label.setText(f"Total Frames: {current_frame}")

        else:
            self.timer.stop()

    #This function is to save frames for a custom location
    def save_frames(self):
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Save Frames")
            if folder_path:
                layout = self.frame_gallery.layout()
                if layout.count() == 0:
                    QMessageBox.warning(self, "Warning", "No frames to save.")
                    return
                
                existing_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                if existing_files:
                    existing_frame_count = sum(1 for file in existing_files if file.startswith("frame_"))
                    start_index = existing_frame_count + 1
                else:
                    start_index = 1

                for i in range(layout.count()):
                    item = layout.itemAt(i)
                    if item.widget():
                        pixmap = item.widget().pixmap()
                        frame_path = os.path.join(folder_path, f"frame_{start_index + i}.png")
                        pixmap.toImage().save(frame_path)
                QMessageBox.information(self, "Information", "Frames saved successfully!")
            else:
                QMessageBox.warning(self, "Warning", "No folder selected!")
        except Exception as e:
            logging.error(f"Error occurred in save_frames: {e}")

    # This function is to clear the frames from the frame display
    def clear_frames(self):
        layout = self.frame_gallery.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        self.total_frames = 0
        self.total_frames_label.setText("Total Frames: 0")
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

# Main class
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoPlayer()
    window.setWindowTitle("Video Player")
    window.setGeometry(0, 0, 1900, 1000)
    window.show()
    sys.exit(app.exec_())