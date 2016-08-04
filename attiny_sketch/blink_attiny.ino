
/*
 * 
*/
#include <Event.h>
#include <Timer.h>

#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>

#ifndef TWI_RX_BUFFER_SIZE
#define TWI_RX_BUFFER_SIZE ( 16 )
#endif

#include <TinyWireS.h>

const uint8_t TWI_ADDR=5;

const int PIN=3;
const int STOP_SWITCH_PIN=4;

const int TIMER_STEP = 8;

#define ON_BUTTON_RELEASED HIGH
#define ON_BUTTON_PRESSED LOW

typedef enum I2C_REG_ADDRESSES {
    REBOOT_SECONDS_LOW  = 0x00,
    REBOOT_SECONDS_HIGH = 0x01,
    REBOOT_ACTIVE       = 0x02,
    STOP_SWITCH         = 0x03,

    I2C_REG_ADDRESSES_COUNT
};

uint8_t statusRegisters[I2C_REG_ADDRESSES_COUNT] = {0, 0, 0, 0};

volatile byte reg_position;
const byte reg_size = sizeof(statusRegisters);
bool registers_updated = false;

bool timer_active = false;

// SLEEP ----------------------------------------

bool on = true;

EMPTY_INTERRUPT(WDT_vect)

void do_sleep() {
    power_all_disable();
    wdt_reset();
    sleep_mode(); // Put to sleep
    power_all_enable();
    power_adc_disable();
}

bool sleep_with_register_counter() {
  if (statusRegisters[REBOOT_ACTIVE] == 0) return false; // Nothing to do
  
  uint16_t sleepTime = sleepTimeFromRegs();
  if (sleepTime == 0) {
    statusRegisters[REBOOT_ACTIVE] = 0;
  } else {

    do_sleep();
    
    if (sleepTime <= TIMER_STEP) { // Update the time left
      sleepTime = 0;
    } else {
      sleepTime -= TIMER_STEP;
    }

    sleepTimeToRegs(sleepTime);
  }

  return (statusRegisters[REBOOT_ACTIVE] == 0);
}

// END SLEEP ----------------------------------------

// I2C ----------------------------------------

void requestEvent()
{
    TinyWireS.send(statusRegisters[reg_position]);
    // Increment the reg position on each read, and loop back to zero
    reg_position++;
    if (reg_position >= reg_size)
    {
        reg_position = 0;
    }
}

void receiveEvent(uint8_t howMany)
{
   if (howMany < 1)
    {
        // Sanity-check
        return;
    }
    if (howMany > TWI_RX_BUFFER_SIZE)
    {
        // Also insane number
        return;
    }

    reg_position = TinyWireS.receive();
    howMany--;
    if (!howMany)
    {
        // This write was only to set the buffer for next read
        return;
    }

     while(howMany--)
    {
        statusRegisters[reg_position] = TinyWireS.receive();
        registers_updated = true;
        reg_position++;
        if (reg_position >= reg_size)
        {
            reg_position = 0;
        }
    }
}

// END I2C ----------------------------------------

void pull_on_switch() {
  const int DELAY = 100;
  const int POWER_ON_TIME=3000; // The power button is pressed for 3 secs
  
  cli();
  digitalWrite(PIN, ON_BUTTON_PRESSED);
  
  for (int i = 0; i< POWER_ON_TIME / DELAY; ++i) {
    //wdt_reset();
    _delay_ms(100);
  }
  digitalWrite(PIN, ON_BUTTON_RELEASED);
  sei();
}

bool update_stop_switch_status() {
  statusRegisters[STOP_SWITCH] = (digitalRead(STOP_SWITCH_PIN) == HIGH) ? 0 : 1;  // Not pressed = Pulled up
  return statusRegisters[STOP_SWITCH] == 1  ;
}

uint16_t sleepTimeFromRegs() {
  return (statusRegisters[REBOOT_SECONDS_HIGH] << 8 | statusRegisters[REBOOT_SECONDS_LOW]); 
}

void sleepTimeToRegs(uint16_t sleepTime) {
  statusRegisters[REBOOT_SECONDS_LOW] = (sleepTime & 0xFF);
  statusRegisters[REBOOT_SECONDS_HIGH] = (sleepTime >> 8) & 0xFF;
}

// SETUP

void setup_watchdog() {
    cli();
    wdt_reset();                  // reset watchdog timer
    MCUSR &= ~(1<<WDRF);          // clear reset flag
    WDTCR = (1<<WDE) | (1<<WDCE); // enable watchdog
    WDTCR = (1<<WDIE) | _BV(WDP3) | _BV(WDP0);  // watchdog interrupt instead of reset; _BV(WDP3) | _BV(WDP0) = 8s
    //+reset, timeout can be 15,30,60,120,250,500ms or 1,2,4,8s
    sei();
}

void setup() {

  setup_watchdog();

  // Setup pins
  // TODO: minimize power consumption on other pins
  pinMode(STOP_SWITCH_PIN, INPUT_PULLUP);
  
  pinMode(PIN, OUTPUT);
  digitalWrite(PIN, ON_BUTTON_RELEASED);

  // Setup I2C
  TinyWireS.begin(TWI_ADDR);
  TinyWireS.onReceive(receiveEvent);
  TinyWireS.onRequest(requestEvent);

  // To reduce power
  power_adc_disable();

  // Setup sleep related stuff
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);
}

// LOOP
void loop() {
  TinyWireS_stop_check();
  wdt_reset();
  update_stop_switch_status();

  if (statusRegisters[STOP_SWITCH] > 0) { // The stop switch is pressed 
    bool parentDeviceSleeping = (statusRegisters[REBOOT_ACTIVE] == 1);
    statusRegisters[REBOOT_ACTIVE] = 0;   // No more reboot
    timer_active = false;
    if (parentDeviceSleeping) {
      pull_on_switch();  
    }
  }
  else // Switch is not pressed
  {
    bool timer_active_current = sleep_with_register_counter();
    if (timer_active && !timer_active_current) { // The timer was active but currently not
      pull_on_switch();
    }
    timer_active = timer_active_current;
  }
}
