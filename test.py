import re
import time
import datetime
import argparse
import paho.mqtt.client as paho
import feedparser

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90, rotate=2)
device.contrast(1)

def on_three(mqttc, obj, mqmsg):
    print(mqmsg.topic+" "+str(mqmsg.qos)+" "+str(mqmsg.payload))
    device.contrast(240)
    for i in range(3):
        show_message(device, str(mqmsg.payload), fill="white", font=proportional(LCD_FONT))
    device.contrast(1)

def on_message(mqttc, obj, mqmsg):
    print(mqmsg.topic+" "+str(mqmsg.qos)+" "+str(mqmsg.payload))
    device.contrast(240)
    show_message(device, str(mqmsg.payload), fill="white", font=proportional(LCD_FONT))
    device.contrast(1)

def on_unimportant(mqttc, obj, mqmsg):
    print(mqmsg.topic+" "+str(mqmsg.qos)+" "+str(mqmsg.payload))
    show_message(device, str(mqmsg.payload), fill="white", font=proportional(LCD_FONT))



mqtt = paho.Client()
#mqtt.on_message = on_message
mqtt.connect("192.168.101.15", 1883)
mqtt.subscribe("lhd/#")
mqtt.message_callback_add("lhd/message", on_message)
mqtt.message_callback_add("lhd/three", on_three)
mqtt.message_callback_add("lhd/unimportant", on_unimportant)
oldheadline = ''
url = 'http://feeds.bbci.co.uk/news/rss.xml?edition=uk'

print "* Looping"

while 1:
    now = datetime.datetime.now()
    secs = int(time.time()-(int(time.time()/60)*60))

    if (secs == 0 or oldheadline == ''):
        feed = feedparser.parse(url)
        chl = feed.entries[0]['title']
        chl = re.sub(r'[^\w\s]','',chl)
        if (chl != oldheadline):
            print chl
            oldheadline = chl
            show_message(device, chl, fill="white", font=proportional(LCD_FONT))

    msg = now.strftime("%H:%M")
    mqtt.loop(0.5)
    with canvas(device) as draw:
        text(draw, (0,0), msg, fill="white", font=proportional(LCD_FONT))



