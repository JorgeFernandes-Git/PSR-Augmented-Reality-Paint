#!/usr/bin/python3
from pprint import pprint

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cv2 import FONT_ITALIC
from cv2.cv2 import LINE_8

def Paint_avalue(Init_image_name):
    area_total_blob = 0
    Total_areas_Blobs = []
    Painted_areas_Blobs = []
    mask_area=[]
    accuracy = []
    results = {}  # Analtino Martinho

    ranges = {'b': {'min': 0, 'max': 256},
              'g': {'min': 0, 'max': 256},
              'r': {'min': 0, 'max': 256}}

    # Processing
    mins = np.array([ranges['b']['min'], ranges['g']['min'], ranges['r']['min']])
    maxs = np.array([ranges['b']['max'], ranges['g']['max'], ranges['r']['max']])

    compare_name = str(Init_image_name) + '4.png'
    image_name = str(Init_image_name) + '.png'

    image = cv2.imread(image_name, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (864, 486))

    # print(compare_name)
    mascaras=[]

    #Base de dados das cores a Utilizar
    color_data_base=[(255, 0, 0),
                    (0, 255, 0),
                    (0, 0, 255)]

    #Chaves para avaliação das Imagens
    keys_of_Bloobs= {'BLOB5_04.png':(1,2,2,3,2,1,1,1,3),
                     'BLOB3_04.png':(1,2,3,3,1),
                     'BLOB4_04.png':(3,3,1,1,2,3,3,3,1,1,2,1,2,2),
                     'BLOB6_04.png':(1,3,3,3,1,1,2,2,2,2,2,3,3)}

    mask = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mask_3 = np.zeros(mask.shape, dtype="uint8")

    output = cv2.connectedComponentsWithStats(mask, 8, cv2.CV_32S)
    (numLabels, labels, stats, centroids) = output

    for i in range(1, numLabels):

        (cX, cY) = centroids[i]

        cv2.putText(image, str(i), (int(cX), int(cY)), FONT_ITALIC, 1, (255, 0, 0), 2, LINE_8)
        cv2.imshow('image', image)

        componentmask=(labels == i).astype("uint8") * 255
        mascaras.append(cv2.bitwise_or(mask_3, componentmask))


    image_a_comparar = cv2.imread(compare_name, cv2.IMREAD_COLOR)
    image_a_comparar = cv2.resize(image_a_comparar, (864, 486))


    cv2.imshow('a_comparar', image_a_comparar)


    for i in range(0,len(mascaras)):

        cv2.imshow('mask_' + str(i), mascaras[i])
        # print(np.array(color_data_base[(keys_of_Bloobs.get(compare_name)[i])-1]))
        mask_range = cv2.inRange(image_a_comparar, mins, np.array(color_data_base[(keys_of_Bloobs.get(compare_name)[i])-1]))

        mask_NEW = cv2.bitwise_and(mascaras[i], mask_range)

        #Apôs muitas horas perdidas o resultado da area da imagem cintinuava a dar valores muito altos
        # o que levou a pensar que a imagem tinha de estar invertida como solução foi necessario fazer '255-mask_NEW'
        output2 = cv2.connectedComponentsWithStats((255-mask_NEW), 8, cv2.CV_32S)
        (numLabels_2, labels_2, stats_2, centroids_2) = output2

        cv2.imshow('mask_NEW' + str(i), mask_NEW)

        Painted_areas_Blobs.append(stats_2[0, cv2.CC_STAT_AREA]/255)
        Total_areas_Blobs.append(stats[i+1, cv2.CC_STAT_AREA]/255)

        accuracy.append((Painted_areas_Blobs[i] / Total_areas_Blobs[i])*100)


    results.update({'Number of areas':len(mascaras),
                    'Areas a pintar':Total_areas_Blobs,
                    'Areas pintadas':Painted_areas_Blobs,
                    'accuracy': accuracy
                    })
    print('')
    pprint(results)
    cv2.waitKey(-1)
    cv2.destroyAllWindows()



