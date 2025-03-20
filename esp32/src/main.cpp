#ifndef ARDUINO_USB_MODE
#error This ESP32 SoC has no Native USB interface
#elif ARDUINO_USB_MODE == 1
#warning This sketch should be used when USB is in OTG mode
void setup() {}
void loop() {}
#else

#include <Arduino.h>
#include <ArduinoJson.h>
#include <USB.h>
#include <USBHID.h>
#include <USBHIDMouse.h>
#include <USBHIDKeyboard.h>
#include <USBHIDSystemControl.h>

USBHID HID;
USBHIDAbsoluteMouse Mouse;
USBHIDKeyboard Keyboard;

HardwareSerial &host_serial = Serial;
// HardwareSerial &mobo_serial = Serial1;

JsonDocument mkb_input;
// JsonDocument post_codes;
JsonDocument power_status;

// put function declarations here:
int myFunction(int, int);

const int8_t pwr_button = 46;
const int8_t cmos_button = 3;
// const int8_t pwr_detect = 8;

void setup()
{
    host_serial.begin(115200);
    // mobo_serial.begin(115200, SERIAL_8N1, 18);
    HID.begin();
    Mouse.begin();
    Keyboard.begin();
    USB.begin();
    pinMode(pwr_button, OUTPUT);
    pinMode(cmos_button, OUTPUT);
    // pinMode(pwr_detect, INPUT);
}

void loop()
{
    static volatile int64_t cur_loop_timestamp = esp_timer_get_time();
    cur_loop_timestamp = esp_timer_get_time();
    // Immediately check power status!
    static volatile int64_t check_power_status_timestamp = -200000;

    if (cur_loop_timestamp - check_power_status_timestamp >= 100000)
    {
        /* if (analogRead(pwr_detect) > 1000)
        {
            power_status["pwr"] = true;
        }

        else
        {
            power_status["pwr"] = false;
        } */

        if (HID.ready())
        {
            power_status["usb"] = true;
        }

        else
        {
            power_status["usb"] = false;
        }

        serializeJson(power_status, host_serial);
        host_serial.write('\n');
        check_power_status_timestamp = esp_timer_get_time();
    }

    /* while (mobo_serial.available())
    {
        post_codes["post_code"] = mobo_serial.read();
        serializeJson(post_codes, host_serial);
        host_serial.write('\n');
    } */

    if (host_serial.available())
    {
        DeserializationError error = deserializeJson(mkb_input, host_serial);

        if (error)
        {
            host_serial.print("deserializeJson() failed: ");
            host_serial.println(error.c_str());
            return;
        }

        else
        {
            if (mkb_input["key_down"].is<JsonVariant>())
            {
                Keyboard.pressRaw(mkb_input["key_down"].as<uint8_t>());
            }

            else if (mkb_input["key_up"].is<JsonVariant>())
            {
                Keyboard.releaseRaw(mkb_input["key_up"].as<uint8_t>());
            }

            else if (mkb_input["mouse_coord"].is<JsonVariant>())
            {
                Mouse.move(mkb_input["mouse_coord"]["x"].as<int16_t>(), mkb_input["mouse_coord"]["y"].as<int16_t>());
            }

            else if (mkb_input["mouse_down"].is<JsonVariant>())
            {
                Mouse.press(mkb_input["mouse_down"].as<uint8_t>());
            }

            else if (mkb_input["mouse_up"].is<JsonVariant>())
            {
                Mouse.release(mkb_input["mouse_up"].as<uint8_t>());
            }

            else if (mkb_input["pwr"].is<JsonVariant>())
            {
                digitalWrite(pwr_button, mkb_input["pwr"].as<uint8_t>());
            }

            else if (mkb_input["cmos"].is<JsonVariant>())
            {
                digitalWrite(cmos_button, mkb_input["cmos"].as<uint8_t>());
            }
        }
    }
}

// put function definitions here:
int myFunction(int x, int y)
{
    return x + y;
}

#endif /* ARDUINO_USB_MODE */