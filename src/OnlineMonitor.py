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


from enigma import eTimer
from Components.config import config
from .Debug import logger
from .SocketUtils import pingHost


PING = 10 * 1000
instance = None


class OnlineMonitor():

	def __init__(self):
		logger.info("...")
		self.online = False
		self.online_timer = eTimer()
		self.online_timer_conn = self.online_timer.timeout.connect(self.doPing)

	@staticmethod
	def getInstance():
		global instance
		if instance is None:
			instance = OnlineMonitor()
		return instance

	def start(self):
		# logger.info("...")
		self.doPing()

	def stop(self):
		# logger.info("...")
		self.online_timer.stop()

	def isOnline(self):
		# logger.info("online: %s", self.online)
		return self.online

	def doPing(self):
		logger.info("...")
		self.online = pingHost(config.plugins.socketcockpit.server_ip_address.value)
		self.online_timer.start(PING, True)
