#!/usr/bin/python2
import time
import zmq
import cv2
import datetime
import argparse
import numpy as np

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

    cv2.waitKey(1)

def showSift(img):
    gray= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

    #sift = cv2.xfeatures2d.SIFT_create()
    #(kp, descs) = sift.detectAndCompute(gray,None)

    sift = cv2.xfeatures2d.SIFT_create()
    kp = sift.detect(gray,None)

    img3 = np.zeros((1,1))
    img=cv2.drawKeypoints(gray,kp, img3)

    cv2.imshow('sift keypoints',img)

def consumer(url):
    context = zmq.Context()
    # recieve {image, timestamp}
    consumer_receiver = context.socket(zmq.PULL)
    consumer_receiver.set_hwm(1)
    consumer_receiver.connect(url)
    # send output..
    #consumer_sender = context.socket(zmq.PUSH)
    #consumer_sender.connect("tcp://127.0.0.1:5558")
    
    while True:
        work = consumer_receiver.recv_pyobj()
        image = work['image']
        timestamp = work['timestamp']

        showHarris(image)
        #showSift(image)

        cv2.putText(image, str(timestamp), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (255,255,0))
        cv2.imshow('frame',image)

        cv2.waitKey(1)

parser = argparse.ArgumentParser(description='Receive images from 0MQ for processing.')
parser.add_argument('--url', help='url of the streamer ("tcp://192.168.1.200:5557")')

args = parser.parse_args()
consumer(args.url)
