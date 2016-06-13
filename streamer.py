#!/usr/bin/python2
import sys
import time
import zmq
import cv2
import datetime

def imageProducer(url):
    cap = cv2.VideoCapture(0)
    try :
        context = zmq.Context()
        print("created zmq.Context()")
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind(url)
        print("bound to " + url)
        # Start your result manager and workers before you start your producers
        while cap.isOpened():
            ret, frame = cap.read()
            ret, frame = cap.read()
            timestamp = datetime.datetime.now()
            work_message = { 'image' : frame, 'timestamp' : timestamp }
            print(timestamp)
            zmq_socket.send_pyobj(work_message)
            print("  sent")
            time.sleep(0.1)
    finally:
        cap.release()


# Call with argument 'tcp://*:5557'
imageProducer(sys.argv[1])
