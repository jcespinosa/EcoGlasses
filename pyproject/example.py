import cv2, numpy
import camera
import features

def processing(frame, wframe):
    temp_feature = features.get_features(wframe)
    temp_descriptor = features.get_descriptor(wframe, temp_feature)

    logo = features.verify_descriptor(temp_descriptor)

    if logo != None:
        print logo

def main():
    cam = camera.CameraIterator(0)
    cam.start(processing, grayscale=True, size=(128, 128), workingCopy = True, show_frame=True, show_wframe=True)

if __name__ == '__main__':
    main()
