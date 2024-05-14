import sys, cv2, threading
import mediapipe as mp
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap, QMovie
from PyQt5.QtMultimedia import QSound
from qt_material import apply_stylesheet
import random
import eyetest_variables as etv
import time

etv.lowest_wrongtimes = -1
etv.level_now = 0.1
language_choice = 'English'

class Ui_MainWindow(QtCore.QObject):
    # signals for updating the message and image
    # avoid updating the GUI from a different thread
    update_message_signal = QtCore.pyqtSignal(str)
    update_distamce_info_signal = QtCore.pyqtSignal(bool)
    update_image_signal = QtCore.pyqtSignal(QImage)
    hide_pushbutton2_signal = QtCore.pyqtSignal(bool)
    choose_pushbutton3_signal = QtCore.pyqtSignal(bool)
    choose_pushbutton4_signal = QtCore.pyqtSignal(bool)
    stop_gif_signal = QtCore.pyqtSignal(bool)
    quit_signal = QtCore.pyqtSignal(bool)  
    
    qsound = QSound("")

    def __init__(self):
        super().__init__()      
        self.round = 1              # round 1 for right eye, round 2 for left eye
        self.counter = 10           # time limit for every event
        self.testeye_now = 'right'  # right eye or left eye
        self.ocv = True             # open the camera or not
        self.teststart = False      # start the test or not
        self.pointstart = False     # start the pointing or not
        self.setsize = 100          # original size of the C image
        self.eye_xdistance = 0      # distance between two eyes
        self.imagedirection = ' '   # direction of the C image
        self.pointingdirection = '' # direction of the pointing
        self.cap = None              
        self.righteye = ''          # result of the right eye
        self.lefteye = ''           # result of the left eye

    # button for quit the application
    def quitButton_clicked(self):
        self.ocv = False        
        sys.exit()      

    # function for hide the start button
    def hide_pushbutton2(self, visibility):
        self.pushButton2.setVisible(not visibility)
        self.pushButton3.setVisible(not visibility)
        self.pushButton4.setVisible(not visibility)
        self.textEdit_6.setVisible(not visibility)
        self.label_2.setVisible(True)
        self.qsound.play('./SoundEffect&Others/Start.wav')

    # hide every widget
    def hide_all(self):
        self.pushButton2.setVisible(False)
        self.pushButton3.setVisible(False)
        self.pushButton4.setVisible(False)
        self.label_2.setVisible(False)
        self.labelC.setVisible(False)
        self.textEdit.setVisible(False)
        self.textEdit_3.setVisible(False)
        self.pushButton.setVisible(False)
        self.textEdit_5.setVisible(False)
        self.textEdit_4.setVisible(True)
    
    #function for set the pushbutton3 black
    def choose_pushbutton3(self, visibility):
        global language_choice       
        if language_choice == 'English':
            self.qsound.play('./SoundEffect&Others/select.wav')
        self.pushButton3.setStyleSheet("font-size: 16pt; background-color: white;")
        self.pushButton4.setStyleSheet("font-size: 16pt; background-color: transparent;")
        language_choice = 'Chinese'
        self.textEdit_2.setText("手勢YA退出應用程式")
        self.textEdit_6.setText("手勢OK開始測試")
        self.textEdit_3.setText("歡迎使用VTABIRD！請選擇您的偏好語言後展示OK手勢。")

    def choose_pushbutton4(self, visibility):
        global language_choice
        if language_choice == 'Chinese':
            self.qsound.play('./SoundEffect&Others/select.wav')
        self.pushButton3.setStyleSheet("font-size: 16pt; background-color: transparent;")
        self.pushButton4.setStyleSheet("font-size: 16pt; background-color: white;")
        language_choice = 'English'
        self.textEdit_2.setText("Gesture YA to quit the application")
        self.textEdit_6.setText("Gesture OK to start the test")
        self.textEdit_3.setText("Welcome to VTABIRD! Please choose your preferred language and then show OK gesture.")

    def stop_gif(self):
        self.loadingmovie.stop()
        self.label_loading.setVisible(False)
        self.label_loadingtext.setVisible(False)
        
    #function for screen to user distance information
    def eye_distance(self):
        global language_choice
        if self.eye_xdistance < 115:
            if language_choice == 'English':
                self.textEdit_5.setText("Please move closer to the camera.")
            else:
                self.textEdit_5.setText("請靠近攝影機。")           
        elif self.eye_xdistance > 130:
            if language_choice == 'English':
                self.textEdit_5.setText("Please move away from the camera.")
            else:
                self.textEdit_5.setText("請遠離攝影機。")
        else:
            if language_choice == 'English':
                self.textEdit_5.setText("The distance is appropriate.")
            else:
                self.textEdit_5.setText("距離適當。")

    # function for updating the message 
    def update_message(self, message):
        self.textEdit_3.setText(message)   
    
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1920, 1080)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # label for background image
        self.label_background = QtWidgets.QLabel(self.centralwidget)
        self.label_background.setGeometry(QtCore.QRect(0, -450, 1920, 1920))
        self.label_background.setObjectName("label_3")
        self.label_background.setStyleSheet("image: url(./background.png);")

        # change the icon of the window
        MainWindow.setWindowIcon(QtGui.QIcon('./icon.png'))

        # only close button available
        MainWindow.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.FramelessWindowHint)

        # text box for time limit
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(900, 730, 150, 50))
        font = QtGui.QFont()     
        self.textEdit.setFont(font)
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setText("10s")
        self.textEdit.setReadOnly(True)
        self.textEdit.setStyleSheet("font-size: 16pt; background-color: transparent;")

        # text box for eye distance
        self.textEdit_5 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_5.setGeometry(QtCore.QRect(50, 730, 830, 50))
        font = QtGui.QFont()
        self.textEdit_5.setFont(font)
        self.textEdit_5.setObjectName("textEdit_5")
        self.textEdit_5.setText("")
        self.textEdit_5.setReadOnly(True)
        self.textEdit_5.setStyleSheet("font-size: 16pt; background-color: transparent;")
        self.update_distamce_info_signal.connect(self.eye_distance)


        # text box for message
        self.textEdit_3 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_3.setGeometry(QtCore.QRect(50, 800, 1000, 50))
        font = QtGui.QFont()
        self.textEdit_3.setObjectName("textEdit_3")
        self.textEdit_3.setText("Please wait for the camera.")
        self.textEdit_3.setReadOnly(True)
        self.textEdit_3.setStyleSheet("font-size: 16pt; background-color: transparent;")

        # button for quit the application
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(1270, 800, 400, 50))
        font = QtGui.QFont()
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("quitButton")
        self.pushButton.setText("Gesture YA to quit the application")
        self.pushButton.clicked.connect(self.quitButton_clicked)
        self.quit_signal.connect(self.quitButton_clicked)
        self.pushButton.setVisible(False)
        self.pushButton.setStyleSheet("font-size: 16pt;")

        #text box for how to quit the application
        self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_2.setGeometry(QtCore.QRect(1330, 800, 400, 50))
        font = QtGui.QFont()
        self.textEdit_2.setObjectName("textEdit_2")
        self.textEdit_2.setText("Gesture YA to quit the application")
        self.textEdit_2.setVisible(True)
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setStyleSheet("font-size: 16pt; background-color: transparent;")

        # text box for how to start the test
        self.textEdit_6 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_6.setGeometry(QtCore.QRect(1330, 730, 400, 50))
        font = QtGui.QFont()
        self.textEdit_6.setObjectName("textEdit_6")
        self.textEdit_6.setText("Gesture OK to start the test")
        self.textEdit_6.setReadOnly(True)
        self.textEdit_6.setStyleSheet("font-size: 16pt; background-color: transparent;")
        self.textEdit_6.setVisible(True)



        # text box for the final result
        self.textEdit_4 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_4.setGeometry(QtCore.QRect(50, 50, 800, 500))
        font = QtGui.QFont()
        self.textEdit_4.setFont(font)
        self.textEdit_4.setObjectName("textEdit_4")
        self.textEdit_4.setText("")
        self.textEdit_4.setVisible(False)
        self.textEdit_4.setReadOnly(True)
        self.textEdit_4.setStyleSheet("font-size: 16pt; background-color: transparent;")

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

        # lable for loading gif
        self.label_loading = QtWidgets.QLabel(self.centralwidget)
        self.label_loading.setGeometry(QtCore.QRect(1250, 150, 200, 200))
        self.label_loading.setObjectName("label_loading")
        self.loadingmovie = QMovie("./loading.gif")
        self.label_loading.setMovie(self.loadingmovie)
        self.loadingmovie.start()
        self.stop_gif_signal.connect(self.stop_gif)

        # label for loading text
        self.label_loadingtext = QtWidgets.QLabel(self.centralwidget)
        self.label_loadingtext.setGeometry(QtCore.QRect(1190, 325, 500, 50))
        self.label_loadingtext.setObjectName("label_loadingtext")
        self.label_loadingtext.setText("Loading camera...")
        self.label_loadingtext.setStyleSheet("font-size: 25pt; color: cyan;")
        self.label_loadingtext.setVisible(True)

        # label for the frame image of the camera
        self.label_cameraframe = QtWidgets.QLabel(self.centralwidget)
        self.label_cameraframe.setGeometry(QtCore.QRect(710, -180, 1200, 1000))
        self.label_cameraframe.setObjectName("label_cameraframe")
        self.label_cameraframe.setStyleSheet("image: url(./cameraframe.png);")

        # label for whiteboard
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(50, 50, 830, 730))
        self.label_2.setObjectName("label_2")
        self.label_2.setStyleSheet("background-color: black; border: 3px solid white;")
        self.label_2.setVisible(False)


        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # connect the signals to the functions
        self.update_message_signal.connect(self.update_message)

        # button for starting
        self.pushButton2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton2.setGeometry(QtCore.QRect(1570, 720, 100, 50))
        font = QtGui.QFont()    
        self.pushButton2.setFont(font)
        self.pushButton2.setObjectName("StartButton")
        self.pushButton2.setText("Start")
        self.pushButton2.setStyleSheet("font-size: 16pt;") 
        self.hide_pushbutton2_signal.connect(self.hide_pushbutton2)
        self.pushButton2.setVisible(False)

        #button for change to Chinese
        self.pushButton3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton3.setGeometry(QtCore.QRect(400, 250, 150, 50))
        font = QtGui.QFont()
        self.pushButton3.setFont(font)
        self.pushButton3.setObjectName("ChineseButton")
        self.pushButton3.setText("中文")
        self.pushButton3.setStyleSheet("font-size: 16pt; background-color: transparent;")
        self.choose_pushbutton3_signal.connect(self.choose_pushbutton3)
        
        #button for change to English
        self.pushButton4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton4.setGeometry(QtCore.QRect(400, 350, 150, 50))
        font = QtGui.QFont()
        self.pushButton4.setFont(font)
        self.pushButton4.setObjectName("EnglishButton")
        self.pushButton4.setText("English")
        self.pushButton4.setStyleSheet("font-size: 16pt; background-color: white;")
        self.choose_pushbutton4_signal.connect(self.choose_pushbutton4)
        
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
        global language_choice
        if self.round == 1:
            if etv.lowest_wrongtimes == 3:
                # show the result
                if language_choice == 'English':
                    self.righteye = f'Your right eye vision level is less than 0.1'
                elif language_choice == 'Chinese':
                    self.righteye = f'您的右眼視力等級小於0.1'    
                if language_choice == 'English':
                    self.textEdit_3.setText("Round 2, please cover your right eye and point with your left hand.")       
                elif language_choice == 'Chinese':
                    self.textEdit_3.setText("第二輪，請遮住右眼，用左手指出缺口方向。")
            
                # initialize
                self.reset_and_init()
                self.testeye_now = 'left'
            for level, times in etv.visionlevel_correctimes.items():
                if times >= 3:
                    # show the result
                    if language_choice == 'English':
                        self.righteye = f"Your right eye vision level is approximately {level}."
                    elif language_choice == 'Chinese':
                        self.righteye = f"您的右眼視力等級約為{level}。"
                    if language_choice == 'English':
                        self.textEdit_3.setText("Round 2, please cover your right eye and point with your left hand.")
                    elif language_choice == 'Chinese':
                        self.textEdit_3.setText("第二輪，請遮住右眼，用左手指出缺口方向.")

                    # initialize
                    self.reset_and_init()
                    self.testeye_now = 'left'
        elif self.round == 2:    
            if etv.lowest_wrongtimes == 3:
                if language_choice == 'English':
                    self.lefteye = f'Your left eye vision level is less than 0.1'
                elif language_choice == 'Chinese':
                    self.lefteye = f'您的左眼視力等級小於0.1'
                self.textEdit_4.setText(f"{self.righteye}\n\n{self.lefteye}")
                self.hide_all()
                self.mytimer.stop()
            for level, times in etv.visionlevel_correctimes.items():
                if times >= 3:
                    if language_choice == 'English':
                        self.lefteye = f"Your left eye vision level is approximately {level}."
                    elif language_choice == 'Chinese':
                        self.lefteye = f"您的左眼視力等級約為{level}。"
                    self.textEdit_4.setText(f"{self.righteye}\n\n{self.lefteye}")
                    self.hide_all()
                    self.mytimer.stop()

    # function for the camera
    def opencv(self):
        global language_choice
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
            self.update_message_signal.emit("Welcome to VTABIRD! Please choose your preferred language and show OK gesture.")
            self.stop_gif_signal.emit(True)
            

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
                            self.eye_xdistance = lefteye[0] - righteye[0]
                            self.update_distamce_info_signal.emit(True)
                            
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

                    # gesture for choosing the language
                    if index_length > 70 and self.teststart == False:
                        if vertical_distance_index < -60:
                            self.choose_pushbutton3_signal.emit(True)
                        elif vertical_distance_index > 60:
                            self.choose_pushbutton4_signal.emit(True)

                    # gesture YA for quit the application
                    if vertical_distance_index < -120 and vertical_distance_middle < -120 and vertical_distance_ring > -30 and vertical_distance_pinky > -30:
                        self.quit_signal.emit(True)

                    # start when OK gesture
                    if distance_thumb_index < 30 and vertical_distance_middle < -100 and vertical_distance_ring < -100 and vertical_distance_pinky < -100 and self.teststart == False and self.eye_xdistance >= 115 and self.eye_xdistance <= 130:
                        self.teststart = True
                        self.hide_pushbutton2_signal.emit(True)
                        if language_choice == 'English':
                            self.update_message_signal.emit("Get ready, please cover left eye and point with your right hand.")
                        elif language_choice == 'Chinese':
                            self.update_message_signal.emit("準備好了嗎？請遮住左眼，用右手指出缺口方向。")                                    

                    # gesture recognition, round 1 right hand
                    if index_length > 70 and self.pointstart == True:
                        if (handness_label == "Right" and self.round == 1) or (handness_label == "Left" and self.round == 2):
                            if vertical_distance_index < -100:
                                if language_choice == 'English':
                                    self.update_message_signal.emit("Pointing up")
                                elif language_choice == 'Chinese':
                                    self.update_message_signal.emit("指向上方")
                                self.pointingdirection = 'up'
                            elif vertical_distance_index > 100:
                                if language_choice == 'English':
                                    self.update_message_signal.emit("Pointing down")
                                elif language_choice == 'Chinese':
                                    self.update_message_signal.emit("指向下方")
                                self.pointingdirection = 'down'
                            elif horizental_distance_index < -50:
                                if language_choice == 'English':
                                    self.update_message_signal.emit("Pointing left")
                                elif language_choice == 'Chinese':
                                    self.update_message_signal.emit("指向左方")
                                self.pointingdirection = 'left'
                            elif horizental_distance_index > 50:
                                if language_choice == 'English':
                                    self.update_message_signal.emit("Pointing right")
                                elif language_choice == 'Chinese':
                                    self.update_message_signal.emit("指向右方")
                                self.pointingdirection = 'right'
                    elif index_length < 70 and self.pointstart == True:
                        if language_choice == 'English':
                            self.update_message_signal.emit("Can't see the notch, pass.")
                        elif language_choice == 'Chinese':
                            self.update_message_signal.emit("看不清楚缺口，跳過。")
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

    main_ui = Ui_MainWindow()
    main_ui.setupUi(MainWindow)

    apply_stylesheet(app, theme='dark_cyan.xml') 

    vedio = threading.Thread(target=main_ui.opencv)
    vedio.start()
    MainWindow.showMaximized()

    # Connect the close event of the main window to close the camera
    MainWindow.closeEvent = main_ui.close_camera

    sys.exit(app.exec_())
