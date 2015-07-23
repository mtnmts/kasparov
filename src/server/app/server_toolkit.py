# Purpose : Support debian command running

import paramiko
import logging
import consts

class ServerConnection(object):
	def __init__(self, username, password, host):
		self._username = username
		self._password = password
		self._host = host
		self._client = paramiko.client.SSHClient()
		self._client.load_system_host_keys()
		self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		self._logger = logging.getLogger(consts.MAIN_LOGGER)
		self._connected = True

	def connect():
		try:
			self._client.connect(self._host, username=self._username, password=self._password)
		except Exception as e:
			self._logger.debug("Error connecting to SSH Server")
			self._logger.error(str(e))
			return False
		return True


	def run_command(client, command):
		''' Returns (stdout, stderr) output '''
		log_cmd(command)
		stdin,stdout,stderr = self.client.exec_command(command)
		wait_for_close(stderr.channel)
		wait_for_close(stdout.channel)

		stdd, stde = stdout.read(), stderr.read()
		log_console(stdd, stde)

		return (stdd, stde)
	
	def log(msg):
		print msg

	def log_info(msg):
		log("INFO: " + msg)

	def log_cmd(command):
		log("Executing: " + command)

	def log_console(stdout='', stderr=''):
		log('\n'.join(['[STDERR] ' + l for l in stderr.splitlines()]))
		log('\n'.join(['[STDOUT] ' + l for l in stderr.splitlines()]))
