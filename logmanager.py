import subprocess
from time import time, sleep, mktime

from threading import Thread, Lock
import re

class event(object):
    def __init__(self, cb, params = None, regex = ""):
        self.cb = cb
        self.params = params
        self.regex = regex
        self.isTriggered = False


class logManager(object):
    def __init__(self, p2adb, logtype = "logcat", pollrate = 0.5):
        self.p2adb = p2adb
        self.logtype = logtype
        self.pollrate = pollrate
        self._event_list = []
        self._isRunning = False

    def __logcat_monitor_func(self):
        cmd = self.p2adb + ' shell "logcat -c"'
                  
        sub_proc = subprocess.Popen(cmd, stdin = subprocess.PIPE, \
                              stdout = subprocess.PIPE, \
                              stderr = subprocess.PIPE, shell = False)
        (stdout, stderr) = sub_proc.communicate()
    
        while self._isRunning:
            sleep(self.pollrate)
            
            cmd = self.p2adb + ' shell "logcat -d && logcat -c"'
                  
            sub_proc = subprocess.Popen(cmd, stdin = subprocess.PIPE, \
                                  stdout = subprocess.PIPE, \
                                  stderr = subprocess.PIPE, shell = False)
            (stdout, stderr) = sub_proc.communicate()
            ret = sub_proc.returncode
            
            for event in self._event_list:
                match = event.regex.search(stdout)
                if match:
                    event.isTriggered = True
                    event.cb(match)

    
    def start(self):
        self.logcat_monitor_tread = Thread(target = self.__logcat_monitor_func)
        self.logcat_monitor_tread.daemon = True
        self._isRunning = True
        self.logcat_monitor_tread.start()
    
    def stop(self):
        self._isRunning = False
        
    def registerEvent(self, event):
        if event == None:
            return 1
        else:
           self._event_list.append(event)
