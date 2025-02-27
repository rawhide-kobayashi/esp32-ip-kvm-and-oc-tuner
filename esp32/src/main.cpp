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
#include <USBHIDMouse.h>
#include <USBHIDKeyboard.h>

USBHIDAbsoluteMouse Mouse;
USBHIDKeyboard Keyboard;

HardwareSerial &host_serial = Serial;
HardwareSerial &mobo_serial = Serial1;

JsonDocument mkb_input;

// put function declarations here:
int myFunction(int, int);

char buffer[100];

void setup()
{
    host_serial.begin(115200);
    mobo_serial.begin(115200, SERIAL_8N1, 18);
    Mouse.begin();
    Keyboard.begin();
    USB.begin();
}

void loop()
{
    while (mobo_serial.available())
    {
        char c = mobo_serial.read();
        host_serial.write(c);
    }
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
            //JsonArray key_down = mkb_input["key_down"];
            //JsonArray key_up = mkb_input["key_up"];
            ////host_serial.println("Hej!");
            ////serializeJsonPretty(key_down, host_serial);
            ////serializeJsonPretty(key_up, host_serial);
            ////host_serial.println("Hej2!");
            //for (JsonVariant key : key_down)
            //{
            //    Keyboard.pressRaw(key.as<u8_t>());
            //    //host_serial.println(key.as<u8_t>());
            //}
            //for (JsonVariant key : key_up)
            //{
            //    Keyboard.releaseRaw(key.as<u8_t>());
            //    //host_serial.println(key.as<u8_t>());
            //}

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
        }
    }
}

// put function definitions here:
int myFunction(int x, int y)
{
    return x + y;
}

#endif /* ARDUINO_USB_MODE */