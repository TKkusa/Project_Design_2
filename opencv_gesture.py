import cv2 
import mediapipe as mp
import time
import math

cap = cv2.VideoCapture(0)
mphands = mp.solutions.hands
hands = mphands.Hands()
mpdraw = mp.solutions.drawing_utils
handLmsStyle = mpdraw.DrawingSpec(color=(0, 0, 255), thickness=5, circle_radius=2)
handConStyle = mpdraw.DrawingSpec(color=(0, 255, 0), thickness=10, circle_radius=2)
pTime = 0
cTIME = 0

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml') 

while True:
    ret, img = cap.read()
    if ret:

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

        #draw the rectangle around the face
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

        

        
        result = hands.process(imgRGB)
        # print(result.multi_hand_landmarks)
        imgheight = img.shape[0]
        imgwidth = img.shape[1]

        if result.multi_hand_landmarks:
            for hand_idx, handLms in enumerate(result.multi_hand_landmarks):                
                mpdraw.draw_landmarks(img, handLms, mphands.HAND_CONNECTIONS, handLmsStyle, handConStyle)

                # the information of every fingers
                thumb_tip = (handLms.landmark[4].x * imgwidth, handLms.landmark[4].y * imgheight)
                thumb_base = (handLms.landmark[2].x * imgwidth, handLms.landmark[2].y * imgheight)
                thumb_length = int(((thumb_tip[0] - thumb_base[0])**2 + (thumb_tip[1] - thumb_base[1])**2)**0.5)

                index_finger_tip = (handLms.landmark[8].x * imgwidth, handLms.landmark[8].y * imgheight)
                index_finger_base = (handLms.landmark[5].x * imgwidth, handLms.landmark[5].y * imgheight)   
                index_length = int(((index_finger_tip[0] - index_finger_base[0])**2 + (index_finger_tip[1] - index_finger_base[1])**2)**0.5)

                horizental_distance = int(index_finger_tip[0] - index_finger_base[0])
                vertical_distance = int(index_finger_tip[1] - index_finger_base[1])

                middle_finger_tip = (handLms.landmark[12].x * imgwidth, handLms.landmark[12].y * imgheight) 
                middle_finger_base = (handLms.landmark[9].x * imgwidth, handLms.landmark[9].y * imgheight)
                middle_length = int(((middle_finger_tip[0] - middle_finger_base[0])**2 + (middle_finger_tip[1] - middle_finger_base[1])**2)**0.5)

                ring_finger_tip = (handLms.landmark[16].x * imgwidth, handLms.landmark[16].y * imgheight)
                ring_finger_base = (handLms.landmark[13].x * imgwidth, handLms.landmark[13].y * imgheight)
                ring_length = int(((ring_finger_tip[0] - ring_finger_base[0])**2 + (ring_finger_tip[1] - ring_finger_base[1])**2)**0.5)

                pinky_finger_tip = (handLms.landmark[20].x * imgwidth, handLms.landmark[20].y * imgheight)
                pinky_finger_base = (handLms.landmark[17].x * imgwidth, handLms.landmark[17].y * imgheight)
                pinky_length = int(((pinky_finger_tip[0] - pinky_finger_base[0])**2 + (pinky_finger_tip[1] - pinky_finger_base[1])**2)**0.5)

                # analyze the gesture
                if index_length > 60:
                    if vertical_distance < -70:
                        print("Pointing up")
                    elif vertical_distance > 70:
                        print("Pointing down")
                    elif horizental_distance < -80:
                        print("Pointing right")
                    elif horizental_distance > 80:
                        print("Pointing left")

        cTIME = time.time() 
        fps = 1/(cTIME - pTime) 
        pTime = cTIME
        cv2.putText(img, f"FPS : {int(fps)}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)

        cv2.imshow("img", img)

    if cv2.waitKey(1) == ord('q'):
        break