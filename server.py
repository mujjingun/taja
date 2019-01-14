import asyncio
import websockets
import json
import uuid

connected = set()
players = set()
game = None

class Game:
    def __init__(self):
        self.text = "닭 쫒던 개 지붕 쳐다보듯 한다"
        self.started = False
        def timer(sec):
            print(sec)
            asyncio.get_event_loop().call_later(1, timer, sec - 1)
        timer(10)

class User:
    def __init__(self, sock):
        self.sock = sock
        self.id = str(uuid.uuid4())
        self.name = "Guest"

    async def handle(self, msg):
        try:
            msg = json.loads(msg)
        except:
            return
        
        if msg['type'] == 'newname':
            self.name = msg['newname']
            await refresh_userlist();
            
        if msg['type'] == 'joingame':
            if game is None:
                game = Game()
            elif not game.started:
                players.add(self)
                await refresh_playerlist();
            
        if msg['type'] == 'leavegame':
            players.remove(self)
            await refresh_playerlist();

async def refresh_playerlist():
    l = {'type': 'playerlist',
         'playerlist': [{'id': u.id, 'name': u.name} for u in players]}
    msg = json.dumps(l)
    for user in connected:
        await user.sock.send(msg)

async def refresh_userlist():
    l = {'type': 'userlist',
         'userlist': [{'id': u.id, 'name': u.name} for u in connected]}
    msg = json.dumps(l)
    for user in connected:
        await user.sock.send(msg)

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
    if user in players:
        players.remove(user)
    await refresh_userlist()
    
start_server = websockets.serve(hello, 'localhost', 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

