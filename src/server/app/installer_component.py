from autobahn.asyncio.websocket import WebSocketServerProtocol
import trollius as asyncio
import json

INSTALL_CMD_VAL = 'INSTALL_CMD'
SERVER_ID_KEY = "server_id"
TYPE_KEY = "type"

class InstallServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		print("Client connecting: {}".format(request.peer))

	def onOpen(self):
		print("WebSocket connection open.")

	def onMessage(self, payload, isBinary):
		if isBinary:
			print("Binary message received: {} bytes".format(len(payload)))
		else:
			print "Datapacket recieved, handling"
	 		_reactMessage(json.loads(payload.decode('utf8')))

	def _reactMessage(data_dict):
		print data_dict
		if data_dict[TYPE_KEY] == INSTALL_CMD_VAL:
			print "Install Command Recieved, initiate installation of " + str(data_dict[SERVER_ID_KEY])

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {}".format(reason))



def installer_service():
	from autobahn.asyncio.websocket import WebSocketServerFactory
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	factory = WebSocketServerFactory()
	factory.protocol = InstallServerProtocol
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
