
import datetime
import os
import subprocess

IMAGE_FOLDER = "/home/chip/images/"
FILENAME_FORMAT = "camera_image_{time}.jpg"
CAMERA_UTILITY = "fswebcam"
RESOLUTION="1280x720"
DEVICE="/dev/video0"

def _create_filename():
    time_part = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    return IMAGE_FOLDER + FILENAME_FORMAT.format(time=time_part)

def _check_folder():
    if not os.path.isdir(IMAGE_FOLDER):
        os.mkdir(IMAGE_FOLDER)

def _do_take_picture(filename):
    command = [CAMERA_UTILITY, "-r", RESOLUTION, "--no-banner", "--jpeg", "-1", "--device", DEVICE, filename]
    subprocess.call(command)

def take_picture():
    _check_folder()
    filename=_create_filename()
    _do_take_picture(filename)
    return filename

if __name__ == "__main__":
    fn = take_picture()
    print (fn)
