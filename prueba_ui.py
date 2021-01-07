import cv2
import logging
import sys
import time

import RPi.GPIO as GPIO

from dash import Ui_MainWindow
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QTimer, QObject, QCoreApplication
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
GPIO.setup(37, GPIO.OUT)
motor = GPIO.PWM(36,100)
motor2 = GPIO.PWM(37,100)


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
                
class Movement(QObject):
    def __init__(self):
        super(Movement, self).__init__()
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        
    def move(self):
        QCoreApplication.processEvents()
        time.sleep(1)
        QCoreApplication.processEvents()
        print("move")
        self.paso_1()
        QCoreApplication.processEvents()
        print("sleep1")
        time.sleep(1)
        QCoreApplication.processEvents()
        print("paso2")
        self.paso_2()
        QCoreApplication.processEvents()
        print("sleep2")
        time.sleep(2.5)
        QCoreApplication.processEvents()
        print("paso3")
        self.paso_3()
        QCoreApplication.processEvents()
        print("sleep3")
        time.sleep(2)
        QCoreApplication.processEvents()
        print("paso4")
        self.paso_4()
        QCoreApplication.processEvents()
        print("sleep4")
        time.sleep(1)
        QCoreApplication.processEvents()
        print("stop")
        self.stop()
        QCoreApplication.processEvents()
        print("sleep5")
        time.sleep(1)
        
    def stop(self):
        GPIO.output(A, False)
        GPIO.output(B, False)
        GPIO.output(C, False)
        GPIO.output(D, False)
        GPIO.output(E, False)
        motor.ChangeDutyCycle(0)
        motor2.ChangeDutyCycle(0)
        print("Stop")
        
    def paso_1(self):
        self.activar_salida_1()
        motor.ChangeDutyCycle(30)
        
    def paso_2(self):
        self.activar_elongacion()
        
    def paso_3(self):
        self.activar_salida_3()
        motor.ChangeDutyCycle(20)
        
    def paso_4(self):
        self.desactivar_elongacion()
        
    def activar_elongacion(self):
        motor2.ChangeDutyCycle(35)
        GPIO.output(E, True)
    
    def desactivar_elongacion(self):
        motor2.ChangeDutyCycle(0)
        GPIO.output(E, False)
        
    def activar_salida_1(self):
        GPIO.output(A, True)
        GPIO.output(B, False)
        GPIO.output(C, True)
        GPIO.output(D, False)
        GPIO.output(E, False)
        print("A, C")
        
    def activar_salida_2(self):
        GPIO.output(A, False)
        GPIO.output(B, True)
        GPIO.output(C, False)
        GPIO.output(D, False)
        GPIO.output(E, True)
        print("A, C, D")
        
    def activar_salida_3(self):
        GPIO.output(A, False)
        GPIO.output(B, True)
        GPIO.output(C, False)
        GPIO.output(D, False)
        GPIO.output(E, True)
        print("A, C, E")
            

class dash(QMainWindow):
    def __init__(self):
        super(dash, self).__init__()
        GPIO.output(A, True)
        GPIO.output(B, True)
        GPIO.output(C, True)
        GPIO.output(D, True)
        GPIO.output(E, True)
        motor.start(0)
        motor2.start(0)
        try:

            self.ui = Ui_MainWindow()

            self.ui.setupUi(self)
            self.label = QLabel(self)
            self.label.move(450, 120)
            self.label.resize(350, 240)
            self.th = Thread(self)
            self.th.start()
            self.th1 = QThread(self)
            self.th2 = Movement()
            self.th2.moveToThread(self.th1)
            self.th1.start()
            self.th.changePixmap.connect(self.setImage)
            self.flect1 = QLabel(self)
            self.flect1.move(50, 130)
            self.flect2 = QLabel(self)
            self.flect2.move(130, 130)
            self.flect3 = QLabel(self)
            self.flect3.move(210, 130)
            self.ui.verticalSlider.valueChanged.connect(self.get_slider1_value)
            self.ui.verticalSlider_2.valueChanged.connect(self.get_slider2_value)
            self.ui.verticalSlider_3.valueChanged.connect(self.get_slider3_value)
            self.ui.checkBox.stateChanged.connect(self.state_changed)
            
            self.show()
        except Exception as e:
            logging.warning(e)
            
    def state_changed(self,int):
        while (True):
            if (self.ui.checkBox.isChecked()):
                self.th2.move()
            else:
                self.th2.stop()
                break
        
    def stop(self):
        self.th2.stop()
        GPIO.output(A, False)
        GPIO.output(B, False)
        GPIO.output(C, False)
        GPIO.output(D, False)
        GPIO.output(E, False)
        
    def paso_1(self):
        self.activar_salida_1()
        
    def paso_2(self):
        self.activar_elongacion()
        
    def paso_3(self):
        self.activar_salida_3()
        
    def paso_4(self):
        self.desactivar_elongacion()
        
    def activar_elongacion(self):
        motor2.ChangeDutyCycle(50)
    
    def desactivar_elongacion(self):
        motor2.ChangeDutyCycle(0)
        
    def activar_salida_1(self):
        GPIO.output(A, True)
        GPIO.output(B, False)
        GPIO.output(C, True)
        GPIO.output(D, False)
        GPIO.output(E, False)
        
    def activar_salida_2(self):
        GPIO.output(A, False)
        GPIO.output(B, True)
        GPIO.output(C, False)
        GPIO.output(D, False)
        GPIO.output(E, True)
        
    def activar_salida_3(self):
        GPIO.output(A, False)
        GPIO.output(B, True)
        GPIO.output(C, False)
        GPIO.output(D, True)
        GPIO.output(E, False)
        

    def get_slider1_value(self, slider_value):
        self.flect1.setText(str(slider_value))
        self.activar_salida_1()
        logging.warning(str(slider_value))
        motor.ChangeDutyCycle(float(slider_value))
    
    def get_slider2_value(self, slider_value):
        self.flect2.setText(str(slider_value))
        self.activar_salida_2()
        logging.warning(str(slider_value))
        motor.ChangeDutyCycle(float(slider_value))

    def get_slider3_value(self, slider_value):
        self.flect3.setText(str(slider_value))
        self.activar_salida_3()
        logging.warning(str(slider_value))      
        motor.ChangeDutyCycle(float(slider_value))

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

GPIO.cleanup()