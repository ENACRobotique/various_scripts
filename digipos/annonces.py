#!/usr/bin/python3
import serial
import time
import datetime
from threading import Lock
import pyinotify

ANNONCES_PATH = "/home/robot/digipos/annonces.txt"

messages = []
mutex = Lock()
wm = pyinotify.WatchManager()
mask = pyinotify.ALL_EVENTS

class EventHandler(pyinotify.ProcessEvent):
  def process_IN_MODIFY(self, event):
    global messages
    mutex.acquire()
    try:
      messages = []
      with open("annonces.txt", 'r') as f:
        for line in f:
          messages.append(str(line).strip())
    finally:
      mutex.release()

handler = EventHandler()
notifier = pyinotify.ThreadedNotifier(wm, handler)
notifier.start()
wdd = wm.add_watch(ANNONCES_PATH, mask)

def run_digipos():
  global messages
  s = serial.Serial("/dev/ttyS0")
  messages = []
  with open(ANNONCES_PATH, 'r') as f:
    for line in f:
      messages.append(str(line).strip())
  i = 0
  s.write(bytes((0x1f, 0x54, datetime.datetime.now().hour, datetime.datetime.now().minute)))
  s.write(bytes((0x1f, 0x55)))
  while True:
    mutex.acquire()
    try:
      mess = messages[i]
      i = (i + 1) % len (messages)
    finally:
      mutex.release()
    assert(len(mess) <= 20)
    s.write(b'\x0b')
    s.write(bytes("                    ", "utf-8"))
    s.write(b'\x0b')
    s.write(bytes((0x1f, 0x24, 10 - int(len(mess) / 2) + 1, 1)))
    s.write(bytes(mess, "utf-8"))
    time.sleep(8)

if __name__ == '__main__':
  run_digipos()

