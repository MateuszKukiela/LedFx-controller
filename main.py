#!/usr/bin/python
import time
import RPi.GPIO as GPIO
from pigpio_encoder.rotary import Rotary
import json
import requests

URL = 'http://raspberrypi:8887/api/devices/adalight/effects'

# initialisieren
with open('default_effects.json') as json_file:
    effects = json.load(json_file)
names = list(effects.keys())
print(len(names))

# Zuordnung der GPIO Pins (ggf. anpassen)
LCD_RS = 4
LCD_E = 17
LCD_DATA4 = 18
LCD_DATA5 = 22
LCD_DATA6 = 23
LCD_DATA7 = 24

LCD_WIDTH = 16  # Zeichen je Zeile
LCD_LINE_1 = 0x80  # Adresse der ersten Display Zeile
LCD_LINE_2 = 0xC0  # Adresse der zweiten Display Zeile
LCD_CHR = GPIO.HIGH
LCD_CMD = GPIO.LOW
E_PULSE = 0.0005
E_DELAY = 0.0005


def lcd_send_byte(bits, mode):
    # Pins auf LOW setzen
    GPIO.output(LCD_RS, mode)
    GPIO.output(LCD_DATA4, GPIO.LOW)
    GPIO.output(LCD_DATA5, GPIO.LOW)
    GPIO.output(LCD_DATA6, GPIO.LOW)
    GPIO.output(LCD_DATA7, GPIO.LOW)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_DATA4, GPIO.HIGH)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_DATA5, GPIO.HIGH)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_DATA6, GPIO.HIGH)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_DATA7, GPIO.HIGH)
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)
    GPIO.output(LCD_DATA4, GPIO.LOW)
    GPIO.output(LCD_DATA5, GPIO.LOW)
    GPIO.output(LCD_DATA6, GPIO.LOW)
    GPIO.output(LCD_DATA7, GPIO.LOW)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_DATA4, GPIO.HIGH)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_DATA5, GPIO.HIGH)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_DATA6, GPIO.HIGH)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_DATA7, GPIO.HIGH)
    time.sleep(E_DELAY)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DELAY)


def display_init():
    lcd_send_byte(0x33, LCD_CMD)
    lcd_send_byte(0x32, LCD_CMD)
    lcd_send_byte(0x28, LCD_CMD)
    lcd_send_byte(0x0C, LCD_CMD)
    lcd_send_byte(0x06, LCD_CMD)
    lcd_send_byte(0x01, LCD_CMD)


def lcd_message(message):
    message = message.ljust(LCD_WIDTH, " ")
    for i in range(LCD_WIDTH):
        lcd_send_byte(ord(message[i]), LCD_CHR)


def rotary_callback(counter):
    lcd_send_byte(LCD_LINE_2, LCD_CMD)
    lcd_message(str(names[counter])[:20])


def sw_short():
    # lcd_send_byte(LCD_LINE_2, LCD_CMD)
    # my_rotary.counter = 0
    # lcd_message(str(my_rotary.counter).ljust(20))
    effect = effects[names[my_rotary.counter]]
    name = list(effect.keys())[0]
    effect_dict = {'config': effect[name]['config'], 'type': names[my_rotary.counter], 'name': name}
    requests.post(URL, json=effect_dict)


def sw_long():
    print("Switch long press")


if __name__ == '__main__':
    # initialisieren
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(LCD_E, GPIO.OUT)
    GPIO.setup(LCD_RS, GPIO.OUT)
    GPIO.setup(LCD_DATA4, GPIO.OUT)
    GPIO.setup(LCD_DATA5, GPIO.OUT)
    GPIO.setup(LCD_DATA6, GPIO.OUT)
    GPIO.setup(LCD_DATA7, GPIO.OUT)

    display_init()

    lcd_send_byte(LCD_LINE_1, LCD_CMD)
    lcd_message("Select Effect:")

    my_rotary = Rotary(
        clk_gpio=5,
        dt_gpio=6,
        sw_gpio=13
    )
    my_rotary.setup_rotary(
        min=0,
        max=len(effects),
        scale=1,
        debounce=200,
        rotary_callback=rotary_callback
    )
    my_rotary.setup_switch(
        debounce=200,
        long_press=True,
        sw_short_callback=sw_short,
        sw_long_callback=sw_long
    )

    my_rotary.watch()


