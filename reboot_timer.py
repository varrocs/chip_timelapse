
import subprocess
import logging

BASE_COMMAND="i2cset -y -f 1 0x05 {reg} {value}" # Bus: 1, device address: 0x05

REBOOT_SECONDS_LOW  = 0x00
REBOOT_SECONDS_HIGH = 0x01
REBOOT_ACTIVE       = 0x02

def _assemble_command_lines(high, low, active):
    return (
        BASE_COMMAND.format(reg=REBOOT_SECONDS_LOW, value=low),
        BASE_COMMAND.format(reg=REBOOT_SECONDS_HIGH, value=high),
        BASE_COMMAND.format(reg=REBOOT_ACTIVE, value=1 if active else 0),
    )

def _execute_command_lines(commands):
    try:
        for command in commands:
            subprocess.call(command, shell=True)
    except Exception as e:
        logging.warn("Error during calling " + commands + ": "+str(e))


def _calculate_byte_values(secs):
    secs = min(secs, 0xFFFF)
    high = (secs >> 8) & 0xFF
    low = secs & 0xFF
    return high, low

def set_reboot_time(secs):
    high, low = _calculate_byte_values(secs)
    _execute_command_lines(
        _assemble_command_lines(high, low, True)
    )

if __name__ == "__main__":
    set_reboot_time(3600*8)