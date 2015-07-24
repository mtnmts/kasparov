# Purpose : Support debian command running

import time
import paramiko
import logging
import consts
import traceback

class ServerConnection(object):
	def __init__(self, username, password, host):
		self._username = username
		self._password = password
		self._host = host
		self._client = paramiko.client.SSHClient()
		self._client.load_system_host_keys()
		self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self._logger = logging.getLogger(consts.MAIN_LOGGER)
		self._connected = False

	def connect(self):
		try:
			self._client.connect(self._host, username=self._username, password=self._password)
			#self._sftp = paramiko.SFTPClient.from_transport(self._client.get_transport())
		except Exception as e:
			traceback.print_exc()
			self._logger.debug("Error connecting to SSH Server")
			self._logger.error(str(e))
			return False
		self._connected = True
		return True


	def run_command(self, command):
		''' Returns (stdout, stderr) output '''
		#log_cmd(command)
		stdin,stdout,stderr = self._client.exec_command(command)
		self._wait_for_close(stderr.channel)
		self._wait_for_close(stdout.channel)

		stdd, stde = stdout.read(), stderr.read()
		#log_console(stdd, stde)

		return (stdd, stde)


	def _wait_for_close(self, channel, max_sleep = 600):
		SLEEP_INTERVAL = 0.1
		total = 0
		while not channel.closed and total < max_sleep:
			time.sleep(SLEEP_INTERVAL)
			total += SLEEP_INTERVAL
		if total > max_sleep:
			raise Exception("Sleep time exceeded while waiting for channel to close.")

	def log(self, msg):
		print msg

	def log_info(self, msg):
		log("INFO: " + msg)

	def log_cmd(self, command):
		log("Executing: " + command)

	def log_console(self, stdout='', stderr=''):
		log('\n'.join(['[STDERR] ' + l for l in stderr.splitlines()]))
		log('\n'.join(['[STDOUT] ' + l for l in stderr.splitlines()]))
