# C.H.I.P timelapse camera project

This project trying to create a timelapse camera device with the NewThingCo's
C.H.I.P board, an atmel attiny as a rebooting device and an USB webcam.

The CHIP board has a power management chip for powering down and the attiny acts
as a delayed power on switch. The board and the attiny communicates over I2C.

The C.H.I.P board boots up, takes a picture, tells the attiny the reboot time
over I2C then powers off. After the reboot time has expired the attiny reboots
the board and so on.
