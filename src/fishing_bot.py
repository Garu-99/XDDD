import cv2
import numpy as np


from argparse import ArgumentParser
from datetime import datetime
from time import sleep

from service.cv_service import CvService
from service.input_service import InputService
from service.windows_service import WindowsService

cv_service = CvService()
input_service = InputService()
windows_service = WindowsService()


def reset_fishing(window):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] Fishing finished, restarting..")
    input_service.fish(window)


def fish(window_name: str, show_window: bool = False,
         show_circle: bool = False, click_delay: float = 0.1, do_click: bool = False):
    show_window = show_window or False
    show_circle = show_circle or False
    click_delay = click_delay or 0.1
    do_click = do_click or False

    window = windows_service.get_window_gw(window_name)
    exception_count = 0

    reset_fishing(window)

    while True:
        if exception_count > 40:
            reset_fishing(window)
            exception_count = 0
        sleep(click_delay)
        frame = windows_service.capture_screen(window_name)

        if frame is not None:
            start_x, end_x = 640, 740
            start_y, end_y = 390, 465
            cropped_mask_image = cv_service.get_mask(frame, (start_x, end_x), (start_y, end_y))

            toleranceX = 100
            toleranceY = 100
            # Get the specific part of the image
            cropped_image = frame[start_y-toleranceY:end_y+toleranceY, start_x-toleranceX:end_x+toleranceX]

            coords = cv_service.get_figure_coordinates(cropped_mask_image)
            center = (0, 0)
            if len(coords) > 0:
                try:
                    coords = np.array(coords)
                    center = cv_service.get_contour_center(coords)
                    absolute_center = (center[0] + start_x, center[1] + start_y)

                    if center and absolute_center and do_click:
                        input_service.click_on_coordinate_in_window(window, absolute_center[0], absolute_center[1])
                except Exception as e:
                    exception_count += 1

            if show_circle and center[0] != 0:
                center2 = (center[0] + toleranceX, center[1] + toleranceY)
                cv2.circle(cropped_image, center2, 5, (0, 0, 255), 2)
            if show_window:
                cv2.imshow("Screen Capture", cropped_image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


parser = ArgumentParser()
parser.add_argument("-wn", "--window-name", dest="window_name", help="Name of the window to capture", type=str, required=True)
parser.add_argument("-sw", "--show-window", dest="show_window", help="Shows captured frames", action="store_true")
parser.add_argument("-cd", "--click-delay", dest="click_delay", help="Delay between each click", type=float)
parser.add_argument("-sc", "--show-circle", dest="show_circle",
                    help="Shows red circle on the captured frames where the bot is clicking", action="store_true")

args = parser.parse_args()

fish(args.window_name, args.show_window, args.show_circle, args.click_delay)
