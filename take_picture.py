
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


def images_size():
    total_size = 0
    root_path=IMAGE_FOLDER
    for dirpath, _, filenames in os.walk(root_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


    return 0

def free_space():
    st = os.statvfs(IMAGE_FOLDER)
    free = st.f_bavail * st.f_frsize
    return free

if __name__ == "__main__":
    fn = images_size() / (1024*1024)
    print (fn)
