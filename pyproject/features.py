#! /usr/bin/python                                                                                                                            
# -*- coding: utf-8 -*- 

import cv2, numpy

from camera import calculate_resize

#
#descriptor_algorithm = 'HARRIS'
#feature_algorithm = 'BRIEF'
descriptor_algorithm = 'SURF'
feature_algorithm = 'SURF'
matcher_algorithm = 'FlannBased'

if matcher_algorithm == 'FlannBased':
    index_params = dict(algorithm = 0, trees = 5)
    search_params = dict(checks = 50) 
    flann = cv2.FlannBasedMatcher(index_params,search_params)
    descriptor_matcher = cv2.FlannBasedMatcher(index_params,search_params)
#
feature_detector = cv2.FeatureDetector_create (feature_algorithm)
feature_descriptor = cv2.DescriptorExtractor_create (descriptor_algorithm)
#descriptor_matcher = cv2.DescriptorMatcher.create (matcher_algorithm)

def get_features(img):
    return feature_detector.detect(img)

def get_descriptor(img, features):
    return feature_descriptor.compute(img, features)[1]


list_reference_images = (
    './logotipos/carnes_finas_san_juan_res.jpg',
    './logotipos/carnes_finas_san_juan.jpg',
    './logotipos/chocokrispis.png',
    './logotipos/metrorrey.png'
    )
#global_list_reference_descriptor = None

def get_reference_descriptors():
    #global global_list_reference_descriptor, list_reference_images
    global descriptor_matcher, list_reference_images

    list_reference_descriptors = list()
    for img_path in list_reference_images:
        image = cv2.imread(img_path , cv2.CV_LOAD_IMAGE_COLOR)
        if image == None:
            print "No se pudo abrir:", img_path 
            continue
        image = cv2.resize(
            image, calculate_resize(
                (int(image.shape[1]), int(image.shape[0])),
                (128, 128)
                ) 
            )

        temp_features = get_features(image)
        print "imagen:", img_path, "N:", len(temp_features)
        temp_descriptor = get_descriptor(image, temp_features)
        list_reference_descriptors.append(temp_descriptor)

    for des in list_reference_descriptors:
        descriptor_matcher.add(des)
        descriptor_matcher.train()


get_reference_descriptors()


def verify_descriptor(descriptor, list_reference_descriptors=None):

    matches = descriptor_matcher.match(queryDescriptors=descriptor)

    print dir(descriptor_matcher)
    
    for v in matches:
        print v.queryIdx, v.trainIdx, v.imgIdx
#        if len(v) < 2:
#            break
#        m, n = v
#        if m.distance < 0.8*n.distance:
#            print m.imgIdx
#            #point = reference_keypoints[n.queryIdx]

    return None

def main():
    pass

if __name__ == '__main__':
    main()
