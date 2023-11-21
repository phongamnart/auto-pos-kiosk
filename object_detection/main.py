import cv2
import numpy as np
import threading
from dobot_api import DobotApiDashboard, DobotApi, DobotApiMove, MyType
from time import sleep
import time

# โค้ดส่วนของกล้อง
def camera_thread():
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

                        arm_control.set_target_position(x_robot, y_robot, z_robot)

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

                        arm_control.set_move_position(distance_x, distance_y)

                        print("point dx", distance_x)
                        print("point dy", distance_y)



        cv2.imshow('Frame with Points', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# โค้ดส่วนของแขนกล
class ArmControl:
    def __init__(self):
        self.currnt_position = None
        self.dashboard, self.move, self.feed = self.connect_robot()
        print("Start power up.")
        self.dashboard.PowerOn()
        print("Please wait patiently,Robots are working hard to start.")
        count = 3
        while count > 0:
            print(count)
            count = count - 1
            sleep(1)

        print("Clear error.")
        self.dashboard.ClearError()

        print("Start enable.")
        self.dashboard.EnableRobot()
        print("Complete enable.")

        self.current_target = None

    def connect_robot(self):
        try:
            ip = "192.168.1.6"
            dashboard_p = 29999
            move_p = 30003
            feed_p = 30004
            print("Connecting...")
            dashboard = DobotApiDashboard(ip, dashboard_p)
            move = DobotApiMove(ip, move_p)
            feed = DobotApi(ip, feed_p)
            print("Connection succeeded.")
            return dashboard, move, feed
        except Exception as e:
            print("Connection failed.")
            raise e

    def set_target_position(self, x, y, z):
        self.current_target = (x, y, z)

    def set_move_position(self, distance_x, distance_y):
        self.currnt_position = (distance_x, distance_y)

    def move_to_target(self):
        if self.current_target is not None:
            x, y, z = self.current_target
            self.move.MovL(x, y, z, -177, 0, -178)
            sleep(3)

    def grip_close(self):
        self.dashboard.ToolDO(1, 1)
        self.dashboard.ToolDO(2, 1)
        sleep(3)

    def grip_open(self):
        self.dashboard.ToolDO(1, 0)
        self.dashboard.ToolDO(2, 0)
        sleep(3)

    def drop(self):
        self.move.MovL(-219, -536, 387, -177, 0, -178)

    def home(self):
        self.move.MovL(-145, -290, 540, -177, 0, 178)

    def move_position(self):
        if self.currnt_position is not None:
            distance_x, distance_y = self.currnt_position

        if distance_x != 0:
            self.move.MovL(-145, -290, 540, -177, 0, 178)

        if distance_y != 0:
            self.move.MovL(-145, -290, 540, -177, 0, 90)



if _name_ == '_main_':
    arm_control = ArmControl()

    camera_thread = threading.Thread(target=camera_thread)
    camera_thread.setDaemon(True)
    camera_thread.start()

    while True:
        if arm_control.current_target is not None:

            arm_control.move_to_target()
            arm_control.move_position()
            arm_control.grip_close()
            arm_control.home()
            arm_control.drop()
            arm_control.grip_open()
            arm_control.home()

        sleep(5)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

arm_control.dashboard.DisableRobot()
arm_control.dashboard.ClearError()
camera_thread().cap.release()
cv2.destroyAllWindows()