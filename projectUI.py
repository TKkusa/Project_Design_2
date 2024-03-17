import sys, cv2, threading
import mediapipe as mp
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from qt_material import apply_stylesheet
import time
import random


eventTime = 5

class Ui_MainWindow(QtCore.QObject):
    # signals for updating the message and image
    # avoid updating the GUI from a different thread
    update_message_signal = QtCore.pyqtSignal(str)
    update_image_signal = QtCore.pyqtSignal(QImage)

    def __init__(self):
        super().__init__()
        self.ocv = True
        self.teststart = False
        self.pointstart = False
        self.setsize = 50
        self.imagedirection = ' '
        self.pointingdirection = ''

    # button for quit the application
    def quitButton_clicked(self):
        self.ocv = False        
        time.sleep(1)
        sys.exit()      

    # start button function, will be replaced by gesture recognition
    def startButton_clicked(self):
        self.teststart = True
        self.textEdit_3.setText("Ready 5 seconds ro start, please point to the notch direction.")
        
    # function for updating the message 
    def update_message(self, message):
        self.textEdit_3.setText(message)   
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1100, 845)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # change the title of the window
        MainWindow.setWindowTitle("VTABIRD")

        # change the icon of the window
        MainWindow.setWindowIcon(QtGui.QIcon('./icon.png'))

        # only close button available
        MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        # text box for time limit
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(900, 730, 150, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(24)       
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setText("5s")
        self.textEdit.setReadOnly(True)

        # text box for message
        self.textEdit_3 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_3.setGeometry(QtCore.QRect(50, 800, 1000, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(24)
        self.textEdit_3.setObjectName("textEdit_3")
        self.textEdit_3.setText("Please wait for the camera.")
        self.textEdit_3.setReadOnly(True)

        # button for quit the application
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(1570, 780, 100, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(24)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("quitButton")
        self.pushButton.setText("Quit")
        self.pushButton.clicked.connect(self.quitButton_clicked)

        self.textEdit.raise_()
        self.textEdit_3.raise_()        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1130, 25))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        # label for the camera
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(950, 50, 720, 480))

        # label for whiteboard
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(50, 50, 830, 730))
        self.label_2.setStyleSheet("background-color: white;")
        self.label_2.setObjectName("label_2")
        self.label_2.setStyleSheet("background-color: black;")

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # connect the signals to the functions
        self.update_message_signal.connect(self.update_message)

        # button for starting(click and show the image at random place)
        self.pushButton2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton2.setGeometry(QtCore.QRect(1570, 720, 100, 50))
        font = QtGui.QFont()    
        font.setFamily("Arial")
        font.setPointSize(24)
        self.pushButton2.setFont(font)
        self.pushButton2.setObjectName("StartButton")
        self.pushButton2.setText("Start")
        self.pushButton2.clicked.connect(self.startButton_clicked)

        # label for the image of "C"
        self.labelC = QtWidgets.QLabel(self.centralwidget)
        self.labelC.setGeometry(QtCore.QRect(70, 70, 720, 480))

        # timer for any event
        self.mytimer = QtCore.QTimer()
        self.mytimer.timeout.connect(self.onTimer)
        self.mytimer.start(1000)
        self.counter = 5
    
    # function for the image
    def imageprocess(self):
        img = cv2.imread("./C.jpg")
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        output_rotete_90 = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        output_rotete_180 = cv2.rotate(img, cv2.ROTATE_180)
        output_rotate_90_counterclockwise = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

        rotate_pattern = random.randint(0, 3)
        if rotate_pattern == 0:
            img = output_rotete_90
            self.imagedirection = 'down'
        elif rotate_pattern == 1:
            img = output_rotete_180
            self.imagedirection = 'left'
        elif rotate_pattern == 2:
            img = output_rotate_90_counterclockwise
            self.imagedirection = 'up'
        else:
            img = img
            self.imagedirection = 'right'


        img = cv2.resize(img, (self.setsize, self.setsize))
        height, width, channel = img.shape
        bytesPerLine = channel * width

        qimg = QImage(img, width, height, bytesPerLine, QImage.Format_RGB888)
        canvas = QPixmap.fromImage(qimg)

        XBound = random.randint(70, 700)
        YBound = random.randint(-70, 450)
        
        self.labelC.setGeometry(QtCore.QRect(XBound, YBound, 720, 480))

        self.labelC.setPixmap(canvas)

    # timer evemt
    def onTimer(self):
        if self.teststart == True:
            self.counter = self.counter - 1
            self.textEdit.setText(str(self.counter)+"s")
            if self.counter == 0:
                self.pointstart = True
                self.counter = 4
                if self.imagedirection == self.pointingdirection:     
                    if self.setsize > 10:             
                        self.setsize = self.setsize // 2
                else:
                    if self.setsize < 100:
                        self.setsize = self.setsize * 2

                self.imageprocess()
        
    # function for the camera
    def opencv(self):

        cap = cv2.VideoCapture(0)
        mphands = mp.solutions.hands
        hands = mphands.Hands()
        
        mpdraw = mp.solutions.drawing_utils
        handLmsStyle = mpdraw.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=2)
        handConStyle = mpdraw.DrawingSpec(color=(0, 255, 0), thickness=10, circle_radius=2)

        if not cap.isOpened():
            print("Error: Could not open camera.")
            exit()
        else:
            self.update_message_signal.emit("Welcome to VTABIRD! Camera is ready, Please click the start button.")

        # loop for the gesture recognition
        while self.ocv == True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            #adapt the information of the frame
            frame = cv2.resize(frame, (800, 600))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            #flip the frame
            frame = cv2.flip(frame, 1)
          
            result = hands.process(frame)
            imgheight = frame.shape[0]
            imgwidth = frame.shape[1]
            

            if result.multi_hand_landmarks:
                for hand_idx, handLms in enumerate(result.multi_hand_landmarks):
                    mpdraw.draw_landmarks(frame, handLms, mphands.HAND_CONNECTIONS, handLmsStyle, handConStyle)
                    # get the handness 
                    handness_label = "Left" if result.multi_handedness[hand_idx].classification[0].label == "Left" else "Right"
                 
                    # the information of every fingers
                    # thumb
                    thumb_tip = (handLms.landmark[4].x * imgwidth, handLms.landmark[4].y * imgheight)
                    thumb_base = (handLms.landmark[2].x * imgwidth, handLms.landmark[2].y * imgheight)
                    thumb_length = int(((thumb_tip[0] - thumb_base[0])**2 + (thumb_tip[1] - thumb_base[1])**2)**0.5)
                    horizental_distance_thumb = int(thumb_tip[0] - thumb_base[0])
                    vertical_distance_thumb = int(thumb_tip[1] - thumb_base[1])
                    
                    # index
                    index_finger_tip = (handLms.landmark[8].x * imgwidth, handLms.landmark[8].y * imgheight)
                    index_finger_base = (handLms.landmark[5].x * imgwidth, handLms.landmark[5].y * imgheight)   
                    index_length = int(((index_finger_tip[0] - index_finger_base[0])**2 + (index_finger_tip[1] - index_finger_base[1])**2)**0.5)
                    horizental_distance_index = int(index_finger_tip[0] - index_finger_base[0])
                    vertical_distance_index = int(index_finger_tip[1] - index_finger_base[1])

                    # middle
                    middle_finger_tip = (handLms.landmark[12].x * imgwidth, handLms.landmark[12].y * imgheight) 
                    middle_finger_base = (handLms.landmark[9].x * imgwidth, handLms.landmark[9].y * imgheight)
                    middle_length = int(((middle_finger_tip[0] - middle_finger_base[0])**2 + (middle_finger_tip[1] - middle_finger_base[1])**2)**0.5)
                    horizental_distance_middle = int(middle_finger_tip[0] - middle_finger_base[0])
                    vertical_distance_middle = int(middle_finger_tip[1] - middle_finger_base[1])

                    # ring
                    ring_finger_tip = (handLms.landmark[16].x * imgwidth, handLms.landmark[16].y * imgheight)
                    ring_finger_base = (handLms.landmark[13].x * imgwidth, handLms.landmark[13].y * imgheight)
                    ring_length = int(((ring_finger_tip[0] - ring_finger_base[0])**2 + (ring_finger_tip[1] - ring_finger_base[1])**2)**0.5)
                    horizental_distance_ring = int(ring_finger_tip[0] - ring_finger_base[0])
                    vertical_distance_ring = int(ring_finger_tip[1] - ring_finger_base[1])

                    # pinky
                    pinky_finger_tip = (handLms.landmark[20].x * imgwidth, handLms.landmark[20].y * imgheight)
                    pinky_finger_base = (handLms.landmark[17].x * imgwidth, handLms.landmark[17].y * imgheight)
                    pinky_length = int(((pinky_finger_tip[0] - pinky_finger_base[0])**2 + (pinky_finger_tip[1] - pinky_finger_base[1])**2)**0.5)
                    horizental_distance_pinky = int(pinky_finger_tip[0] - pinky_finger_base[0])
                    vertical_distance_pinky = int(pinky_finger_tip[1] - pinky_finger_base[1])

                    # block to analyze the gesture
                    if index_length > 60 and self.pointstart == True and handness_label == "Right":
                        if vertical_distance_index < -60:
                                self.update_message_signal.emit("Pointing up")
                                self.pointingdirection = 'up'
                        elif vertical_distance_index > 60:
                                self.update_message_signal.emit("Pointing down")
                                self.pointingdirection = 'down'
                        elif horizental_distance_index < -60:
                                self.update_message_signal.emit("Pointing left")
                                self.pointingdirection = 'left'
                        elif horizental_distance_index > 60:
                                self.update_message_signal.emit("Pointing right")   
                                self.pointingdirection = 'right'

            # get the frame information
            height, width, channel = frame.shape
            bytesPerLine = channel * width

            # convert the frame to QImage
            qimg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qimg))
        
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    apply_stylesheet(app, theme='dark_teal.xml') 

    vedio = threading.Thread(target=ui.opencv)
    vedio.start()
    MainWindow.showMaximized()

    sys.exit(app.exec_())
