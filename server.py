import asyncio
import websockets
import json
import uuid
import time
import random
import ssl
import pathlib

connected = set()
players = set()
game = None

def send_all(msg):
    for user in connected:
        asyncio.ensure_future(user.sock.send(msg))

texts = [
    "닭 쫒던 개 지붕 쳐다보듯 한다.",
    "키스의 고유 조건은 입술끼리 만나야 하고 특별한 기술은 필요치 않다.",
    "올림픽을 겨냥한 마스코트 수호랑 반다비 책자는 유용한 것으로 판명됐다.",
    "케이크를 좋아하는 건 푹신한 촉감과 단 맛이 혀를 타고 부유하듯 교차하기 때문이야.",
    "장난꾸러기 달팽이녀석 구름타고 바람슝슝 치키치키챠카챠카쵸코쵸코쵸 하늘을 난다.",
    "여자와 남자가 성인 축하를 하는 방법엔 포도향 콘돔과 샤넬 토드백으로 분류되어지죠.",
    "7000만년 전 백악기에는 티라노, 트리케라톱스 및 파키케팔로사우루스 등 다양한 종류의 공룡이 살았었다.",
    "카스테라는 따듯한 우유와 곁들여야 촉촉하고 풍부한 질감을 느낄 수 있죠.",
    "아침은 유리잔에 크림파스타, 점심은 야끼교자, 저녁은 발바닥에 해물리조또.",
    "모든 여성분 음료는 야자유 아메리카노로 통일하여 수천회 리필 가능합니다.",
    "한컴 타자연습 (옛 이름: 한/글 타자연습, 한글과컴퓨터 타자 연습)은 한글과컴퓨터에서 개발한 타자 연습 프로그램으로, 자리 연습, 낱말 연습, 짧은 글 연습, 긴 글 연습, 타자 놀이 등을 제공한다.",
    "대한민국에서는 세종대왕이 훈민정음을 반포한 날인 10월 9일을 한글날로 정하여 태극기를 게양하며, 조선민주주의인민공화국에서는 세종대왕이 훈민정음을 창제한 날인 1월 15일을 조선글날로 정하고 있다.",
    "창어 4호는 중국의 달 탐사선이다. 2019년 1월 3일 세계 최초로 달 뒷면에 착륙하였으며 여러가지 실험을 진행한다.",
    "2006년 12월 4일, NASA의 더그 쿠크(Doug Cooke)는 달 남극 근처 아이트켄 분지(Aitken Basin)에 루나 아웃포스트를 설치할 계획이라고 발표했다.",
    "달력은 1년을 날짜별로 달, 날, 요일, 기념일, 공휴일 등을 표기한 책자 형태의 물건이다. 책력은 1년의 시령과 그 날짜를 기록한 문서를 말한다.",
    "일본에서는 스테이플러를 '호치키스'라고 부르기도 하는데, 이는 일본에서 처음 수입한 스테이플러가 E.H.Hotchkiss 사에서 제작한 것이기 때문이다. 대한민국에서도 스테이플러를 호치키스로 부르기도 한다.",
    "중세 이후 프랑스와 영국은 유럽대륙의 주도권 및 식민지 쟁탈을 놓고 서로 적대국인 경우가 많았으나 때로는 동맹을 맺기도 하였다.",
    "낭트(프랑스어: Nantes)는 프랑스 본토 브르타뉴 지방에 위치한 도시이다. 페이드라루아르 레지옹의 중심지이며, 루아르아틀랑티크 주의 주도이기도 하다. 프랑스에서 6번째로 큰 도시이다.",
    "남조선국방경비대는 대한민국 국군의 전신으로서 1946년 1월 15일에 미군정이 1개 연대 병력으로 창설하였다. 이 날은 대한민국 육군의 창설 기념일이기도 하다.",
    "마하 수(Mach number)란 음속에 비하여 속도가 얼마나 되는지를 나타내는 수이다. 오스트리아의 과학자 에른스트 마하(Ernst Mach)의 이름을 따 명명되었다.",
    "1<M<5의 영역에서는 물체의 앞에서 공기의 압력과 밀도가 급격히 변화하는 지점이 발생하는데 이것을 충격파라고 부른다.",
    "국어기본법 제20조 (한글날) (1) 정부는 한글의 독창성과 과학성을 국내외에 널리 알리고 범국민적 한글 사랑 의식을 높이기 위하여 매년 10월 9일을 한글날로 정하고, 기념행사를 한다.",
    "부마민주항쟁 또는 부마민중항쟁은 1979년 10월 16일부터 10월 20일까지 대한민국의 부산광역시와 경상남도 마산시(현 창원시)에서 유신 체제에 대항한 항쟁을 말한다.",
    "거리에 가로등불이 하나 둘씩 켜지고 검붉은 노을너머 또 하루가 저물 땐 왠지 모든 것이 꿈결같아요 유리에 비친 내 모습은 무얼 찾고 있는지 뭐라 말하려해도 기억하려 하여도",
    "그리운 그대 아름다운 모습으로 마치 아무 일도 없던 것처럼 내가 알지 못하는 머나먼 그곳으로 떠나버린 후 사랑의 슬픈 추억은 소리없이 흩어져",
    "이젠 그대 모습도 함께 나눈 사랑도 더딘 시간 속에 잊혀져 가요 거리에 짙은 어둠이 낙엽처럼 쌓이고",
    "니가 없는 거리에는 내가 할 일이 없어서 마냥 걷다 걷다보면 추억을 가끔 마주치지",
    "학퍈턷켤쵬즈유수뵤",
    "주요 도시로는 모스크바, 상트페테르부르크, 이르쿠츠크, 노보시비르스크, 블라디보스토크, 크라스노야르스크, 소치 등이 있다.",
    "옐친 대통령은 1991년 11월 러시아 최고회의가 부여한 비상대권을 1년간 유지하면서 지속적인 시장경제 정책을 추구했으나 성과를 거두지 못하고 경제가 악화됐다.",
    "삼림대는 러시아 국토의 약 30%를 차지하는 광대한 지역으로서, 이는 북부의 침엽수림대와 남부의 활엽수가 섞인 혼합림대로 나눈다.",
    "소비에트 연방의 붕괴 후 출생률과 평균 수명이 줄어들어 1993년부터 인구가 감소하기 시작했고 2008년까지 15년 동안 러시아의 인구는 660만 명이 감소했다.",
    "아돌프 히틀러는 자신의 자서전인 나의 투쟁에서, 독일의 동유럽 정착을 위한 새로운 영토 확장인 레벤스라움을 주장했다.",
    "어미에 따라 드러나는 복잡한 존비어 체계가 특징적으로, 화자 간에 존댓말(높임말)과 반말(낮춤말, 평어)에 대한 합의가 명확하게 이루어지지 않은 상태에서는 의사소통에 있어서 어색한 상황이 발생한다.",
    "국립국제교육원이 주최하고 교육과학기술부가 인정하는 자격시험으로 매년 4월과 9월에 시행된다. (한국에서는 2007년부터 일본에서는 2008년부터 연 2회 볼 수 있게 되었다)",
    "tvN에서 2015년 11월 6일부터 2016년 1월 16일까지 방영한 드라마로, 응답하라 시리즈의 세 번째 작품이며, 연출자는 전작과 같은 신원호 PD.",
    "온 가족이 도란도란 모여 앉아 보던 '한 지붕 세 가족', 앞집, 옆집, 뒷집 너나없이 나누고 살았던 골목 이웃들을 기억한다.",
    "또한, 전작들에 비해 OST들의 약진도 주목할 만한데, 오혁의 <소녀>나 이적의 <걱정말아요 그대> 등이 주요 음원 차트를 휩쓸었다.",
    "조선민주주의인민공화국의 정치구조는 초기에 남로당 계열, 갑산파 계열, 소련파 계열, 연안파 계열 등으로 이루어진 연립내각 체제였다.",
    "Can ~는/은 and ~이/가 be used interchangeably in sentences?",
    "그래서 tvN측에서는 다음 촬영 시에는 관광 용도 활용을 고려해서 세트장을 설치하겠다고 밝혔다.",
    "막다른길 다다라서 낯익은 벽 기대보며 가로등 속"
]

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
            await asyncio.sleep(60)
            self.end()
        selft.timeout_timer = asyncio.ensure_future(timeout())

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

