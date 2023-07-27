import cv2

from typing import Tuple


class CvService:

    def __init__(self):
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2(history=100, detectShadows=True)

    def get_mask(self, frame, x_coords: Tuple[int, int] = None, y_coords: Tuple[int, int] = None):
        fg_mask = self.background_subtractor.apply(frame)

        if x_coords and y_coords:
            start_y, end_y = y_coords
            start_x, end_x = x_coords
            return fg_mask[start_y:end_y, start_x:end_x]
        else:
            return fg_mask

    def get_figure_coordinates(self, fg_mask):
        # Find contours in the foreground mask
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        figure_coordinates = []
        for contour in contours:
            # Approximate the contour to reduce the number of points in the curve
            epsilon = 0.02 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            # Extract the coordinates of the figure's boundary
            coordinates = approx.reshape(-1, 2).tolist()
            figure_coordinates.append(coordinates)

        return figure_coordinates

    def get_contour_center(self, contour):
        # Compute the moments of the contour
        moments = cv2.moments(contour)

        # Calculate the centroid (center) of the contour
        center_x = int(moments['m10'] / moments['m00'])
        center_y = int(moments['m01'] / moments['m00'])

        return center_x, center_y

    def show_image(self, screen_name, image, circle_coords: Tuple[int, int] = None,
                   circle_color: Tuple[int, int, int] = (0, 0, 255),
                   arrow_start: Tuple[int, int] = None, arrow_end: Tuple[int, int] = None):
        if circle_coords:
            cv2.circle(image, circle_coords, 5, circle_color, 2)
        cv2.imshow(screen_name, image)
