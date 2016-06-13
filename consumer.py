#!/usr/bin/python2
import time
import zmq
import random
import cv2
import datetime
import argparse

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
        cv2.putText(image, str(timestamp), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.37, (255,255,0))
        cv2.imshow('frame',image)
        cv2.waitKey(1)

parser = argparse.ArgumentParser(description='Receive image from 0MQ.')
parser.add_argument('--url', help='url of the streamer ("tcp://192.168.1.200:5557"')

args = parser.parse_args()
consumer(args.url)
