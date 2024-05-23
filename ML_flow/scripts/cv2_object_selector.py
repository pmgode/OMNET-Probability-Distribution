import cv2
import os
import time
from loguru import logger


class Cv2ObjectGUI:
    """
    Class to create and interface with an OpenCv2 GUI to select and
    extract sections.
    """
    def __init__(self, window_name, cap, output_dir, output_prefix):
        # Initialize variables
        self.window_name = window_name
        self.output_dir = output_dir
        self.output_prefix = output_prefix
        self.cap = cap
        self.marked_areas = []
        self.write_periodically = False
        cv2.namedWindow(self.window_name)

    def play(self):
        start_time = time.time()
        passed_time = 0
        write_counter = 0
        while self.cap.isOpened() and self.handle_input(cv2.waitKey(1)):
            ret, self.frame = self.cap.read()
            if not ret:
                logger.error(f"Could not read frame in window '{self.window_name}'")
                self.quit()
                break
            if self.write_periodically:
                past_time = start_time - time.time()
                if past_time > 600:
                    write_areas(self.frame, "_" +str(write_counter))
                    past_time = 0
                    write_counter += 1
            self.__animate_all_areas()
            cv2.imshow(self.window_name, self.frame)
    def __animate_all_areas(self):
        # Draw all marked areas into frame
        for area in self.marked_areas:
            thickness = 2
            area.animate_in(frame=self.frame, thickness=thickness)

    def quit(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def set_to_second(self, time):
        seconds = time * 1000
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, seconds)

    def write_areas(self, frame, output_postfix):
        for area in self.marked_areas:
            (start, end) = area.get_coordinates()
            subimage = self.frame[start[1]+5:end[1]-5, start[0]+5 : end[0]-5]
            path = (
                f"{os.path.join(self.output_dir, self.output_prefix)}_{area.name}{output_postfix}.png"
            )
            cv2.imwrite(path, subimage)

    def handle_input(self, key):
        """
        Entry point for input handeling.
        Returns FALSE if input instructs to quit the GUI.
        """
        # QUIT
        if key == ord("q"):
            self.quit()
            return False
        # NEW AREA
        elif key == ord("a"):  # Draw new area
            name = "area_" + str(len(self.marked_areas))
            color = (255, 0, 0)  # blue
            area = Cv2ObjectGuiMarkedAreaHandler(name, color)
            cv2.setMouseCallback(self.window_name, area.make)
            self.marked_areas.append(area)
        # WRITE
        elif key == ord("w"):
            self.write_areas(self.frame, "")
        # WRITE PERIODICALLY
        elif key == ord("p"):
            self.write_periodically = True
        # UNDO
        elif key == ord("u"):  # Undo
            self.marked_areas.pop()

        return True


class Cv2ObjectGuiMarkedAreaHandler:
    """
    Class to help with the creation and handeling of marked areas.
    """

    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.start_point = None
        self.end_point = None
        self.drawing = False

    def make(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drawing = True
            self.start_point = (x, y)
        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            self.end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            self.drawing = False
            self.end_point = (x, y)

    def animate_in(self, frame, thickness):
        # Do
        if not (self.start_point and self.end_point):
            return
        # Draw area
        thickness = 5
        cv2.rectangle(
            frame,
            self.start_point,
            self.end_point,
            self.color,
            thickness,
        )
        # Add label
        font = cv2.FONT_HERSHEY_DUPLEX
        font_size = 1.2
        cv2.putText(frame, self.name, self.end_point, font, font_size, self.color)

    def get_coordinates(self):
        return (self.start_point, self.end_point)
