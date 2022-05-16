
from pprint import pprint

import json
from pyexpat.errors import messages

import tornado.web
import tornado.websocket
import tornado.ioloop
import time
from tornado import gen

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clint_dc = {}
    ID = 0

    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)

        self.socket_id = WebSocketHandler.ID

        WebSocketHandler.ID += 1

    def simple_init(self):
        self.last = time.time()
        self.stop = False

    def open(self):
        self.simple_init()
        self.clint_dc[self.socket_id] = self

        print(f"New client {self.socket_id} connected")
        self.write_message(f"FROM_SERVER|| You are connected server {self.socket_id}")

        self.loop = tornado.ioloop.PeriodicCallback(self.check_ten_seconds, 1000)
        self.loop.start()

    def on_message(self, message):
        print(message, type(message))

        data = json.loads(message)
        for client_id, client in WebSocketHandler.clint_dc.items():
            client.write_message(f"FROM_SERVER|| Client ID {self.socket_id} {data['name']} said: " + data['message'])

        self.last = time.time()

    def on_close(self):
        print("Client disconnected")
        self.loop.stop()

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def run(self):
        while True:
            msg = yield self.ws.read_message()
            print('\x1b[1;32m' + f'FROM ({self})msg: {msg}' + '\x1b[0m')

            if msg is None:
                print("connection closed")
                self.ws = None
                break

    def check_ten_seconds(self):
        if (time.time() - self.last > 10):
            # self.write_message("FROM_server You sleeping mate?")
            print('ping')
            self.last = time.time()

class HDRCreateServerConfig(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        resp = {
            "status_code" : -1
        }
            
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        self.write(json.dumps(resp))
        self.flush()
        self.finish()

application = tornado.web.Application([
    (r'/ws', WebSocketHandler),
    ])

application_2 = tornado.web.Application([
    (r'/test', HDRCreateServerConfig),
    ])

def test():
    print('123')
    
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer(application)
    # http_server_2 = tornado.httpserver.HTTPServer(application_2)

    http_server.listen(8888)
    # http_server_2.listen(8080)

    print('\x1b[31;21m' + f'run server' + '\x1b[0m')
    # tornado.ioloop.IOLoop.instance().start()
    io_loop = tornado.ioloop.IOLoop.current()
    io_loop.start()

    io_loop.create_task()