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


import select
import threading
import six.moves.cPickle as cPickle
from .Debug import logger
from .SocketUtils import createClientSocket, sendSocket, receiveSocket


class RequestClient(threading.Thread):

	def __init__(self, host, port, request):
		logger.debug("request: %s", request)
		self.host = host
		self.port = port
		self.request = request
		threading.Thread.__init__(self)

	def run(self):
		request_type, _ = self.request.split(":")
		self.reply = None
		sock = createClientSocket(self.host, self.port)
		if not sock:
			return
		if sendSocket(sock, self.request):
			while True:
				_read_sockets, _write_sockets, _error_sockets = select.select([sock], [], [], 1)
				data = receiveSocket(sock)
				if request_type == "multiple":
					if self.reply is None:
						self.reply = []
					if data:
						logger.debug("received len(data): %s", len(data))
						if data != "done":
							try:
								self.reply.append(cPickle.loads(data))
							except Exception as e:
								logger.error("exeption: %s, data: %s", e, data)
							_read_sockets, _write_sockets, _error_sockets = select.select([], [sock], [], 1)
							sendSocket(sock, "next")
						else:
							logger.debug("done.")
							logger.debug("received %s list entries.", len(self.reply))
							break
					else:
						logger.debug("no data")
						break
				elif request_type == "single":
					if self.reply is None:
						self.reply = ""
					if data:
						if not data.endswith("done"):
							logger.debug("received len(data): %s", len(data))
							self.reply += data
						else:
							self.reply += data[:-4]
							self.reply = cPickle.loads(self.reply)
							logger.debug("received len(data): %s.", len(data))
							logger.debug("done.")
							break
					else:
						logger.debug("no data")
						break
		logger.debug("closing client connection.")
		sock.close()
