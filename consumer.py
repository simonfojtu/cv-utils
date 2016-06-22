#!/usr/bin/python2
import time
import zmq
import cv2
import datetime
import argparse
import numpy as np
from sets import Set

import ocv_calibration

def showHarris(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    gray = np.float32(gray)

    # harris
    blockSize = 7
    ksize = 3
    k = 0.04
    dst = cv2.cornerHarris(gray, blockSize, ksize, k)

    #result is dilated for marking the corners, not important
    #dst = cv2.dilate(dst,None)
    
    # Threshold for an optimal value, it may vary depending on the image.
    img = image.copy()
    img[dst>0.2015*dst.max()]=[0,0,255]

    cv2.imshow('harris',img)

    #cv2.waitKey(1)

def showSift(img):
    gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    #sift = cv2.xfeatures2d.SIFT_create()
    #(kp, descs) = sift.detectAndCompute(gray,None)

    sift = cv2.xfeatures2d.SIFT_create()
    kp = sift.detect(gray,None)

    img3 = np.zeros((1,1))
    img=cv2.drawKeypoints(gray,kp, img3)

    cv2.imshow('sift keypoints',img)

def drawOCVCorners(image):
    img = image.copy()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(gray, (7,6),None)

    # If found, add object points, image points (after refining them)
    if ret == True:

        corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, (7,6), corners2,ret)
        cv2.imshow('ocv corners',img)

def drawCorners(img):
    min_dilations = 0
    max_dilations = 7
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    for k in range(0, 6):
        for dilations in range(min_dilations, max_dilations):
    
            #cv2.adaptiveThreshold(img, thresh_img, 255,
            #        cv2.CV_ADAPTIVE_THRESH_MEAN_C, CV_THRESH_BINARY, block_size, (k/2)*5)
    
            #if dilations > 0:
            #    thresh_img = cv2.dilate(thresh_img, 0, dilations - 1)

            mean = cv2.mean(gray)[0]
            thresh_level = int(mean - 10)
            thresh_level = max(thresh_level, 10)

            retval, thresh_img = cv2.threshold(gray, thresh_level, 255, cv2.THRESH_BINARY)
            cv2.dilate(thresh_img, None, thresh_img, (-1,-1), dilations)

            rows = len(thresh_img)
            cols = len(thresh_img[0])
                    
            cv2.rectangle(thresh_img, (0, 0), (cols-1, rows-1), (255, 255, 255), 3, 8)
            
            cv2.imshow("drawCorners: thresh_img " + str(k*0) + str(dilations), thresh_img)
            cv2.waitKey(1)

    
def drawCircles(image):
    gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (13, 13), 6)

    circles = cv2.HoughCircles(gray,cv2.HOUGH_GRADIENT,1,20,
                                        param1=50,param2=30,minRadius=9,maxRadius=0)

    circles = np.uint16(np.around(circles))

    img = gray.copy()
    if not circles is None:
        for circle in circles[0]:
            c = (circle[0], circle[1])
            r = circle[2]
            cv2.circle(img, c, r, 255, 4)
    cv2.imshow("circles", img)




def consumer(url):
    context = zmq.Context()
    # recieve {image, timestamp}
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.set_hwm(1)
    consumer_receiver.connect(url)
    # send output..
    #consumer_sender = context.socket(zmq.PUSH)
    #consumer_sender.connect("tcp://127.0.0.1:5558")
    
    images = []

    while True:
        work = consumer_receiver.recv_pyobj()
        image = work['image']
        timestamp = work['timestamp']

        key = cv2.waitKey(1)
        if key != -1:
            # 's'
            if key == 115:
                print('image captured')
                images.append(image)
                print(images)
                cv.imwrite(str(timestamp) + '.png', image)

            # 'c'
            if key == 99:
                print('calibration started')
                calib = ocv_calibration.OCV_calibration()
                print(calib.calibrate(images))

            if key == 27:
                return

        #showHarris(image)
        #showSift(image)
        #drawOCVCorners(image)
        #drawCorners(image)
        drawCircles(image)

        cv2.putText(image, str(timestamp), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (255,255,0))
        cv2.imshow('frame',image)



parser = argparse.ArgumentParser(description='Receive images from 0MQ for processing.')
parser.add_argument('--url', help='url of the streamer ("tcp://192.168.1.200:5557")')

args = parser.parse_args()
consumer(args.url)
