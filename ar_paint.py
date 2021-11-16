#!/usr/bin/python3

import argparse
import copy
import json
import math
from functools import partial
import cv2
import numpy as np
from cv2 import FONT_ITALIC, LINE_8
from time import ctime

# dictionary with ranges
ranges_pcss = {"b": {"min": 100, "max": 256},
               "g": {"min": 100, "max": 256},
               "r": {"min": 100, "max": 256},
               }

drawing = False  # true if mouse is pressed
# mode = str('rectangle') # if 'rectangle', draw rectangle.
ix, iy = -1, -1

# create a white image background
background = np.zeros((422, 750, 3), np.uint8)
background.fill(255)


def shape(event, x, y, flags, params, mode):
    global ix, iy, drawing

    if event == cv2.EVENT_LBUTTONDOWN:
        # value of variable draw will be set to True, when you press DOWN left mouse button
        drawing = True
        # mouse location is captured here
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        # Dragging the mouse at this juncture
        if drawing:
            if mode == 'rectangle':
                # If draw is True then it means you've clicked on the left mouse button
                # Here we will draw a rectangle from previous position to the x,y where the mouse is currently located
                cv2.rectangle(background, (ix, iy), (x, y), (0, 255, 0), 3)
                # Nas ultimas cordenadas devo desenhar um retangulo da cor do fundo
                a = x
                b = y
                if a != x | b != y:
                    cv2.rectangle(background, (ix, iy), (x, y), (255, 255, 255), -1)
            if mode == 'circle':
                radius = math.pow(((math.pow(x, 2) - math.pow(ix, 2)) + (math.pow(y, 2) - math.pow(iy, 2))), 1 / 2)
                cv2.circle(background, (ix, iy), int(radius), (0, 0, 255), 3)
                a = x
                b = y
                if a != x | b != y:
                    radius = math.pow(((math.pow(x, 2) - math.pow(ix, 2)) + (math.pow(y, 2) - math.pow(iy, 2))), 1 / 2)
                    cv2.circle(background, (ix, iy), int(radius), (255, 255, 255), -1)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == 'rectangle':
            # As soon as you release the mouse button, variable draw will be set as False
            # Here we are completing to draw the rectangle on image window
            # background=clone
            cv2.rectangle(background, (ix, iy), (x, y), (0, 255, 0), 2)

        if mode == 'circle':
            radius = math.pow(((math.pow(x, 2) - math.pow(ix, 2)) + (math.pow(y, 2) - math.pow(iy, 2))), 1 / 2)
            cv2.circle(background, (ix, iy), int(radius), (0, 0, 255), 3)


def main():
    """
    INITIALIZE -----------------------------------------
    """
    # program flags
    background_white = True  # background color
    pointer_on = False  # pointer method incomplete
    rect_drawing = False  # rectangle drawing flag
    circle_drawing = False  # circle drawing flag
    shake_prevention = False

    # variables
    dot_x, dot_y = 0, 0  # pen points
    prev_x, prev_y = 0, 0  # point for continuous draw
    rect_pt1_x, rect_pt1_y, rect_pt2_x, rect_pt2_y = 0, 0, 0, 0  # rectangle drawing points
    circle_pt1_x, circle_pt1_y, circle_pt2_x, circle_pt2_y = 0, 0, 0, 0  # circle drawing points

    # parse the json file with BGR limits (from color_segmenter.py)
    parser = argparse.ArgumentParser(description="Load a json file with limits")
    parser.add_argument("-j", "--json", type=str, required=True, help="Full path to json file")
    parser.add_argument("-usp", "--use_shake_prevention", action="store_true", help="Activating shake prevention")
    args = vars(parser.parse_args())

    # activate shake prevention
    if args["use_shake_prevention"]:
        shake_prevention = True

    # read the json file
    with open(args["json"], "r") as file_handle:
        data = json.load(file_handle)

    # print json file then close
    print(data)
    file_handle.close()

    ranges_pcss["b"]["min"] = data["b"]["min"]
    ranges_pcss["b"]["max"] = data["b"]["max"]
    ranges_pcss["g"]["min"] = data["g"]["min"]
    ranges_pcss["g"]["max"] = data["g"]["max"]
    ranges_pcss["r"]["min"] = data["r"]["min"]
    ranges_pcss["r"]["max"] = data["r"]["max"]

    # print(ranges_pcss)  # debug

    # numpy arrays
    mins_pcss = np.array([ranges_pcss['b']['min'], ranges_pcss['g']['min'], ranges_pcss['r']['min']])
    maxs_pcss = np.array([ranges_pcss['b']['max'], ranges_pcss['g']['max'], ranges_pcss['r']['max']])

    # initial setup
    capture = cv2.VideoCapture(0)  # connect to webcam

    # create canvas image to join draw and video
    image_canvas = np.zeros((422, 750, 3), np.uint8)

    # pen variables
    pen_color = (0, 0, 0)
    pen_thickness = 5

    """
    EXECUTION -----------------------------------------
    """
    while True:
        # read the image
        _, image = capture.read()
        image = cv2.resize(image, (750, 422))  # resize the capture window
        image = cv2.flip(image, 1)  # flip video capture

        # transform the image and show it
        mask = cv2.inRange(image, mins_pcss, maxs_pcss)  # colors mask
        image_segmenter = cv2.bitwise_and(image, image, mask=mask)

        # get contours
        contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        # create the rectangle over object and draw on the background
        for contours in contours:
            (x, y, w, h) = cv2.boundingRect(contours)

            # draw the rectangle only if the area is > 3000 px for preventing multiple detections
            if cv2.contourArea(contours) < 3000:
                continue

            # draw the rectangle over detected object
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # center of the rectangle
            dot_x = x + w / 2
            dot_y = y + h / 2

            # Draw cruz vermelha sobre o centroid da imagem
            cv2.putText(image, '+', (int(dot_x), int(dot_y)), FONT_ITALIC, 1, (255, 0, 0), 2, LINE_8)

            # mode for cursor only
            if not pointer_on:
                # draw in the background
                if prev_x == 0 and prev_y == 0:  # skip first iteration
                    prev_x, prev_y = dot_x, dot_y

                # Activating shake prevention
                if shake_prevention:
                    if abs(prev_x - dot_x) < 50 and abs(prev_y - dot_y) < 50:
                        cv2.line(background, (int(prev_x), int(prev_y)), (int(dot_x),
                                                                          int(dot_y)), pen_color, pen_thickness)
                        cv2.line(image_canvas, (int(prev_x), int(prev_y)), (int(dot_x), int(dot_y)), pen_color,
                                 pen_thickness)
                        prev_x, prev_y = dot_x, dot_y
                    else:
                        prev_x, prev_y = 0, 0
                else:
                    cv2.line(background, (int(prev_x), int(prev_y)), (int(dot_x),
                                                                      int(dot_y)), pen_color, pen_thickness)
                    cv2.line(image_canvas, (int(prev_x), int(prev_y)), (int(dot_x), int(dot_y)), pen_color,
                             pen_thickness)
                    prev_x, prev_y = dot_x, dot_y

            else:
                if background_white:
                    background.fill(255)
                else:
                    background.fill(0)
                # background.fill(255)
                # cv2.circle(background, (int(dot_x), int(dot_y)), pen_thickness, pen_color, cv2.FILLED)
                cv2.putText(background, '+', (int(dot_x), int(dot_y)), FONT_ITALIC, 1, (255, 0, 0), 2, LINE_8)

        # merge the video and the drawing ----------------------------INCOMPLETE DOESN'T DRAW THE BLACK COLOR
        image_gray = cv2.cvtColor(image_canvas, cv2.COLOR_BGR2GRAY)
        _, image_inverse = cv2.threshold(image_gray, 50, 255, cv2.THRESH_BINARY_INV)

        # join frames
        final_frame_h1 = cv2.hconcat((image, background))

        # DUPLICAR IMAGEM ------------------------------------------------
        image_copy = copy.deepcopy(image)

        # join video and drawing
        image_inverse = cv2.cvtColor(image_inverse, cv2.COLOR_GRAY2BGR)
        image_copy = cv2.bitwise_and(image_copy, image_inverse)
        image_copy = cv2.bitwise_or(image_copy, image_canvas)

        # horizontally concatenating the two frames.
        final_frame_h2 = cv2.hconcat((image_segmenter, image_copy))
        final_frame = cv2.vconcat((final_frame_h1, final_frame_h2))

        # Show the concatenated frame using imshow.
        cv2.imshow('frame', final_frame)

        """
        interactive keys (k) -----------------------------------------
        """
        # ESC and q to close
        k = cv2.waitKey(1) & 0xFF
        if k == 27 or k == ord("q"):
            break

        # clean the screen
        if k == ord("c"):
            if background_white:
                background.fill(255)
                image_canvas.fill(0)
                print("CLEAN")
            else:
                background.fill(0)

        # red color
        if k == ord("r"):
            pen_color = (0, 0, 255)
            print("YOU SELECT RED COLOR")

        # green color
        if k == ord("g"):
            pen_color = (0, 255, 0)
            print("YOU SELECT GREEN COLOR")

        # blue color
        if k == ord("b"):
            pen_color = (255, 0, 0)
            print("YOU SELECT BLUE COLOR")

        # black color
        if k == ord("B"):
            if background_white:
                pen_color = (0, 0, 0)
                print("YOU SELECT BLACK COLOR")
            else:
                pen_color = (255, 255, 255)
                print("YOU SELECT WHITE COLOR")

        # thickness
        if k == 43:  # caracter + "Aumentar linha"
            pen_thickness += 1
            print("THICKNESS: " + str(pen_thickness))

        if k == 45:  # caracter - "Diminuir linha"
            pen_thickness -= 1
            if pen_thickness < 0:
                pen_thickness = 0
            print("THICKNESS: " + str(pen_thickness))

        # erase
        if k == ord("b"):
            if background_white:
                pen_color = (255, 255, 255)
                print("YOU SELECT ERASER")
            else:
                pen_color = (0, 0, 0)
                print("YOU SELECT ERASER")

        # flip the background
        if k == ord("f"):
            if background_white:
                background.fill(0)
                background_white = False
                pen_color = (255, 255, 255)
            else:
                background.fill(255)
                background_white = True
                pen_color = (0, 0, 0)

        # pointer mode ---- not working
        if k == ord("p"):
            if pointer_on:
                pointer_on = False
            else:
                pointer_on = True

        # save the draw in png file
        if k == ord("w"):
            cv2.imwrite('./drawing_' + str(ctime()) + '.png', background)
            print("DRAWING SAVED AS A .PNG FILE")

        # draw a rectangle with mouse events
        if k == ord("R"):
            cv2.namedWindow('Image_Window')
            rectangle = partial(shape, mode=str('rectangle'))
            cv2.setMouseCallback('Image_Window', rectangle)
            cv2.imshow('Image_Window', background)

        # draw a circle with mouse events
        if k == ord("C"):
            cv2.namedWindow('Image_Window')
            circle = partial(shape, mode=str('circle'))
            cv2.setMouseCallback('Image_Window', circle)
            cv2.imshow('Image_Window', background)

        # draw a rectangle----------------------------------------------------------------------
        if k == ord("s"):
            rect_drawing = True
            rect_pt1_x = int(dot_x)
            rect_pt1_y = int(dot_y)
            # print(rect_cnt)
            # print(rect_pt1_x, rect_pt1_y)

        if rect_drawing:
            if background_white:
                background.fill(255)
            else:
                background.fill(0)
            # background.fill(255)
            rect_pt2_x = int(dot_x)
            rect_pt2_y = int(dot_y)
            cv2.rectangle(background, (rect_pt1_x, rect_pt1_y), (rect_pt2_x, rect_pt2_y), pen_color, pen_thickness)
            # Nas ultimas cordenadas devo desenhar um retangulo da cor do fundo
            a = rect_pt2_x
            b = rect_pt2_y
            if a != rect_pt2_x | b != rect_pt2_y:
                cv2.rectangle(background, (rect_pt1_x, rect_pt1_y), (rect_pt2_x, rect_pt2_y), pen_color, pen_thickness)

        if k == ord("L") and rect_drawing:
            rect_pt2_x = int(dot_x)
            rect_pt2_y = int(dot_y)
            rect_drawing = False
            cv2.rectangle(background, (rect_pt1_x, rect_pt1_y), (rect_pt2_x, rect_pt2_y), pen_color, pen_thickness)

        # draw a circle------------------------------------------------------------------------
        if k == ord("e"):
            circle_drawing = True
            circle_pt1_x = int(dot_x)
            circle_pt1_y = int(dot_y)

        if circle_drawing:
            if background_white:
                background.fill(255)
            else:
                background.fill(0)
            # background.fill(255)
            circle_pt2_x = int(dot_x)
            circle_pt2_y = int(dot_y)
            # cv2.circle(image, center_coordinates, radius, color, thickness)
            # cv2.ellipse(background, (circle_pt1_x, circle_pt1_y),
            #             (circle_pt2_x, circle_pt2_y), 0, 0, 360, pen_color, cv2.FILLED)
            try:
                radius = math.pow(((math.pow(circle_pt1_x, 2) - math.pow(circle_pt2_x, 2)) + (
                        math.pow(circle_pt1_y, 2) - math.pow(circle_pt2_y, 2))), 1 / 2)
                cv2.circle(background, (circle_pt2_x, circle_pt2_y), int(radius), pen_color, pen_thickness)
                a = circle_pt1_x
                b = circle_pt1_y
                if a != circle_pt1_x | b != circle_pt1_y:
                    radius = math.pow(((math.pow(circle_pt1_x, 2) - math.pow(circle_pt2_x, 2)) + (
                            math.pow(circle_pt1_y, 2) - math.pow(circle_pt2_y, 2))), 1 / 2)
                    cv2.circle(background, (circle_pt2_x, circle_pt2_y), int(radius), pen_color, pen_thickness)
            except:
                pass

        if k == ord("L") and circle_drawing:
            circle_pt2_x = int(dot_x)
            circle_pt2_y = int(dot_y)
            circle_drawing = False
            # cv2.ellipse(background, (circle_pt1_x, circle_pt1_y),
            #             (circle_pt2_x, circle_pt2_y), 0, 0, 360, pen_color, cv2.FILLED)
            try:
                radius = math.pow(((math.pow(circle_pt1_x, 2) - math.pow(circle_pt2_x, 2)) + (
                        math.pow(circle_pt1_y, 2) - math.pow(circle_pt2_y, 2))), 1 / 2)
                cv2.circle(background, (circle_pt2_x, circle_pt2_y), int(radius), pen_color, pen_thickness)
                a = circle_pt1_x
                b = circle_pt1_y
                if a != circle_pt1_x | b != circle_pt1_y:
                    radius = math.pow(((math.pow(circle_pt1_x, 2) - math.pow(circle_pt2_x, 2)) + (
                            math.pow(circle_pt1_y, 2) - math.pow(circle_pt2_y, 2))), 1 / 2)
                    cv2.circle(background, (circle_pt2_x, circle_pt2_y), int(radius), pen_color, pen_thickness)
            except:
                pass

    """
    FINALIZATION -----------------------------------------
    """
    capture.release()  # free the webcam for other use
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
