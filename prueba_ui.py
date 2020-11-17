import cv2
import logging
import sys

import RPi.GPIO as GPIO

from dash import Ui_MainWindow
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication, QMainWindow

GPIO.setmode(GPIO.BOARD)
#Válvula A
GPIO.setup(11, GPIO.OUT)
#Válvula B
GPIO.setup(13, GPIO.OUT)
#Válvula C
GPIO.setup(15, GPIO.OUT)
#Válvula D
GPIO.setup(19, GPIO.OUT)
#Válvula E
GPIO.setup(21, GPIO.OUT)

motor = GPIO.PWM(32,100)

logging.getLogger().setLevel(logging.WARNING)

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            try:
                ret, frame = cap.read()
                if (ret):
                    # https://stackoverflow.com/a/55468544/6622587
                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.changePixmap.emit(p)
            except Exception as e:
                logging.warning(e)
            

class dash(QMainWindow):
    def __init__(self):
        super(dash, self).__init__()
        motor.start(0)
        try:

            self.ui = Ui_MainWindow()

            self.ui.setupUi(self)
            self.label = QLabel(self)
            self.label.move(450, 120)
            self.label.resize(350, 240)
            th = Thread(self)
            th.changePixmap.connect(self.setImage)
            th.start()
            self.flect1 = QLabel(self)
            self.flect1.move(50, 130)
            self.flect2 = QLabel(self)
            self.flect2.move(130, 130)
            self.flect3 = QLabel(self)
            self.flect3.move(210, 130)
            self.ui.verticalSlider.valueChanged.connect(self.get_slider1_value)
            self.ui.verticalSlider_2.valueChanged.connect(self.get_slider2_value)
            self.ui.verticalSlider_3.valueChanged.connect(self.get_slider3_value)
            self.ui.verticalSlider.valueChanged.connect(self.set_motor_freq)
            self.ui.verticalSlider_2.valueChanged.connect(self.get_slider2_value)
            self.ui.verticalSlider_3.valueChanged.connect(self.get_slider3_value)
            
            self.show()
        except Exception as e:
            logging.warning(e)
            
    def set_motor_freq(self, slider_value):
        motor.ChangeDutyCycle(slider_value)
        

    def get_slider1_value(self, value_of_slider):
        self.flect1.setText(str(value_of_slider))
    
    def get_slider2_value(self, value_of_slider):
        self.flect2.setText(str(value_of_slider))

    def get_slider3_value(self, value_of_slider):
        self.flect3.setText(str(value_of_slider))

    @pyqtSlot(QImage)
    def setImage(self, image):
        try:
            self.label.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            logging.warning(e)
        

app = QApplication([])

application = dash()

##application.show()

sys.exit(app.exec())