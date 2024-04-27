# *****************************************************************************
# * Copyright (c) 2011, 2013-2014, 2016 Wind River Systems, Inc. and others.
# * All rights reserved. This program and the accompanying materials
# * are made available under the terms of the Eclipse Public License 2.0
# * which accompanies this distribution, and is available at
# * https://www.eclipse.org/legal/epl-2.0/
# *
# * Contributors:
# *     Wind River Systems - initial API and implementation
# *****************************************************************************

import collections
import importlib
import threading
from typing import NewType

from .. import protocol
from ..channel import Token
from ..channel.Command import Command
from .arguments import *

_providers = []
_lock = threading.RLock()

TokenType = NewType("TokenType", Token)


class ServiceProvider(object):
    """Clients can implement this abstract class if they want to provide
    implementation of a local service or remote service proxy.
    """

    def getLocalService(self, channel):
        pass

    def getServiceProxy(self, channel, service_name):
        pass


def addServiceProvider(provider):
    with _lock:
        _providers.append(provider)


def removeServiceProvider(provider):
    with _lock:
        _providers.remove(provider)


def onChannelCreated(channel, services_by_name):
    with _lock:
        # TODO ZeroCopy support is incomplete
        # zero_copy = ZeroCopy()
        # services_by_name[zero_copy.getName()] = zero_copy
        for provider in _providers:
            try:
                arr = provider.getLocalService(channel)
                if not arr:
                    continue
                for service in arr:
                    if service.getName() in services_by_name:
                        continue
                    services_by_name[service.getName()] = service
            except Exception as x:
                protocol.log("Error calling TCF service provider", x)


def onChannelOpened(channel, service_names, services_by_name):
    with _lock:
        for name in service_names:
            for provider in _providers:
                try:
                    service = provider.getServiceProxy(channel, name)
                    if not service:
                        continue
                    services_by_name[name] = service
                    break
                except Exception as x:
                    protocol.log("Error calling TCF service provider", x)
            if name in services_by_name:
                continue
            services_by_name[name] = GenericProxy(channel, name)


def getServiceManagerID():
    # In current implementation ServiceManager is a singleton,
    # so its ID is same as agent ID.
    return protocol.getAgentID()


class DoneHWCommand(object):
    """Client call back interface for generic commands."""

    def doneHW(self, token, error, args):
        """Called when memory operation command command is done.
        :param token: Command handle.
        :param error: Error object or **None**.
        """
        pass

    def __call__(self, token, error, args):
        return self.doneHW(token, error, args)


class GenericCallback(object):

    def __init__(self, callback):
        self.callback = callback

    def __getattr__(self, attr):
        if attr.startswith("done"):
            return self.callback


class Service(object):
    """TCF service base class."""

    def __init__(self, channel):
        self.channel = channel

    def getName(self):
        """Abstract method to get the service name.

        :returns: This service name
        """
        raise NotImplementedError("Abstract method")

    def __str__(self):
        """TCF service string representation.

        :returns: The name of the service.
        """
        return self.getName()

    def _makeCallback(self, done):
        """Turn *done* into a callable.

        If *done* is already a :class:`collections.Callable`, it is returned
        as is, else, it is made callable, and returned.

        :param done: The item to make callable.

        :returns: The callable value of *done*
        """
        if isinstance(done, collections.Callable):
            return GenericCallback(done)
        return done

    def send_command(self, name, args, done):
        done = self._makeCallback(done)
        service = self

        class HWCommand(Command):
            def __init__(self):
                super(HWCommand, self).__init__(service.channel,
                                                service.getName(),
                                                name,
                                                args)

            def done(self, error, results):
                if not error:
                    assert len(results) > 0
                    # error = self.toError(results[0])
                    error = results[0]
                    results = results[1:]
                done.doneHW(self.token, error, results)

        return HWCommand().token

    def send_xicom_command(self, name, args, done, progress=None):
        done = self._makeCallback(done)
        service = self

        class XicomCommand(Command):
            def __init__(self):
                super(XicomCommand, self).__init__(service.channel,
                                                   service.getName(),
                                                   name,
                                                   to_xargs(args))

            def done(self, error, results):
                if not error:
                    assert len(results) >= 1
                    error = results[0]
                    if isinstance(error, dict) and 'Format' in error:
                        e = Exception(error['Format'])
                        try:
                            mod = importlib.import_module(error['Module'])
                            cls = getattr(mod, error["Class"])
                            e = cls(f"TCF Error: {service.getName()} {name}: {error['Format']}")
                        except Exception:
                            pass
                        error = e
                    results = from_xargs(results[1:]) if len(results) > 1 else None
                    if results and len(results) == 1:
                        results = results[0]
                if done:
                    done.doneHW(self.token, error, results)

            def progress_update(self, error, results):
                if not error:
                    assert len(results) >= 1
                    error = results[0]
                    if isinstance(error, dict) and 'Format' in error:
                        e = Exception(error['Format'])
                        try:
                            mod = importlib.import_module(error['Module'])
                            cls = getattr(mod, error["Class"])
                            e = cls(f"TCF Error: {service.getName()} {name}: {error['Format']}")
                        except Exception:
                            pass
                        error = e
                    results = from_xargs(results[1:]) if len(results) > 1 else None
                    if results and len(results) == 1:
                        results = results[0]
                if progress:
                    progress(self.token, error, results)

        return XicomCommand().token


class CommandResult(object):
    def __init__(self, token, error, args):
        self.token = token
        self.error = error
        # unwrap result if only one element
        # if args and len(args) == 1 and \
        #         not isinstance(args, dict):
        #     args = args[0]
        self.args = args

    def __str__(self):
        if self.error:
            return "[%s] error: %s" % (self.token.id, self.error)
        return "[%s] result: %s" % (self.token.id, self.args)

    __repr__ = __str__

    def __iter__(self):
        yield self.error
        yield self.args

    def get(self, key=None):
        if key:
            return self.args.get(key)
        return self.args


class CommandWrapper(object):
    def __init__(self, control, command):
        self._control = control
        self._command = command

    def __call__(self, *args, **kwargs):
        return self._control.invoke(self._command, *args, **kwargs)


class ZeroCopy(Service):
    def getName(self):
        return "ZeroCopy"


class GenericProxy(Service):
    """Objects of GenericProxy class represent remote services, which don't
    have a proxy class defined for them.

    Clients still can use such services, but framework will not provide
    service specific utility methods for message formatting and parsing.
    """

    def __init__(self, channel, name):
        self.__channel = channel
        self.name = name

    def getName(self):
        return self.name

    def getChannel(self):
        return self.__channel


class DefaultServiceProvider(ServiceProvider):
    package_base = str(__package__) + ".remote"

    def getLocalService(self, channel):
        # TODO DiagnosticsService
        # return [DiagnosticsService(channel)]
        return []

    def getServiceProxy(self, channel, service_name):
        service = None
        try:
            clsName = service_name + "Proxy"
            package = self.package_base + "." + clsName
            clsModule = __import__(package, fromlist=[clsName],
                                   globals=globals())
            cls = clsModule.__dict__.get(clsName)
            service = cls(channel)
            assert service_name == service.getName()
        except ImportError:
            pass
        except Exception as x:
            protocol.log("Cannot instantiate service proxy for " +
                         service_name, x)
        return service


addServiceProvider(DefaultServiceProvider())
