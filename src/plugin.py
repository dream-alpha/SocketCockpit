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


from Components.config import config
from Plugins.Plugin import PluginDescriptor
from .Debug import logger
from .__init__ import _
from .Version import VERSION
from .SocketCockpit import SocketCockpit
from .ConfigInit import ConfigInit
from .SkinUtils import loadPluginSkin
from .ConfigScreen import ConfigScreen


socket_cockpit = None


def openSettings(session, **__):
	logger.info("...")
	session.open(ConfigScreen, config.plugins.socketcockpit)


def autoStart(reason, **kwargs):
	if reason == 0:  # startup
		if "session" in kwargs:
			logger.info("+++ Version: %s starts...", VERSION)
			loadPluginSkin("skin.xml")
			global socket_cockpit
			if not socket_cockpit:
				socket_cockpit = SocketCockpit()
	elif reason == 1:  # shutdown
		logger.info("--- shutdown")
		if socket_cockpit:
			socket_cockpit.stopServer()
	else:
		logger.info("reason not handled: %s", reason)


def Plugins(**__):
	logger.info("+++ Plugins")
	ConfigInit()
	descriptors = [
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_AUTOSTART,
				PluginDescriptor.WHERE_SESSIONSTART,
			],
			fnc=autoStart
		),
		PluginDescriptor(
			name="SocketCockpit" + " - " + _("Setup"),
			description=_("Open setup"),
			icon="SocketCockpit.svg",
			where=[
				PluginDescriptor.WHERE_PLUGINMENU,
			],
			fnc=openSettings
		)
	]
	return descriptors
