import sys, cv2, threading
import mediapipe as mp
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtMultimedia import QSound
from qt_material import apply_stylesheet
import random
import eyetest_var as etv

etv.lowest_wrongtimes = -1
etv.level_now = 0.1

class Ui_MainWindow(QtCore.QObject):
    # signals for updating the message and image
    # avoid updating the GUI from a different thread
    update_message_signal = QtCore.pyqtSignal(str)
    update_image_signal = QtCore.pyqtSignal(QImage)
    hide_pushbutton2_signal = QtCore.pyqtSignal(bool)
    qsound = QSound("")

    def __init__(self):
        super().__init__()
        self.round = 1
        self.counter = 10
        self.testeye_now = 'right'
        self.ocv = True
        self.teststart = False
        self.pointstart = False
        self.setsize = 100           
        self.imagedirection = ' '
        self.pointingdirection = ''
        self.cap = None              

    # button for quit the application
    def quitButton_clicked(self):
        self.ocv = False        
        sys.exit()      

    # function for hide the start button
    def hide_pushbutton2(self, visibility):
        self.pushButton2.setVisible(not visibility)

    # start button function, will be replaced by gesture recognition
    def startButton_clicked(self):
        self.teststart = True
        self.pushButton2.setVisible(False)
        self.textEdit_3.setText("Get ready, please cover left eye and point with your right hand.")
        

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
        font.setPointSize(18)       
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setText("10s")
        self.textEdit.setReadOnly(True)

        # text box for message
        self.textEdit_3 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_3.setGeometry(QtCore.QRect(50, 800, 1000, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
        self.textEdit_3.setObjectName("textEdit_3")
        self.textEdit_3.setText("Please wait for the camera.")
        self.textEdit_3.setReadOnly(True)

        # button for quit the application
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(1570, 780, 100, 50))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(18)
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
        font.setPointSize(18)
        self.pushButton2.setFont(font)
        self.pushButton2.setObjectName("StartButton")
        self.pushButton2.setText("Start")
        self.pushButton2.clicked.connect(self.startButton_clicked)
        self.hide_pushbutton2_signal.connect(self.hide_pushbutton2)

        # label for the image of "C"
        self.labelC = QtWidgets.QLabel(self.centralwidget)
        self.labelC.setGeometry(QtCore.QRect(70, 70, 720, 480))

        # timer for any event
        self.mytimer = QtCore.QTimer()
        self.mytimer.timeout.connect(self.onTimer)
        self.mytimer.start(1000)
    

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
 

    # eyetest flow event
    def onTimer(self):
        if self.teststart == True:
            self.counter = self.counter - 1
            self.textEdit.setText(str(self.counter)+"s")

            if self.counter != 0:
                self.qsound.play('./SoundEffect&Others/countdown.wav')

            if self.counter == 0:
                self.labelC.setVisible(True)
                self.pointstart = True
                self.counter = 4
                self.qsound.play('./SoundEffect&Others/countdownEnd.wav')

                print(etv.visionlevel_correctimes, etv.lowest_wrongtimes, etv.level_now)

                self.vision_test()
                self.check_vision_level()
                self.imageprocess()


    # reset every value vision_correctimes dictionary to 0
    def reset_and_init(self):
        for level, times in etv.visionlevel_correctimes.items():
            etv.visionlevel_correctimes[level] = 0
        self.pointstart = False
        self.setsize = 100           
        self.imagedirection = ' '
        self.pointingdirection = ''
        self.round = 2
        self.counter = 11
        self.labelC.setVisible(False)
        etv.lowest_wrongtimes = -1
        etv.level_now = 0.1


    # vision test event handler
    def vision_test(self):
        if etv.level_now == 0.1:     
            if self.pointingdirection == self.imagedirection:  
                etv.visionlevel_correctimes[etv.level_now] += 1           
                etv.level_now = 0.2 
                self.setsize = 50
            else:
                etv.lowest_wrongtimes += 1
                self.setsize = 100
        elif etv.level_now == 0.2:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 0.3
                self.setsize = 33                       
            else:
                etv.level_now = 0.1
                self.setsize = 100
        elif etv.level_now == 0.3:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 0.4
                self.setsize = 25
            else:
                etv.level_now = 0.2
                self.setsize = 50
        elif etv.level_now == 0.4:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 0.5
                self.setsize = 20
            else:
                etv.level_now = 0.3
                self.setsize = 33
        elif etv.level_now == 0.5:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 0.6
                self.setsize = 17
            else:
                etv.level_now = 0.4
                self.setsize = 25
        elif etv.level_now == 0.6:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 0.7
                self.setsize = 14
            else:
                etv.level_now = 0.5
                self.setsize = 20
        elif etv.level_now == 0.7:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 0.8
                self.setsize = 12
            else:
                etv.level_now = 0.6
                self.setsize = 17
        elif etv.level_now == 0.8:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 0.9
                self.setsize = 11
            else:
                etv.level_now = 0.7
                self.setsize = 14
        elif etv.level_now == 0.9:
            if self.pointingdirection == self.imagedirection:

                etv.visionlevel_correctimes[etv.level_now] += 1
                etv.level_now = 1.0
                self.setsize = 10
            else:
                etv.level_now = 0.8
                self.setsize = 12
        elif etv.level_now == 1.0:
            if self.pointingdirection == self.imagedirection:
                etv.visionlevel_correctimes[etv.level_now] += 1
                self.setsize = 10
            else:
                etv.level_now = 0.9
                self.setsize = 11


    # check the vision level of two eyes
    def check_vision_level(self):
        if self.round == 1:
            if etv.lowest_wrongtimes == 3:
                # show the result
                print(f'Your {self.testeye_now} eye is less than 0.1') 
                self.textEdit_3.setText("Round 2, please cover your right eye and point with your left hand.")
            
                # initialize
                self.reset_and_init()
                self.testeye_now = 'left'
            for level, times in etv.visionlevel_correctimes.items():
                if times >= 3:
                    # show the result
                    print(f"Your {self.testeye_now} vision level is {level}.")
                    self.textEdit_3.setText("Round 2, please cover your right eye and point with your left hand.")

                    # initialize
                    self.reset_and_init()
                    self.testeye_now = 'left'
        elif self.round == 2:    
            if etv.lowest_wrongtimes == 3:
                print(f'Your {self.testeye_now} eye is less than 0.1')
                self.ocv = False
                sys.exit()
            for level, times in etv.visionlevel_correctimes.items():
                if times >= 3:
                    print(f"Your {self.testeye_now} vision level is {level}.")
                    self.ocv = False
                    sys.exit()


    # function for the camera
    def opencv(self):
        self.cap = cv2.VideoCapture(0)

        mphands = mp.solutions.hands
        hands = mphands.Hands()
        
        mp_face_detection = mp.solutions.face_detection
        
        mpdraw = mp.solutions.drawing_utils
        handLmsStyle = mpdraw.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=2)
        handConStyle = mpdraw.DrawingSpec(color=(0, 255, 0), thickness=10, circle_radius=2)

        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            exit()
        else:
            self.update_message_signal.emit("Welcome to VTABIRD! Please click the start button or show OK gesture.")
            

        # loop for the gesture recognition
        while self.ocv == True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame.")
                break

            # adapt the information of the frame
            frame = cv2.resize(frame, (800, 600))
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # flip the frame
            frame = cv2.flip(frame, 1)
          
            result = hands.process(frame)

            imgheight = frame.shape[0]
            imgwidth = frame.shape[1]

            # face detection, get the distance between eyes
            if self.teststart == False:
                with mp_face_detection.FaceDetection(min_detection_confidence=0.6) as face_detection:
                    result_face = face_detection.process(frame)
                    if result_face.detections:
                        for detection in result_face.detections:
                            lefteye = int(detection.location_data.relative_keypoints[1].x * imgwidth), int(detection.location_data.relative_keypoints[1].y * imgheight)
                            righteye = int(detection.location_data.relative_keypoints[0].x * imgwidth), int(detection.location_data.relative_keypoints[0].y * imgheight)
                            eyes_xdistance = lefteye[0] - righteye[0]

            if result.multi_hand_landmarks:
                for hand_idx, handLms in enumerate(result.multi_hand_landmarks):
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


                    # Distance between thumb and index finger tip
                    distance_thumb_index = int(((thumb_tip[0] - index_finger_tip[0])**2 + (thumb_tip[1] - index_finger_tip[1])**2)**0.5)

                    # start when OK gesture
                    if distance_thumb_index < 40 and vertical_distance_middle < -80 and vertical_distance_ring < -80 and vertical_distance_pinky < -80 and self.teststart == False:
                        self.teststart = True
                        self.hide_pushbutton2_signal.emit(True)
                        self.update_message_signal.emit("Get ready, please cover left eye and point with your right hand.")
                         

                    # gesture recognition, round 1 right hand
                    if index_length > 70 and self.pointstart == True:
                        if (handness_label == "Right" and self.round == 1) or (handness_label == "Left" and self.round == 2):
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
                    elif index_length < 70 and self.pointstart == True:
                        self.update_message_signal.emit("Can't see the notch, pass.")
                        self.pointingdirection = 'pass'


            # get the frame information
            height, width, channel = frame.shape
            bytesPerLine = channel * width

            # convert the frame to QImage
            qimg = QImage(frame.data, width, height, bytesPerLine, QImage.Format_RGB888)
            self.label.setPixmap(QPixmap.fromImage(qimg))
        
        self.cap.release()
        cv2.destroyAllWindows()


    # Add method to close the camera
    def close_camera(self):
        if self.cap is not None and self.cap.isOpened():
            self.ocv = False


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)

    apply_stylesheet(app, theme='dark_teal.xml') 

    vedio = threading.Thread(target=ui.opencv)
    vedio.start()
    MainWindow.showMaximized()

    # Connect the close event of the main window to close the camera
    MainWindow.closeEvent = ui.close_camera

    sys.exit(app.exec_())
