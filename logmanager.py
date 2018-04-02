from time import time, sleep, mktime
from adb import ADB

from threading import Thread, Lock
import re
import os

#global
cacheFilePath = os.getcwd() + '\cache.txt'

class event(object):
    def __init__(self, cb, params = None, regex = "", startline = 0):
        self.cb = cb
        self.params = params
        self.regex = regex
        self.startline = startline


class logManager(object):
    def __init__(self, p2adb, logtype = "logcat", pollrate = 0.5):
        self.adb = ADB(p2adb)
        self.logtype = logtype
        self.pollrate = pollrate
        self._event_list = []
        self._isRunning = False
        self.logcat_monitor_tread = None
        self.cacheMutex = Lock()
        self.cacheLineNum = 0

    def __logcat_monitor_func(self):
        (stdout, stderr) = self.adb.execute(' shell "logcat -c"')
    
        while self._isRunning:
            sleep(self.pollrate)
            
            (stdout, stderr) = self.adb.execute(' shell "logcat -d && logcat -c"')
            
            self.cacheMutex.acquire()
            self.cacheLineNum += len(stdout.splitlines())
            with open(cacheFilePath, "a+") as f:
                f.write(stdout)
            self.cacheMutex.release()
            
            for event in self._event_list:
                match = event.regex.search(stdout)
                if match:
                    event.cb(match)

    
    def start(self):
        # create cache file
        if os.path.exists(cacheFilePath):
            os.remove(cacheFilePath)
        
        # create  thread for logcat monitor
        self.logcat_monitor_tread = Thread(target = self.__logcat_monitor_func)
        self.logcat_monitor_tread.daemon = False
        self._isRunning = True
        self.logcat_monitor_tread.start()
    
    def stop(self):
        self._isRunning = False
        self.logcat_monitor_tread.join()

        if os.path.exists(cacheFilePath):
            os.remove(cacheFilePath)
        
    def registerEvent(self, cb = None, params = None, regex = ""):
        if cb == None or regex == "":
            return -1
        self.cacheMutex.acquire()
        e = event(cb, params, regex, self.cacheLineNum)
        self._event_list.append(e)
        ret = len(self._event_list) - 1
        self.cacheMutex.release()
        
        return ret
        
    def getLogHistory(self, eventhandle):
        self.cacheMutex.acquire()
        # assume evenhandle always exist, need to refine
        with open(cacheFilePath, "r") as f:
                loghist = f.readlines()[self._event_list[eventhandle].startline:]
        self.cacheMutex.release()
        return ''.join(loghist)

        
