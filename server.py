import asyncio
import websockets
import json
import uuid
import time
import random
import ssl
import pathlib
import os

connected = set()
players = set()
game = None

def send_all(msg):
    for user in connected:
        asyncio.ensure_future(user.sock.send(msg))

texts = []
for file in os.scandir('text'):
    with open(file) as fp:
        texts += fp.readlines()

texts = [t.strip() for t in texts]

class Game:
    def __init__(self):
        global game
        game = self
        self.text = texts[random.randint(0, len(texts) - 1)]
        self.started = False
        self.lastrank = 0
        async def timer():
            for sec in range(10,0,-1):
                send_all(json.dumps({'type': 'ready', 'sec': sec}))
                await asyncio.sleep(1)
            self.start()
        self.start_timer = asyncio.ensure_future(timer())
        async def timeout():
            for sec in range(60):
                send_all(json.dumps({'type': 'timeout', 'sec': sec}))
                await asyncio.sleep(1)
            end_game()
        self.timeout_timer = asyncio.ensure_future(timeout())

    def start(self):
        print("game begin")
        self.started = True
        self.start_time = time.time()
        send_all(json.dumps({'type': 'ready', 'sec': 0, 'text': self.text}))

    def end(self):
        self.start_timer.cancel()
        self.timeout_timer.cancel()
        send_all(json.dumps({'type': 'ready', 'sec': -1}))

def start_game():
    print("start game")
    Game()

def end_game():
    print("end game")
    players.clear()
    global game
    if game is not None:
        game.end()
    game = None
    send_all(json.dumps({'type': 'gameover'}))

class User:
    def __init__(self, sock):
        self.sock = sock
        self.id = str(uuid.uuid4())
        self.name = "Guest" + self.id[-4:]

    async def handle(self, msg):
        try:
            msg = json.loads(msg)
        except:
            return

        if msg['type'] == 'newname':
            self.name = msg['newname']
            await refresh_userlist();
            await refresh_playerlist();

        if msg['type'] == 'joingame':
            players.add(self)
            self.progress = 0
            self.rank = -1
            self.finished = False
            self.finish_time = time.time()
            await refresh_playerlist();

            if game is None:
                start_game()

        if msg['type'] == 'leavegame':
            await self.leave_game()

        if msg['type'] == 'progress':
            if game is not None and self in players and not self.finished:
                self.progress = msg['chars']
                self.finish_time = time.time()
                if self.progress == len(game.text):
                    self.rank = game.lastrank + 1
                    game.lastrank += 1
                    self.finished = True
                await refresh_playerlist()

                if self.progress == len(game.text):
                    if all([p.finished for p in players]):
                        end_game()

    async def leave_game(self):
        if self in players:
            players.remove(self)
        await refresh_playerlist();

        if len(players) == 0:
            end_game()

async def refresh_playerlist():
    if game is not None and game.started:
        l = {'type': 'playerlist',
             'playerlist': [
                 {'id': u.id, 'name': u.name, 'progress': u.progress,
                  'wpm': u.progress / 3.0
                      / (u.finish_time - game.start_time) * 60.0,
                  'rank': u.rank}
                 for u in players]}
    else:
        l = {'type': 'playerlist',
             'playerlist': [
                 {'id': u.id, 'name': u.name, 'progress': u.progress,
                  'wpm': 0, 'rank': -1}
                 for u in players]}
    send_all(json.dumps(l))

async def refresh_userlist():
    l = {'type': 'userlist',
         'userlist': [{'id': u.id, 'name': u.name} for u in connected]}
    send_all(json.dumps(l))

async def hello(websocket, path):
    user = User(websocket)
    await websocket.send(json.dumps({"type": "yourid", 'yourid': user.id}))
    connected.add(user)
    await refresh_userlist()
    await refresh_playerlist()

    while True:
        try:
            msg = await websocket.recv()
        except:
            break

        await user.handle(msg)

    print(f"{user.name} disconnected")

    connected.remove(user)
    await user.leave_game()

#ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
#ssl_context.load_cert_chain(input('cert file: '))
start_server = websockets.serve(hello, input('hostname: '), 8765)

random.seed()
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

