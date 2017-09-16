''' Server module accepting the client and dispatching the message to the clients
    that are connected to the server at any moment
'''
import argparse
import json
import websockets
import asyncio

class Server:
    
    DEFAULT_HOST = 'localhost'
    DEFAULT_PORT = 5000

    def __init__(self, config):
        
        self.host = config.host or self.DEFAULT_HOST
        self.port = config.port or self.DEFAULT_PORT
        self._cluster_group = {}
        self._client_cluster = set()


    @classmethod
    def from_command_line(cls):
        config = cls._from_cli()
        _instance = cls(config=config)
        return _instance

    @classmethod
    def _from_cli(cls):
        _config = mdict()
        for key, val in vars(cls._get_args_from_cli()).items():
            _key = key.upper()
            _config[key] = val
        return _config

            
    @classmethod
    def _get_args_from_cli(cls):
        argument_parser = argparse.ArgumentParser(
            description="Server configuration for chat app"
        )
        argument_parser.add_argument(
            '-host',
            action='store',
            type=str,
            dest='host'
        )

        argument_parser.add_argument(
            '-p', '--port',
            action='store',
            type=int,
            dest='port'
        )

        return argument_parser.parse_args()
    
    async def _handler(self, websocket, path):
        print('Got connection from the ', websocket)
        #store the websocket in a set
        self._client_cluster.add(websocket)
        while True:
            #wait for the connection
            try:
                rcv = await websocket.recv()
            except websockets.exceptions.ConnectionClosed:
                self._client_cluster.discard(websocket)
                print('cient removed')
                break
            
            for client in self._client_cluster.difference({websocket}):
                try:
                    await client.send(rcv)
                except websockets.exceptions.ConnectionClosed:
                    #if connection closed
                    print('client removed')
                    self._client_cluster.discard(websocket)
                    break
    
    def run(self):
        #this runs the server

        server = websockets.serve(
            self._handler,
            host=self.host,
            port=self.port
        )
        loop = asyncio.get_event_loop()
        loop.run_until_complete(server)
        loop.run_forever()

# ignore
class mdict(dict):
    '''A dictionary subclass to make code a bit cleaner . I think'''

    def __getattr__(self, key):
        return self[key]
    
    def __setattr__(self, key, val):
        self[key] = val

if __name__ == '__main__':
    s = Server.from_command_line()
    s.run()
    
