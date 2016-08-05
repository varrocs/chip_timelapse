
import subprocess


PREG_NAME = 0
PREG_UNIT = 1
PREG_BASE_REG = 2
PREG_BASE = 3
PREG_STEP = 4


power_chip_registers = [
#name, unit, base register, base, step
["ACIN_Voltage", "mV", 0x56, 0, 1.7],
["ACIN_Current", "mA", 0x58, 0, 0.625],
["VBUS_voltage", "mV", 0x5A, 0, 1.7],
["VBUS_Current", "mA", 0x5C, 0, 0.375],
["Internal_Temperature", "C", 0x5E, -144.7, 0.1],
["Temperature_Sensor_Voltage", "mV", 0x62, 0, 0.8],
["APS_IPSOUT_Voltage", "mV",0x7E, 0, 1.4],
["Battery_Voltage", "mV", 0x78, 0, 1.1],
["Battery_Discharge_Current", "mA", 0x7A, 0, 0.5],
["Battery_Charge_Current", "mA", 0x7C, 0, 0.5],
];

#Turn on battery current ADC: i2cset -y -f 0 0x34 0x82 0xc3
#Turn on all ADC: i2cset -y -f 0 0x34 0x82 0xff

BASE_COMMAND="/usr/sbin/i2cget -y -f 0 0x34 "  # Bus: 0, device address: 0x34

def _assemble_command_lines(d):
    return (
        BASE_COMMAND + str(d[PREG_BASE_REG]+0),
        BASE_COMMAND + str(d[PREG_BASE_REG]+1)
    )

def _run_commands(commands):
    result = []

    for command in commands:
        try:
            result.append(
                int(subprocess.check_output(command, shell=True), 16)
            )
        except Exception as e:
            print "Error during calling ", command, ": ", str(e)
            result.append(0)
    return result

def _parse_result(result, power_chip_register):
    value = result[0] << 4 | result[1]
    normalized_value =  power_chip_register[PREG_BASE] + value*power_chip_register[PREG_STEP]
    result = {
        "name": power_chip_register[PREG_NAME],
        "value": normalized_value,
        "unit": power_chip_register[PREG_UNIT]
    }

    return result

def _run_command_for(power_chip_register):
    return _parse_result(
        _run_commands(
            _assemble_command_lines(power_chip_register)),
        power_chip_register)

def turn_on_current_adc_measurement():
    subprocess.call("/usr/sbin/i2cset -y -f 0 0x34 0x82 0xc3", shell=True)

def read_power_data():
    return [_run_command_for(power_chip_register) for power_chip_register in power_chip_registers]


if __name__ == "__main__":
    import json
    ret = read_power_data()
    print json.dumps(ret)
