
import datetime
import os
import subprocess

IMAGE_FOLDER = "images/"
FILENAME_FORMAT = "camera_image_{time}.png"
CAMERA_UTILITY = "fswebcam"
RESOLUTION="640x480"

def _create_filename():
    time_part = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return IMAGE_FOLDER + FILENAME_FORMAT.format(time=time_part)


def _check_folder():
    if not os.path.isdir(IMAGE_FOLDER):
        os.mkdir(IMAGE_FOLDER)

def _do_take_picture(filename):
    command = [CAMERA_UTILITY, "-r", RESOLUTION, "--no-banner", filename]
    #subprocess.call(command)
    print " ".join(command)

def take_picture():
    _check_folder()
    _do_take_picture(_create_filename())

if __name__ == "__main__":
    take_picture()