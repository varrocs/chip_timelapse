
import logging
import json
import time

import power_supply
import reboot_timer
import subprocess
import dweet_client
import take_picture

import traceback

LOGFILE="/home/chip/timelapse.log"
REBOOT_TIME=300
FOR_REAL=True

def log_data(switch_status, attiny_present):
    try:
        log_data = {}
        try:
            power_supply.turn_on_current_adc_measurement()
            time.sleep(1)
            log_data['powerData'] = power_supply.read_power_data()
            log_data['powerdataStatus'] = True
        except Exception as e:
            logging.error("Failed to get power data: "+str(e))
            log_data['powerData'] = {}
            log_data['powerdataStatus'] = False

        try:
            log_data['imagesSizeMB'] = take_picture.images_size() / (1024*1024)
            log_data['freeDiskSpaceMB'] = take_picture.free_space() / (1024*1024)
            log_data['diskSpaceStatus'] = True
        except Exception as e:
            logging.error("Failed to get file system status: "+str(e))
            log_data['imagesSizeMB'] = 0
            log_data['freeDiskSpaceMB'] = 0
            log_data['diskSpaceStatus'] = False

        log_data['switchStatus'] = switch_status
        log_data['rebootTime'] = REBOOT_TIME
        log_data['attinyPresent'] = attiny_present

        dweet_client.send_status_message(log_data)
        logging.info("Status data: "+json.dumps(log_data))
    except Exception as e:
        logging.error("[!] Failed to log status data" + str(e))

def sync_data():
    logging.info(" ------------ Syncing files ...")
    logging.info("SKIP")
    logging.info(" ------------ Syncing files ... DONE")

def take_photo():
    logging.info(" ------------ Taking photo ...")
    take_picture.take_picture()
    logging.info(" ------------ Taking photo ... DONE")

def power_off():
    if FOR_REAL:
        print("poweroff_")
        subprocess.call("poweroff")
    else:
        print("fake poweroff")

def setup_reboot_timer():
    if FOR_REAL:
        reboot_timer.set_reboot_time(REBOOT_TIME)

def is_stop_switch_active():
        try:
            return reboot_timer.get_stop_switch_status(), True
        except Exception as e:
            return False, False

def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename=LOGFILE, filemode="a")
    logging.info(" ------------ Started ------------ ")
    take_photo()
    switch_active, attiny_present = is_stop_switch_active()

    log_data(switch_active, attiny_present)
    sync_data()
    if not switch_active and attiny_present:
        setup_reboot_timer()
        logging.info(" ------------ Finished ------------ ")
        logging.shutdown()
        power_off()
    else:
        logging.info("Stop switch is active or attiny is missing! Quitting without poweroff")
        sync_data()

if __name__ == "__main__":
    main()
