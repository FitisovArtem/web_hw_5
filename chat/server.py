import asyncio
import logging
from aiofile import async_open
import aiopath

import websockets
from websockets import WebSocketServerProtocol
import names
from websockets.exceptions import ConnectionClosedOK
from main import main as exchange_main

logging.basicConfig(level=logging.INFO)
filename = "exchange_log.log"
path = aiopath.Path()

class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if 'exchange' in message:
                await log_to_file(message)
                day = 0
                mess = message.split(" ")
                if len(mess) > 1 and mess[1].isdigit():
                    day = int(mess[1])
                exchange = await exchange_main(day)
                await self.send_to_clients(exchange)
            else:
                await self.send_to_clients(f"{ws.name}: {message}")


async def log_to_file(context):
    pass

async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    asyncio.run(main())
