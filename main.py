
import logging
import json
import time

import power_supply
import reboot_timer
import subprocess
import take_picture

LOGFILE="timelapse.log"
REBOOT_TIME=45
FOR_REAL=True

def log_power_data():
    try:
        if FOR_REAL:
            power_supply.turn_on_current_adc_measurement()
            time.sleep(1)
            power_data = power_supply.read_power_data()
        else:
            power_data = '["skipped"]'
        logging.info("Power data: "+json.dumps(power_data))
    except Exception as e:
        logging.error("[!] Failed to log power data")

def sync_data():
    logging.info(" ------------ Syncing files ...")

    logging.info(" ------------ Syncing files ... DONE")

def take_photo():
    logging.info(" ------------ Taking photo ...")
    logging.info(" ------------ Taking photo ... DONE")

def power_off():
    if FOR_REAL:
        print("poweroff_") 
	subprocess.call("poweroff")
    else:
        print("poweroff")

def setup_reboot_timer():
    if FOR_REAL:
        reboot_timer.set_reboot_time(REBOOT_TIME)

def is_stop_switch_active():
    if FOR_REAL:
        return reboot_timer.get_stop_switch_status()
    else:
        return False


def main():
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG, filename=LOGFILE, filemode="a")
    logging.info(" ------------ Started ------------ ")
    take_photo()
    log_power_data()
    sync_data()
    if not is_stop_switch_active():
        setup_reboot_timer()
        logging.info(" ------------ Finished ------------ ")
        logging.shutdown()
        power_off()
    else:
        logging.info("Stop switch is active! Quitting without reboot")
        sync_data()

if __name__ == "__main__":
    main()
