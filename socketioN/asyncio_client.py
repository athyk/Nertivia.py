import asyncio
import logging
import random
import traceback

import engineioN
import nertivia.cache_nertivia_data
import nertivia.message

from . import client
from . import exceptions
from . import packet

default_logger = logging.getLogger('socketioN.client')


class AsyncClient(client.Client):
    """A Socket.IO client for asyncio.

    This class implements a fully compliant Socket.IO web client with support
    for websocket and long-polling transports.

    :param reconnection: ``True`` if the client should automatically attempt to
                         reconnect to the server after an interruption, or
                         ``False`` to not reconnect. The default is ``True``.
    :param reconnection_attempts: How many reconnection attempts to issue
                                  before giving up, or 0 for infinite attempts.
                                  The default is 0.
    :param reconnection_delay: How long to wait in seconds before the first
                               reconnection attempt. Each successive attempt
                               doubles this delay.
    :param reconnection_delay_max: The maximum delay between reconnection
                                   attempts.
    :param randomization_factor: Randomization amount for each delay between
                                 reconnection attempts. The default is 0.5,
                                 which means that each delay is randomly
                                 adjusted by +/- 50%.
    :param logger: To enable logging set to ``True`` or pass a logger object to
                   use. To disable logging set to ``False``. The default is
                   ``False``. Note that fatal errors are logged even when
                   ``logger`` is ``False``.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have ``dumps`` and ``loads``
                 functions that are compatible with the standard library
                 versions.

    The Engine.IO configuration supports the following settings:

    :param request_timeout: A timeout in seconds for requests. The default is
                            5 seconds.
    :param http_session: an initialized ``requests.Session`` object to be used
                         when sending requests to the server. Use it if you
                         need to add special client options such as proxy
                         servers, SSL certificates, etc.
    :param ssl_verify: ``True`` to verify SSL certificates, or ``False`` to
                       skip SSL certificate verification, allowing
                       connections to servers with self signed certificates.
                       The default is ``True``.
    :param engineio_logger: To enable Engine.IO logging set to ``True`` or pass
                            a logger object to use. To disable logging set to
                            ``False``. The default is ``False``. Note that
                            fatal errors are logged even when
                            ``engineio_logger`` is ``False``.
    """

    def is_asyncio_based(self):
        return True

    async def connect(self, url, headers={}, auth=None, transports=None,
                      namespaces=None, socketio_path='socket.io', wait=True,
                      wait_timeout=1):
        """Connect to a Socket.IO server.

        :param url: The URL of the Socket.IO server. It can include custom
                    query string parameters if required by the server. If a
                    function is provided, the client will invoke it to obtain
                    the URL each time a connection or reconnection is
                    attempted.
        :param headers: A dictionary with custom headers to send with the
                        connection request. If a function is provided, the
                        client will invoke it to obtain the headers dictionary
                        each time a connection or reconnection is attempted.
        :param auth: Authentication data passed to the server with the
                     connection request, normally a dictionary with one or
                     more string key/value pairs. If a function is provided,
                     the client will invoke it to obtain the authentication
                     data each time a connection or reconnection is attempted.
        :param transports: The list of allowed transports. Valid transports
                           are ``'polling'`` and ``'websocket'``. If not
                           given, the polling transport is connected first,
                           then an upgrade to websocket is attempted.
        :param namespaces: The namespaces to connect as a string or list of
                           strings. If not given, the namespaces that have
                           registered event handlers are connected.
        :param socketio_path: The endpoint where the Socket.IO server is
                              installed. The default value is appropriate for
                              most cases.
        :param wait: if set to ``True`` (the default) the call only returns
                     when all the namespaces are connected. If set to
                     ``False``, the call returns as soon as the Engine.IO
                     transport is connected, and the namespaces will connect
                     in the background.
        :param wait_timeout: How long the client should wait for the
                             connection. The default is 1 second. This
                             argument is only considered when ``wait`` is set
                             to ``True``.

        Note: this method is a coroutine.

        Example usage::

            sio = socketioN.AsyncClient()
            sio.connect('http://localhost:5000')
        """
        if self.connected:
            raise exceptions.ConnectionError('Already connected')

        self.connection_url = url
        self.connection_headers = headers
        self.connection_auth = auth
        self.connection_transports = transports
        self.connection_namespaces = namespaces
        self.socketio_path = socketio_path

        if namespaces is None:
            namespaces = list(set(self.handlers.keys()).union(
                set(self.namespace_handlers.keys())))
            if len(namespaces) == 0:
                namespaces = ['/']
        elif isinstance(namespaces, str):
            namespaces = [namespaces]
        self.connection_namespaces = namespaces
        self.namespaces = {}
        if self._connect_event is None:
            self._connect_event = self.eio.create_event()
        else:
            self._connect_event.clear()
        real_url = await self._get_real_value(self.connection_url)
        real_headers = await self._get_real_value(self.connection_headers)
        try:
            await self.eio.connect(real_url, headers=real_headers,
                                   transports=transports,
                                   engineio_path=socketio_path)
        except engineioN.exceptions.ConnectionError as exc:
            await self._trigger_event(
                'connect_error', '/',
                exc.args[1] if len(exc.args) > 1 else exc.args[0])
            raise exceptions.ConnectionError(exc.args[0]) from None

        if wait:
            try:
                while True:
                    await asyncio.wait_for(self._connect_event.wait(),
                                           wait_timeout)
                    self._connect_event.clear()
                    if set(self.namespaces) == set(self.connection_namespaces):
                        break
            except asyncio.TimeoutError:
                pass
            if set(self.namespaces) != set(self.connection_namespaces):
                await self.disconnect()
                raise exceptions.ConnectionError(
                    'One or more namespaces failed to connect')

        self.connected = True

    async def wait(self):
        """Wait until the connection with the server ends.

        Client applications can use this function to block the main thread
        during the life of the connection.

        Note: this method is a coroutine.
        """
        while True:
            await self.eio.wait()
            await self.sleep(1)  # give the reconnect task time to start up
            if not self._reconnect_task:
                break
            await self._reconnect_task
            if self.eio.state != 'connected':
                break

    async def emit(self, event, data=None, namespace=None, callback=None):
        """Emit a custom event to one or more connected clients.

        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param data: The data to send to the server. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. To send
                     multiple arguments, use a tuple where each element is of
                     one of the types indicated above.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the the server has received the message. The arguments
                         that will be passed to the function are those provided
                         by the server.

        Note: this method is not designed to be used concurrently. If multiple
        tasks are emitting at the same time on the same client connection, then
        messages composed of multiple packets may end up being sent in an
        incorrect sequence. Use standard concurrency solutions (such as a Lock
        object) to prevent this situation.

        Note 2: this method is a coroutine.
        """
        namespace = namespace or '/'
        if namespace not in self.namespaces:
            raise exceptions.BadNamespaceError(
                namespace + ' is not a connected namespace.')
        self.logger.info('Emitting event "%s" [%s]', event, namespace)
        if callback is not None:
            id = self._generate_ack_id(namespace, callback)
        else:
            id = None
        # tuples are expanded to multiple arguments, everything else is sent
        # as a single argument
        if isinstance(data, tuple):
            data = list(data)
        elif data is not None:
            data = [data]
        else:
            data = []
        await self._send_packet(packet.Packet(
            packet.EVENT, namespace=namespace, data=[event] + data, id=id))

    async def send(self, data, namespace=None, callback=None):
        """Send a message to one or more connected clients.

        This function emits an event with the name ``'message'``. Use
        :func:`emit` to issue custom event names.

        :param data: The data to send to the server. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. To send
                     multiple arguments, use a tuple where each element is of
                     one of the types indicated above.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param callback: If given, this function will be called to acknowledge
                         the the server has received the message. The arguments
                         that will be passed to the function are those provided
                         by the server.

        Note: this method is a coroutine.
        """
        await self.emit('message', data=data, namespace=namespace,
                        callback=callback)

    async def call(self, event, data=None, namespace=None, timeout=60):
        """Emit a custom event to a client and wait for the response.

        :param event: The event name. It can be any string. The event names
                      ``'connect'``, ``'message'`` and ``'disconnect'`` are
                      reserved and should not be used.
        :param data: The data to send to the server. Data can be of
                     type ``str``, ``bytes``, ``list`` or ``dict``. To send
                     multiple arguments, use a tuple where each element is of
                     one of the types indicated above.
        :param namespace: The Socket.IO namespace for the event. If this
                          argument is omitted the event is emitted to the
                          default namespace.
        :param timeout: The waiting timeout. If the timeout is reached before
                        the client acknowledges the event, then a
                        ``TimeoutError`` exception is raised.

        Note: this method is not designed to be used concurrently. If multiple
        tasks are emitting at the same time on the same client connection, then
        messages composed of multiple packets may end up being sent in an
        incorrect sequence. Use standard concurrency solutions (such as a Lock
        object) to prevent this situation.

        Note 2: this method is a coroutine.
        """
        callback_event = self.eio.create_event()
        callback_args = []

        def event_callback(*args):
            callback_args.append(args)
            callback_event.set()

        await self.emit(event, data=data, namespace=namespace,
                        callback=event_callback)
        try:
            await asyncio.wait_for(callback_event.wait(), timeout)
        except asyncio.TimeoutError:
            raise exceptions.TimeoutError() from None
        return callback_args[0] if len(callback_args[0]) > 1 \
            else callback_args[0][0] if len(callback_args[0]) == 1 \
            else None

    async def disconnect(self):
        """Disconnect from the server.

        Note: this method is a coroutine.
        """
        # here we just request the disconnection
        # later in _handle_eio_disconnect we invoke the disconnect handler
        for n in self.namespaces:
            await self._send_packet(packet.Packet(packet.DISCONNECT,
                                                  namespace=n))
        await self.eio.disconnect(abort=True)

    def start_background_task(self, target, *args, **kwargs):
        """Start a background task using the appropriate async model.

        This is a utility function that applications can use to start a
        background task using the method that is compatible with the
        selected async mode.

        :param target: the target function to execute.
        :param args: arguments to pass to the function.
        :param kwargs: keyword arguments to pass to the function.

        This function returns an object compatible with the `Thread` class in
        the Python standard library. The `start()` method on this object is
        already called by this function.
        """
        return self.eio.start_background_task(target, *args, **kwargs)

    async def sleep(self, seconds=0):
        """Sleep for the requested amount of time using the appropriate async
        model.

        This is a utility function that applications can use to put a task to
        sleep without having to worry about using the correct call for the
        selected async mode.

        Note: this method is a coroutine.
        """
        return await self.eio.sleep(seconds)

    async def _get_real_value(self, value):
        """Return the actual value, for parameters that can also be given as
        callables."""
        if not callable(value):
            return value
        if asyncio.iscoroutinefunction(value):
            return await value()
        return value()

    async def _send_packet(self, pkt):
        """Send a Socket.IO packet to the server."""
        encoded_packet = pkt.encode()
        if isinstance(encoded_packet, list):
            for ep in encoded_packet:
                await self.eio.send(ep)
        else:
            await self.eio.send(encoded_packet)

    async def _handle_connect(self, namespace, data):
        namespace = namespace or '/'
        if namespace not in self.namespaces:
            self.logger.info('Namespace {} is connected'.format(namespace))
            self.namespaces[namespace] = (data or {}).get('sid', self.sid)
            await self._trigger_event('connect', namespace=namespace)
            self._connect_event.set()

    async def _handle_disconnect(self, namespace):
        if not self.connected:
            return
        namespace = namespace or '/'
        await self._trigger_event('disconnect', namespace=namespace)
        if namespace in self.namespaces:
            del self.namespaces[namespace]
        if not self.namespaces:
            self.connected = False
            await self.eio.disconnect(abort=True)

    async def _handle_event(self, namespace, id, data):
        namespace = namespace or '/'
        self.logger.info('Received event "%s" [%s]', data[0], namespace)
        try:
            r = await self._trigger_event(data[0], namespace, *data[1:])
        except Exception:
            print(traceback.format_exc())
        if id is not None:
            # send ACK packet with the response returned by the handler
            # tuples are expanded as multiple arguments
            if r is None:
                data = []
            elif isinstance(r, tuple):
                data = list(r)
            else:
                data = [r]
            await self._send_packet(packet.Packet(
                packet.ACK, namespace=namespace, id=id, data=data))

    async def _handle_ack(self, namespace, id, data):
        namespace = namespace or '/'
        self.logger.info('Received ack [%s]', namespace)
        callback = None
        try:
            callback = self.callbacks[namespace][id]
        except KeyError:
            # if we get an unknown callback we just ignore it
            self.logger.warning('Unknown callback received, ignoring.')
        else:
            del self.callbacks[namespace][id]
        if callback is not None:
            if asyncio.iscoroutinefunction(callback):
                await callback(*data)
            else:
                callback(*data)

    async def _handle_error(self, namespace, data):
        namespace = namespace or '/'
        self.logger.info('Connection to namespace {} was rejected'.format(
            namespace))
        if data is None:
            data = tuple()
        elif not isinstance(data, (tuple, list)):
            data = (data,)
        await self._trigger_event('connect_error', namespace, *data)
        self._connect_event.set()
        if namespace in self.namespaces:
            del self.namespaces[namespace]
        if namespace == '/':
            self.namespaces = {}
            self.connected = False

    async def _call_event(self, event, namespace, data=None):
        namespace = namespace or '/'
        self.logger.info('Received custom event "%s" [%s]', event, namespace)
        try:
            if data:
                r = await self._trigger_event(event, namespace, data)
            else:
                r = await self._trigger_event(event, namespace)
        except Exception as e:
            print(traceback.format_exc())

    async def _trigger_event(self, event, namespace, *args):
        """Invoke an application event handler."""
        # first see if we have an explicit handler for the event
        ret = None
        if event == "server:joined":
            nertivia.cache_nertivia_data.guilds[str(args[0]["server_id"])] = nertivia.Server(args[0])
        elif event == "success":

            servers = args[0]["user"]["servers"]

            for guild in servers:
                try:
                    nertivia.cache_nertivia_data.guilds[guild["server_id"]] = nertivia.Server(guild)

                except Exception as e:
                    print(traceback.format_exc())

            members = args[0]["serverMembers"]
            for member in members:
                nertivia.cache_nertivia_data.users[member["member"]["id"]] = nertivia.User(member["member"])
            nertivia.cache_nertivia_data.user = nertivia.User(args[0]["user"])

            await self._call_event("update_bot_user", "/", nertivia.cache_nertivia_data.user)
            await self._call_event("on_ready", "/")

        if event == "receiveMessage":
            nertivia.cache_nertivia_data.messages[str(args[0]["message"]["messageID"])] = nertivia.message.Message(
                *args)
        if event == "server:member_add":
            nertivia.cache_nertivia_data.users[str(args[0]["member"]["id"])] = nertivia.User(args[0])
        # ["update_message",{"channelID":"6802723449891459072","message":"91a",
        # "creator":{"id":"6597216273183019008","username":"FluxedScript","tag":"0000","avatar":"6597216273183019008/6721500359669321728/avatar.png","badges":8},
        # "created":1628775136388, "mentions":[],"quotes":[],"messageID":"6831578069652738048",
        # "timeEdited":1628861635958,"files":[],"embed":0}]
        # noinspection PyTypeChecker
        before_message = None
        # noinspection PyTypeChecker
        after_message = None
        if event == "update_message":
            before_message: nertivia.message.Message = nertivia.cache_nertivia_data.messages.__getitem__(str(args[0]["messageID"]))
            nertivia.cache_nertivia_data.messages[str(args[0]["messageID"])] = nertivia.message.Message({"message": args[0]})
            after_message: nertivia.message.Message = nertivia.cache_nertivia_data.messages.__getitem__(str(args[0]["messageID"]))
        if namespace in self.handlers and event in self.handlers[namespace]:
            if asyncio.iscoroutinefunction(self.handlers[namespace][event]):
                try:
                    for handler in self.handlers[namespace][event]:
                        try:
                            if event == "receiveMessage":
                                ret = await handler(nertivia.message.Message(*args))
                            elif event == "delete_message":
                                ret = await handler(
                                    nertivia.cache_nertivia_data.messages.__getitem__(str(args[0]["messageID"])))
                            elif event == "update_message":
                                ret = await handler(before_message, after_message)
                            elif event == "success":
                                ret = await handler(nertivia.user.User(*args))
                            else:
                                ret = await handler(*args)
                        except asyncio.CancelledError:  # pragma: no cover
                            ret = None
                except Exception as e:

                    await self.handlers[namespace][event](*args)
                    print(traceback.format_exc())
            else:
                try:
                    for handler in self.handlers[namespace][event]:
                        if event == "receiveMessage":
                            ret = await handler(nertivia.message.Message(*args))
                        elif event == "update_message":
                            ret = await handler(before_message, after_message)
                        elif event == "delete_message":
                            try:
                                ret = await handler(nertivia.cache_nertivia_data.messages[str(args[0]["messageID"])])
                            except:
                                pass
                        else:
                            ret = await handler(*args)
                except Exception as e:
                    self.handlers[namespace][event](*args)

        if event == "delete_message":
            nertivia.cache_nertivia_data.messages.pop(str(args[0]["messageID"]))
        if event == "server:member_remove":
            del nertivia.cache_nertivia_data.users[(str(args[0]["member"]["id"]))]
        if event == "server:leave":
            del nertivia.cache_nertivia_data.guilds[str(args[0]["server_id"])]

        # or else, forward the event to a namepsace handler if one exists
        if namespace in self.namespace_handlers:
            return await self.namespace_handlers[namespace].trigger_event(
                event, *args)
        return ret

    async def _handle_reconnect(self):
        if self._reconnect_abort is None:  # pragma: no cover
            self._reconnect_abort = self.eio.create_event()
        self._reconnect_abort.clear()
        client.reconnecting_clients.append(self)
        attempt_count = 0
        current_delay = self.reconnection_delay
        while True:
            delay = current_delay
            current_delay *= 2
            if delay > self.reconnection_delay_max:
                delay = self.reconnection_delay_max
            delay += self.randomization_factor * (2 * random.random() - 1)
            self.logger.info(
                'Connection failed, new attempt in {:.02f} seconds'.format(
                    delay))
            try:
                await asyncio.wait_for(self._reconnect_abort.wait(), delay)
                self.logger.info('Reconnect task aborted')
                break
            except (asyncio.TimeoutError, asyncio.CancelledError):
                pass
            attempt_count += 1
            try:
                await self.connect(self.connection_url,
                                   headers=self.connection_headers,
                                   auth=self.connection_auth,
                                   transports=self.connection_transports,
                                   namespaces=self.connection_namespaces,
                                   socketio_path=self.socketio_path)
            except (exceptions.ConnectionError, ValueError):
                pass
            else:
                self.logger.info('Reconnection successful')
                self._reconnect_task = None
                break
            if self.reconnection_attempts and \
                    attempt_count >= self.reconnection_attempts:
                self.logger.info(
                    'Maximum reconnection attempts reached, giving up')
                break
        client.reconnecting_clients.remove(self)

    async def _handle_eio_connect(self):
        """Handle the Engine.IO connection event."""
        self.logger.info('Engine.IO connection established')
        self.sid = self.eio.sid
        real_auth = await self._get_real_value(self.connection_auth)
        for n in self.connection_namespaces:
            await self._send_packet(packet.Packet(
                packet.CONNECT, data=real_auth, namespace=n))

    async def _handle_eio_message(self, data):
        """Dispatch Engine.IO messages."""
        if self._binary_packet:
            pkt = self._binary_packet
            if pkt.add_attachment(data):
                self._binary_packet = None
                if pkt.packet_type == packet.BINARY_EVENT:
                    await self._handle_event(pkt.namespace, pkt.id, pkt.data)
                else:
                    await self._handle_ack(pkt.namespace, pkt.id, pkt.data)
        else:
            pkt = packet.Packet(encoded_packet=data)
            if pkt.packet_type == packet.CONNECT:
                await self._handle_connect(pkt.namespace, pkt.data)
            elif pkt.packet_type == packet.DISCONNECT:
                await self._handle_disconnect(pkt.namespace)
            elif pkt.packet_type == packet.EVENT:
                await self._handle_event(pkt.namespace, pkt.id, pkt.data)
            elif pkt.packet_type == packet.ACK:
                await self._handle_ack(pkt.namespace, pkt.id, pkt.data)
            elif pkt.packet_type == packet.BINARY_EVENT or \
                    pkt.packet_type == packet.BINARY_ACK:
                self._binary_packet = pkt
            elif pkt.packet_type == packet.CONNECT_ERROR:
                await self._handle_error(pkt.namespace, pkt.data)
            else:
                raise ValueError('Unknown packet type.')

    async def _handle_eio_disconnect(self):
        """Handle the Engine.IO disconnection event."""
        self.logger.info('Engine.IO connection dropped')
        if self.connected:
            for n in self.namespaces:
                await self._trigger_event('disconnect', namespace=n)
            self.namespaces = {}
            self.connected = False
        self.callbacks = {}
        self._binary_packet = None
        self.sid = None
        if self.eio.state == 'connected' and self.reconnection:
            self._reconnect_task = self.start_background_task(
                self._handle_reconnect)

    def _engineio_client_class(self):
        return engineioN.AsyncClient
