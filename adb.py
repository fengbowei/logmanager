import sys
import os
import subprocess

class ADB(object):
    def __init__(self, p2adb = ''):
        self.p2adb = p2adb
        
    def execute(self, cmd = ''):
        cmd = self.p2adb + ' ' + cmd
        
        sub_proc = subprocess.Popen(cmd, stdin = subprocess.PIPE, \
                          stdout = subprocess.PIPE, \
                          stderr = subprocess.PIPE, shell = False)
        (stdout, stderr) = sub_proc.communicate()
        
        return (stdout, stderr)