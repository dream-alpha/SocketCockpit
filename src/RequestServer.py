#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import threading
import select
import six.moves.cPickle as cPickle
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager  # noqa: F401, pylint: disable=W0611
from .Debug import logger
from .SocketUtils import createServerSocket, sendallSocket, receiveSocket


class RequestServer(threading.Thread):

	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.stop_event = threading.Event()
		threading.Thread.__init__(self)

	def join(self, _timeout=None):
		self.stop_event.set()
		threading.Thread.join(self)

	def getReply(self, request):
		logger.debug("request: %s", request)
		try:
			reply = eval(request)
		except Exception as e:
			logger.error("exception: %s", e)
			reply = None
		if reply is None:
			reply = ""
		logger.debug("len(reply): %s", len(reply))
		return reply

	def sendMultiple(self, sock, data):
		logger.debug("data: %s", data)
		reply_list = self.getReply(data)
		if reply_list:
			to_send = len(reply_list)
			act_sent = 0
			for afile in reply_list:
				data = cPickle.dumps(afile)
				_read_sockets, _write_sockets, _error_sockets = select.select([], [sock], [], 1)
				sendallSocket(sock, data)
				_read_sockets, _write_sockets, _error_sockets = select.select([sock], [], [], 1)
				data = receiveSocket(sock)
				act_sent += 1
				logger.debug("received: %s", data)
			if to_send != act_sent:
				logger.error("to_send: %s, act_sent: %s", to_send, act_sent)

	def sendSingle(self, sock, data):
		logger.debug("data: %s", data)
		afile = self.getReply(data)
		data = cPickle.dumps(afile)
		sendallSocket(sock, data)

	def run(self):
		server_socket = createServerSocket(self.host, self.port)
		if not server_socket:
			return
		connection_list = [server_socket]
		while not self.stop_event.isSet():  # pylint: disable=W1505
			read_sockets, _write_sockets, _error_sockets = select.select(connection_list, [], [], 1)
			for sock in read_sockets:
				if sock == server_socket:
					conn, address = sock.accept()
					connection_list.append(conn)
					logger.debug(("client (%s, %s) connected"), address[0], address[1])
				else:
					connection_list.remove(sock)
					data = receiveSocket(sock)
					logger.debug("received msg: %s", data)
					request_type, data = data.split(":")
					if request_type == "multiple":
						self.sendMultiple(sock, data)
					elif request_type == "single":
						self.sendSingle(sock, data)
					sendallSocket(sock, "done")
					logger.debug("closing connection")
					sock.close()
		server_socket.close()
