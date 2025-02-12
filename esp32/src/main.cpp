#ifndef ARDUINO_USB_MODE
#error This ESP32 SoC has no Native USB interface
#elif ARDUINO_USB_MODE == 1
#warning This sketch should be used when USB is in OTG mode
void setup() {}
void loop() {}
#else

#include <Arduino.h>
#include <USB.h>
#include <USBHIDMouse.h>
#include <USBHIDKeyboard.h>
USBHIDMouse Mouse;
USBHIDKeyboard Keyboard;

// put function declarations here:
int myFunction(int, int);

void setup() {
  // put your setup code here, to run once:
  int result = myFunction(2, 3);
  Serial.begin(115200);
  Mouse.begin();
  Keyboard.begin();
  USB.begin();
}

void loop() {
  //Keyboard.write(0x4C);
  //Keyboard.pressRaw(HID_KEY_DELETE);
  //Keyboard.releaseRaw(HID_KEY_DELETE);
  // put your main code here, to run repeatedly:
  /*if (Serial.available() > 0) {
    char inChar = Serial.read();

    
  }*/
 sleep(1000);
}

// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}

#endif /* ARDUINO_USB_MODE */