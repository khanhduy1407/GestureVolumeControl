"""
Volume Hand Control Advance
Bởi: NKDuy
"""

import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # pip install pycaw==20181226

###############
wCam, hCam = 640, 480
###############

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

detector = htm.handDetector(detectionCon = 0.7, maxHands = 1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0
area = 0
colorVol = (255, 0, 0)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Tìm tay
    detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw = True)
    if len(lmList) != 0:

        # Bộ lọc dựa trên kích thước
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        # print(area)
        if 250 < area < 1000:

            # Tìm khoảng cách giữa chỉ mục và Ngón cái
            length, img, lineInfo = detector.findDistance(4, 8, img)
            # print(length)

            # Chuyển đổi âm lượng
            # Phạm vi tay 50 - 200
            # Phạm vi âm lượng -65 - 0
            volBar = np.interp(length, [50, 200], [400, 150])
            volPer = np.interp(length, [50, 200], [0, 100])

            # Giảm độ phân giải để làm cho nó mượt mà hơn
            smoothness = 5
            volPer = smoothness * round(volPer / smoothness)

            # Kiểm tra các ngón tay hướng lên
            fingers = detector.fingersUp()
            # print(fingers)

            # Nếu ngón út hướng xuống thì thiết đặt âm lượng
            if not fingers[4]:
                volume.SetMasterVolumeLevelScalar(volPer / 100, None)
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                colorVol = (0, 255, 0)
            else:
                colorVol = (255, 0, 0)

    # Bản vẽ
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)}%', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    cVol = int(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'Set Vol: {int(cVol)}%', (400, 50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3)

    # Tỷ lệ khung hình
    # cTime = time.time()
    # fps = 1 / (cTime - pTime)
    # pTime = cTime
    # cv2.putText(img, f'FPS: {int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    cv2.imshow("Gesture Volume Control", img)
    cv2.waitKey(1)
