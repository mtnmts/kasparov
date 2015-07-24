# Purpose : Support debian command running

import time
import paramiko
import logging
import app.consts as consts
import re
import traceback

SUPPORTED_PLATFORM_REGEX = ".*deb[6|7].*"


class ServerConnection(object):

    def __init__(self, username, password, host):
        self._username = username
        self._password = password
        self._host = host
        self._client = paramiko.client.SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._logger = logging.getLogger(__name__)
        self._connected = False

    def verify(self):
        # Confirm VM is good for execution:
        # - Debian
        # - Root access
        # - Connected already
        if not self._connected:
            self._logger.info("Verify failed: Not connected")
            return False
        if not self.RunCommandAnticipate('uname -a', SUPPORTED_PLATFORM_REGEX):
            self._logger.info("Verify failed: Not debian-based uname -a: " + output)
            return False
        
        if not self._verify_root():
            self._logger.info("Verify failed: not root")
            return False
        
        return True
    
    def _verify_root(self):
        if not self.RunCommandAnticipate('/usr/bin/id -u','0'):
            return False
        return True


    def connect(self):
        try:
            self._client.connect(
                self._host, username=self._username, password=self._password)
            self._sftp = paramiko.SFTPClient.from_transport(self._client.get_transport())
        except Exception as e:
            self._logger.error("Error connecting to SSH Server")
            self._logger.debug(str(e))
            return False
        self._connected = True
        return True

    def runCommand(self, command, join_streams=True):
        ''' Returns (stdout, stderr) output '''
        stdin, stdout, stderr = self._client.exec_command(command)
        if not self._wait_for_close(stderr.channel) or not self._wait_for_close(stdout.channel):
            self._logger.error("Timed out executing command: " + command)
            return False

        stdd, stde = stdout.read(), stderr.read()
        if  join_streams:
            stdj = stdd.splitlines() + stde.splitlines()
            return '\n'.join(stdj)
        return (stdd, stde)

    def RunCommandAnticipate(self, command, anticipated_regex):
        output = self.runCommand(command)
        if output:
            if re.match(anticipated_regex, output):
                return True
            return False
        else:
            self._logger.error("RunCommandAnticipate failed running command (Pre-regex test)")
            return False

    def _wait_for_close(self, channel, max_sleep=600):
        SLEEP_INTERVAL = 0.1
        total = 0
        while not channel.closed and total < max_sleep:
            time.sleep(SLEEP_INTERVAL)
            total += SLEEP_INTERVAL
        if total > max_sleep:
            self._logger.error("Timed out waiting for channel to close")
            return False
        return True
