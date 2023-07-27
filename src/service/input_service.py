from pydirectinput import click, press
from time import sleep


class InputService:

    BAIT_KEY = "f2"
    FISH_KEY = "space"

    def fish(self, window):
        window.activate()
        sleep(0.01)
        press(InputService.BAIT_KEY)
        sleep(0.5)
        press(InputService.FISH_KEY)

    def click_on_coordinate_in_window(self, window, x, y):
        try:
            if not window.isActive:
                window.activate()  # Set the window as active (bring to foreground)
                sleep(0.01)  # Wait for the window to become active

            # Get the position of the window (in case it was moved)
            window_x, window_y = window.left, window.top

            # Calculate the absolute position of the click
            absolute_x, absolute_y = window_x + x, window_y + y

            # Perform the click action on the specified coordinates
            click(absolute_x, absolute_y)
        except Exception as e:
            print(f"An error occurred: {e}")
