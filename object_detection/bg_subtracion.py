import cv2
import numpy as np
import time

cap = cv2.VideoCapture(2)
cap.set(3, 1280)
cap.set(4, 720)

background = cv2.imread('bg_Color.png')

background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)

threshold = 60

ret, first_frame = cap.read()
first_frame_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
last_first_frame_update_time = time.time()

while True:
    ret, frame = cap.read()

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    background_gray_resized = cv2.resize(background_gray, (frame_gray.shape[1], frame_gray.shape[0]))

    if (time.time() - last_first_frame_update_time) >= 5:
        ret, first_frame = cap.read()
        first_frame_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
        last_first_frame_update_time = time.time()

    difference = cv2.absdiff(first_frame_gray, background_gray_resized)
    _, thresholded = cv2.threshold(difference, threshold, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresholded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 30 and h > 30:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

                depth_frame = cap.retrieve()[1]
                if depth_frame is not None:
                    # CAMERA
                    depth_value = depth_frame[cy, cx]
                    z = depth_value[0]

                    text = f'(x {cx}, y {cy}, z {z})'
                    cv2.putText(frame, text, (x - 40, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # ROBOT
                    y_robot = cx - 1190
                    x_robot = cy - 235
                    z_robot = (z * (-1.6)) + 600
                    robot = f'x {x_robot}, y {y_robot}, z {z_robot}'
                    cv2.putText(frame, robot, (x - 40, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)


                    vertical_line = ((cx, y), (cx, y + h))
                    horizontal_line = ((x, cy), (x + w, cy))

                    vertical_line_length = np.sqrt((vertical_line[1][0] - vertical_line[0][0]) ** 2 +
                                                (vertical_line[1][1] - vertical_line[0][1]) ** 2)
                    horizontal_line_length = np.sqrt((horizontal_line[1][0] - horizontal_line[0][0]) ** 2 +
                                                (horizontal_line[1][1] - horizontal_line[0][1]) ** 2)

                    if vertical_line_length < horizontal_line_length:
                        shortest_line = vertical_line
                    else:
                        shortest_line = horizontal_line

                    cv2.line(frame, shortest_line[0], shortest_line[1], (0, 255, 255), 2)


                    start_point, end_point = shortest_line[0] , shortest_line[1]

                    distance_x = end_point[0] - start_point[0]
                    distance_y = end_point[1] - start_point[1]

                    print("point dx", distance_x)
                    print("point dy", distance_y)



        cv2.imshow('Frame with Points', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()