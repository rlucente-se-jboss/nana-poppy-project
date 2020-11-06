#!/usr/bin/env python3
#
# Copyright 2020 Rich Lucente
#
# Source code adapted from
# https://github.com/google/aiyprojects-raspbian/src/examples/voice/assistant_grpc_demo.py
# 
# Original source header follows
#
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""A demo of the Google Assistant GRPC recognizer."""

import argparse
import locale
import logging
import signal
import sys

from datetime import datetime
import inflect
import pyowm
import random
import time

from aiy.assistant.grpc import AssistantServiceClientWithLed
from aiy.board import Board, Led
from aiy.voice.audio import play_wav

def volume(string):
    value = int(string)
    if value < 0 or value > 100:
        raise argparse.ArgumentTypeError('Volume must be in [0...100] range.')
    return value

def locale_language():
    language, _ = locale.getdefaultlocale()
    return language

def main():
    logging.basicConfig(level=logging.DEBUG)
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

    parser = argparse.ArgumentParser(description='Assistant service example.')
    parser.add_argument('--language', default=locale_language())
    parser.add_argument('--volume', type=volume, default=100)
    args = parser.parse_args()

    with Board() as board:
        assistant = AssistantServiceClientWithLed(board=board,
                                                  volume_percentage=args.volume,
                                                  language_code=args.language)

        # indicate app is ready after power on
        board.led.state = Led.BLINK
        time.sleep(4)
        board.led.state = Led.OFF

        while True:
            board.button.wait_for_press()
            generate_messages()
            assistant.conversation()

def generate_date_msg(now, p):
    msg = ['good']
    hour = now.time().hour

    # arbitrary cutoffs for morning, afternoon, evening, and night
    if hour < 12:
        msg.append('morning')
    elif hour < 17:
        msg.append('afternoon')
    elif hour < 20:
        msg.append('evening')
    else:
        msg.append('night')

    msg.extend(['nana_and_poppy', 'today', 'is'])

    # month name in lowercase
    msg.append(now.strftime("%B").lower())

    # word expression of ordinal day (e.g. first, twenty second, etc)
    day = now.date().day
    msg.extend(p.number_to_words(p.ordinal(day)).replace('-', ' ').split(' '))
    return msg

def generate_time_msg(now, p):
    msg = ['the_time', 'is']

    hour = now.time().hour

    ampm = "am"
    if hour > 11:
        ampm = "pm"

    # convert to 12 hour format
    hour %= 12
    if hour == 0:
        hour = 12

    msg.append(p.number_to_words(hour))

    minute=now.time().minute

    if minute > 0 and minute < 10:
        msg.append('oh')

    if minute > 0:
        msg.extend(p.number_to_words(minute).replace('-', ' ').split(' '))

    msg.append(ampm)
    return msg

def generate_temp_msg(owm_mgr, location, p):
    msg = ['the_current_temperature_for', location, 'is']

    # location is lowercase with underscore instead of spaces.
    # Convert to format for use with OpenWeatherMap API
    city = location.replace('_', ' ').title() + ', US'
    try:
        # get current temperature in fahrenheit for location
        obs = owm_mgr.weather_at_place(city)
        temp = round(obs.weather.temperature('fahrenheit')['temp'])

        if temp < 0:
            msg.append('minus')
            temp = -temp

        msg.extend(p.number_to_words(temp).replace('-', ' ').split(' '))
    except:
        # lack of network connectivity replaces temp with "minus minus"
        msg.extend(['minus', 'minus'])

    msg.append('degrees')
    return msg

def generate_messages():
    now = datetime.now()
    p = inflect.engine()

    greeting1 = generate_date_msg(now, p)
    greeting2 = generate_time_msg(now, p)

    # OpenWeatherMap API key
    owm = pyowm.OWM('YOUR-OPEN-WEATHER-MANAGER-API-KEY')
    mgr = owm.weather_manager()

    greeting3 = generate_temp_msg(mgr, 'waynesboro', p)
    greeting4 = generate_temp_msg(mgr, 'ocean_city', p)

    children = ['child1', 'child2']
    random.shuffle(children)

    play_files(children[0], greeting1)
    play_files(children[1], greeting2)
    play_files(children[0], greeting3)
    play_files(children[1], greeting4)

def play_files(child, msg):
    for word in msg:
        filepath = '/home/pi/' + child + '/' + word + '.wav'
        play_wav(filepath)

if __name__ == '__main__':
    main()
