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
A = 11
B = 13
C = 15
D = 19
E = 21

GPIO.setup(A, GPIO.OUT)
#Válvula B
GPIO.setup(B, GPIO.OUT)
#Válvula C
GPIO.setup(C, GPIO.OUT)
#Válvula D
GPIO.setup(D, GPIO.OUT)
#Válvula E
GPIO.setup(E, GPIO.OUT)

GPIO.setup(36, GPIO.OUT)

motor = GPIO.PWM(36,100)

logging.getLogger().setLevel(logging.WARNING)

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        while True:
            try:
                ret, frame = cap.read()
                if (ret):
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
        GPIO.output(A, True)
        GPIO.output(B, True)
        GPIO.output(C, True)
        GPIO.output(D, True)
        GPIO.output(E, True)
        motor.start(100)
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
            
            self.show()
        except Exception as e:
            logging.warning(e)
        

    def get_slider1_value(self, slider_value1):
        self.flect1.setText(str(slider_value1))
        GPIO.output(A, False)
        GPIO.output(B, True)
        GPIO.output(C, False)
        GPIO.output(D, True)
        GPIO.output(E, True)
        logging.warning(str(float(slider_value1)))
        motor.ChangeDutyCycle(float(100-slider_value1))
    
    def get_slider2_value(self, slider_value2):
        self.flect2.setText(str(slider_value2))
        GPIO.output(A, True)
        GPIO.output(B, False)
        GPIO.output(C, True)
        GPIO.output(D, True)
        GPIO.output(E, False)
        logging.warning(str(float(slider_value2)))
        motor.ChangeDutyCycle(float(100-slider_value2))

    def get_slider3_value(self, slider_value3):
        self.flect3.setText(str(slider_value3))
        GPIO.output(A, True)
        GPIO.output(B, False)
        GPIO.output(C, True)
        GPIO.output(D, False)
        GPIO.output(E, True)
        logging.warning(str(float(slider_value3)))      
        motor.ChangeDutyCycle(float(100-slider_value3))

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
GPIO.output(A, True)
GPIO.output(B, True)
GPIO.output(C, True)
GPIO.output(D, True)
GPIO.output(E, True)
GPIO.cleanup()