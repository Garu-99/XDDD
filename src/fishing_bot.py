import cv2
import numpy as np
import asyncio

from argparse import ArgumentParser
from datetime import datetime
from time import sleep

from service.cv_service import CvService
from service.input_service import InputService
from service.windows_service import WindowsService
from service.algebra_service import AlgebraService, Vector2

cv_service = CvService()
input_service = InputService()
windows_service = WindowsService()
algebra_service = AlgebraService()


def reset_fishing(window):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] Fishing finished, restarting..")
    input_service.fish(window)


def fish(window_name: str, show_window: bool = False,
         show_circle: bool = False, do_click: bool = False, click_frequency: float = 10):

    window = windows_service.get_window_gw(window_name)
    exception_count = 0
    frame_number = 0

    # Pixels to add to the current direction of the fish
    prediction_scalar = 20
    last_pos: Vector2 = (0, 0)

    # Fishing minigame dimensions
    start_x, end_x = 640, 740
    start_y, end_y = 390, 460

    # Frame to show beyond the cropped image
    toleranceX = 100
    toleranceY = 100

    reset_fishing(window)

    # 60 fps
    frame_delay = 1/60

    while True:
        # We didn't find any fishes moving, we assume we stopped fishing, so we start again
        if exception_count > 120:
            reset_fishing(window)
            exception_count = 0

        sleep(frame_delay)
        frame = windows_service.capture_screen(window_name)

        if frame is None:
            continue

        cropped_mask_image = cv_service.get_mask(frame, (start_x, end_x), (start_y, end_y))
        cropped_image = frame[start_y-toleranceY:end_y+toleranceY, start_x-toleranceX:end_x+toleranceX]

        coords = cv_service.get_figure_coordinates(cropped_mask_image)
        center = (0, 0)

        frame_number = frame_number + 1 if frame_number < 1000000 else 0

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        if len(coords) <= 0:
            continue

        try:
            coords = np.array(coords)
            center = cv_service.get_contour_center(coords)

            coords_to_click = center
            if last_pos[0] != 0:
                direction = AlgebraService.get_direction(last_pos, center)
                # Predict movement based on current direction
                coords_to_click = AlgebraService.add(coords_to_click,
                                                     AlgebraService.mult(direction, prediction_scalar))
            last_pos = center
            coords_to_click = AlgebraService\
                .to_int_vector(AlgebraService.add(coords_to_click, (start_x, start_y)))

            is_click_frame = center and center[0] != 0 and coords_to_click \
                and do_click and frame_number % click_frequency == 0

            if is_click_frame:
                input_service.click_on_coordinate_in_window(window, coords_to_click[0], coords_to_click[1])
        except Exception as e:
            exception_count += 1

        if show_window:
            abs_center = (center[0] + toleranceX, center[1] + toleranceY)
            circle_coords = abs_center if center[0] != 0 and show_circle else None

            cv_service.show_image("Screen Capture", cropped_image, circle_coords)
            # cv_service.show_image("Mask", cropped_mask_image, circle_coords)


parser = ArgumentParser()
parser.add_argument("-wn", "--window-name", dest="window_name", help="Name of the window to capture", type=str,
                    required=True)
parser.add_argument("-cf", "--click-frequency", dest="click_frequency", help="Every how many frames to click", type=int,
                    default=10)
parser.add_argument("-sw", "--show-window", dest="show_window", help="Shows captured frames", action="store_true",
                    default=False)
parser.add_argument("-c", "--click", dest="do_click", help="Whether to click on the fish or not", action="store_true",
                    default=False)
parser.add_argument("-sc", "--show-circle", dest="show_circle",
                    help="Shows red circle on the captured frames where the bot is clicking", action="store_true",
                    default=False)

args = parser.parse_args()

fish(args.window_name, args.show_window, args.show_circle, args.do_click, args.click_frequency)
