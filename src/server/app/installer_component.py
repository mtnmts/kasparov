from autobahn.asyncio.websocket import WebSocketServerProtocol
import trollius as asyncio
import json
import globs
from app.remote import stratagies
from app.models import Target
INSTALL_CMD_VAL = 'INSTALL_CMD'
LOG_MAIN_TYPE = "LOG_MAIN"
LOG_SECONDARY_TYPE = "LOG_SECONDARY"
LOG_ERROR_TYPE = "LOG_ERROR"
LOG_INFO_TYPE = "LOG_INFO"
PROGRESS_REPORT_TYPE = "PROGRESS_REPORT"
SERVER_ID_KEY = "server_id"
TYPE_KEY = "type"
PAYLOAD_KEY = "payload"

import logging
logger = logging.getLogger('websockets.server')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
logging.basicConfig(filename='example.log', filemode='w', level=logging.DEBUG)


class InstallServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		print("Client connecting: {}".format(request.peer))

	def onOpen(self):
		print("WebSocket connection open.")

	def onMessage(self, payload, isBinary):
		if not isBinary:
			self._reactMessage(payload.decode('utf8'))
			

	def _reactMessage(self,data_dict):
		data = json.loads(data_dict)
		if 'ping' in data:
			self.sendMessage(json.dumps({'pong':'ping'}))
			return
		if data[TYPE_KEY] == INSTALL_CMD_VAL:
			zta = Target(str(data['ip']),str(data['password']))
			self._installServer(zta)


	def _installServer(self, target):
		print("Installation has begun")
		self._sendLogMsg("Creating Client Connection...")
		sin.log = lambda msg : self._sendSecondaryMsg(msg)
		try:
			c = sin.create_client(target.ip, target.user, target.password)
			self._sendProgressReport(15)
		except:
			self._sendErrorMsg("Failed connecting to server, Bad IP/Username/Password perhaps?")
			self._sendErrorMsg("Check your connection to the internet also.")
			self._sendProgressReport(100)
			raise
		self._sendLogMsg("Downloading toolkit script to server.")
		try:
			sin.fetch_script(c)
			self._sendProgressReport(30)
			self._sendLogMsg("Script downloaded successfully.")

		except:
			self._sendErrorMsg("Failed fetching script, check detailed log below.")
			self._sendProgressReport(100)
			raise
		self._sendLogMsg("Performing cleanup and upgrades.")
		try:
			sin.perform_cleanup_upgrades(c)
			self._sendProgressReport(50)
			self._sendLogMsg("Cleanup & Upgrade completed successfully.")
		except:
			self._sendErrorMsg("Failed to perform cleanup/upgrades, check detailed log below.")
			self._sendProgressReport(100)
			raise

		self._sendLogMsg("Installing MYSQL")
		try:
			success, passw = sin.install_mysql(c)
			if success:
				self._sendLogMsg("MYSQL Installation successful")
				self._sendInfoMsg("MYSQL username: root, MYSQL Password: " + passw)
				self._sendProgressReport(60)
			if not success:
				self._sendErrorMsg("MYSQL Installation Failed, MYSQL Password has been saved at .my.cnf though.")
				self._sendInfoMsg("(Install Failed, but keep this just incase) MYSQL username: root, MYSQL Password: " + passw)
				self._sendProgressReport(100)
				raise Exception("Quitting!")
		except:
				self._sendErrorMsg("MYSQL Installation Failed.")
				self._sendProgressReport(100)
		self._sendLogMsg("Installing LAMP Stack (dropbear, nginx, php & php modules)")
		try:
			sin.install_lamp_stack(c)
			self._sendLogMsg("LAMP Stack installed successfully")
			self._sendProgressReport(100)
		except:
				self._sendErrorMsg("LAMP Stack Installation Failed.")
				self._sendProgressReport(100)
		self._sendInfoMsg("Finished Installation on " + c.ip)
		
	def _sendSecondaryMsg(self, msg):
		self.sendMessage(json.dumps({TYPE_KEY : LOG_SECONDARY_TYPE, PAYLOAD_KEY : msg}))

	def _sendLogMsg(self, msg):
		self.sendMessage(json.dumps({TYPE_KEY : LOG_MAIN_TYPE, PAYLOAD_KEY : msg}))
	
	def _sendInfoMsg(self, msg):
		self.sendMessage(json.dumps({TYPE_KEY : LOG_INFO_TYPE, PAYLOAD_KEY : msg}))

	def _sendErrorMsg(self, msg):
		self.sendMessage(json.dumps({TYPE_KEY : LOG_ERROR_TYPE, PAYLOAD_KEY : msg}))


	def _sendProgressReport(self, precentage):
		self.sendMessage(json.dumps({TYPE_KEY : PROGRESS_REPORT_TYPE, PAYLOAD_KEY : str(precentage)}))


	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {}".format(reason))



def installer_service():
	from autobahn.asyncio.websocket import WebSocketServerFactory
	loop = asyncio.get_event_loop()
	factory = WebSocketServerFactory()
	factory.protocol = InstallServerProtocol
	loop.set_debug(True)
	print "Starting"
	coro = loop.create_server(factory, '127.0.0.1', 9190)
	server = loop.run_until_complete(coro)
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		server.close()
		loop.close()
	finally:
		server.close()
		loop.close()
