#! /usr/bin/python 
# -*- coding: utf-8 -*-

import cv2, numpy

def calculate_resize(actual_size, input_size):
    if actual_size[0] > actual_size[1]:
        if input_size[0] > input_size[1]:
            rate_change = float(input_size[0]) / actual_size[0]
        else:
            rate_change = float(input_size[1]) / actual_size[0]
    else:
        actual_size[1]
        if input_size[0] > input_size[1]:
            rate_change = float(input_size[0]) / actual_size[1]
        else:
            rate_change = float(input_size[1]) / actual_size[1]

    return (int(actual_size[0]*rate_change), int(actual_size[1]*rate_change))


class CameraIterator:
    
    def __init__(self, camera_index):
        self.cam = cv2.VideoCapture(0)
        if not self.cam.isOpened():
            print "ERROR:: No fue posible acceder a la cámara"
            return None
        
    def start(self, f, grayscale=False, size=None, workingCopy = False, show_frame=False, show_wframe=False):
        while True:
            retval, frame = self.cam.read()
            
            if workingCopy:
                wframe = frame.copy()
                if size != None:
                    wframe = cv2.resize(wframe, 
                                        calculate_resize( (wframe.shape[1], wframe.shape[0]),
                                                          size)
                                        )
                if grayscale:
                    wframe = cv2.cvtColor(wframe, cv2.COLOR_BGR2GRAY)
                f(frame, wframe)
            else:
                f(frame)

            if show_frame: 
                cv2.imshow('frame', frame)
            if show_wframe:
                cv2.imshow('wframe', wframe)
            
            key = cv2.waitKey(20)
            if key in (ord('Q'), ord('q')):
                break

    def __del__(self):
        self.cam.release()


def main():
    cam = CameraIterator(0)
    cam.start(lambda frame, i=0: i)

if __name__ == '__main__':
    main()
