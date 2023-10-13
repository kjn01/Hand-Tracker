import cv2 as cv
import mediapipe as mp
from pynput.mouse import Button, Controller
from threading import Thread
import pyautogui as gui
import time

global stopHold
global stopRel

class HandDetector():
    def __init__(self, mode = False, max_hands = 1, detect_conf = 0.5, track_conf = 0.5):
        self.mode = mode
        self.max_hands = max_hands
        self.detect_conf = detect_conf
        self.track_conf = track_conf

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode = self.mode, max_num_hands = self.max_hands, min_detection_confidence = self.detect_conf, min_tracking_confidence = self.track_conf)
        self.mp_draw = mp.solutions.drawing_utils
    
    def find_hands(self, frame, draw = True):
        self.results = self.hands.process(frame)
        
        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        
        return frame
    
    def find_position(self, frame, hand_no = 0, draw = True):
        lm_list = []
        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[hand_no]
            for id, lm in enumerate(my_hand.landmark):
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])
                if draw:
                    cv.putText(frame, str(id), (cx, cy), cv.FONT_HERSHEY_COMPLEX, 3, (255, 0, 255), 1)
        
        return lm_list

def main():
    capture = cv.VideoCapture(0)
    detector = HandDetector()
    mouse = Controller()
    pressed = False
    clicked = False
    prev = (0, 0)

    while True:
        ret, frame = capture.read()
        frame = cv.resize(frame, (int(1920*1.3), int(1080*1.3)))
        frame = detector.find_hands(frame)
        lm_list = detector.find_position(frame)
        xS = 0
        yS = 0
        l = len(lm_list)

        if l != 0:
            current = (1920-(lm_list[9][1]), (lm_list[9][2]))
            if abs(prev[0] - current[0]) < 1 and abs(prev[1] - current[1]) < 1:
                mouse.position = prev
            else:
                mouse.position = current
                prev = current
            
            xS = abs(lm_list[8][1]-lm_list[4][1])
            yS = abs(lm_list[8][2]-lm_list[4][2])
            # print(str(xS) +  ", " + str(yS))

            xScrollDown = abs(lm_list[12][1]-lm_list[4][1])
            yScrollDown = abs(lm_list[12][2]-lm_list[4][2])
            xScrollUp = abs(lm_list[16][1]-lm_list[4][1])
            yScrollUp = abs(lm_list[16][2]-lm_list[4][2])

            xSelect = abs(lm_list[20][1]-lm_list[4][1])
            ySelect = abs(lm_list[20][2]-lm_list[4][2])

            if xS < 30 and yS < 90 and not clicked:
                print("clicked")
                clicked = True
                mouse.click(Button.left)
            elif xSelect < 30 and ySelect < 90 and not pressed:
                print("pressed")
                pressed = True
                mouse.press(Button.left)
            elif xSelect >= 30 and ySelect >= 90 and pressed:
                print("released")
                pressed = False
                mouse.release(Button.left)
            elif xScrollDown < 20 and yScrollDown < 50:
                print("down")
                mouse.scroll(0, -1)
            elif xScrollUp < 20 and yScrollUp < 50:
                print("up")
                mouse.scroll(0, 1)
            
            if xS >= 30 and yS >= 90 and clicked:
                clicked = False

        # cv.imshow('frame', frame)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    main()