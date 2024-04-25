import _thread
import binascii
import gzip
import json
import os
import signal
# from config import LIVE_GIFT_LIST
# from src.utils.logger import logger
import re
import time
import requests
import websocket
# from src.utils.ws_send import ws_sender
# from src import live_rank
# from src.utils.common import GlobalVal
from protobuf_inspector.types import StandardParser
from google.protobuf import json_format
from douyin_proto.douyin_pb2 import PushFrame
from douyin_proto.douyin_pb2 import Response
from douyin_proto.douyin_pb2 import MatchAgainstScoreMessage
from douyin_proto.douyin_pb2 import LikeMessage
from douyin_proto.douyin_pb2 import MemberMessage
from douyin_proto.douyin_pb2 import GiftMessage
from douyin_proto.douyin_pb2 import ChatMessage
from douyin_proto.douyin_pb2 import SocialMessage
from douyin_proto.douyin_pb2 import RoomUserSeqMessage
from douyin_proto.douyin_pb2 import UpdateFanTicketMessage
from douyin_proto.douyin_pb2 import CommonTextMessage
from douyin_proto.douyin_pb2 import ProductChangeMessage
import send2unity

# 直播信息全局变量
liveRoomId = ""
ttwid = ""
roomStore = ""
liveRoomTitle = ''
live_stream_url = ""
# 记录抓取直播时间
start_time = time.time()


from config import SEND_URL
def sender_msg(payload):
    print(f"推送直播消息:", {"msg":payload})
    send2unity.add_pending_msg(payload)
    # response = requests.request("POST", SEND_URL, headers=headers, data={"msg":payload})


def onMessage(ws: websocket.WebSocketApp, message: bytes):
    wssPackage = PushFrame()
    wssPackage.ParseFromString(message)
    logId = wssPackage.logId
    # 使用gzip压缩
    decompressed = gzip.decompress(wssPackage.payload)
    payloadPackage = Response()
    payloadPackage.ParseFromString(decompressed)
    # 发送ack包
    if payloadPackage.needAck:
        sendAck(ws, logId, payloadPackage.internalExt)

    messages = []
    for msg in payloadPackage.messagesList:
        messages.append({"method":msg.method, "payload": msg.payload})

        # 反对分数消息
        if msg.method == 'WebcastMatchAgainstScoreMessage':
            unPackMatchAgainstScoreMessage(msg.payload)
            continue

        # 点赞数
        if msg.method == 'WebcastLikeMessage':
            unPackWebcastLikeMessage(msg.payload)
            continue

        # 成员进入直播间消息
        if msg.method == 'WebcastMemberMessage':
            unPackWebcastMemberMessage(msg.payload)
            continue

        # 礼物消息
        if msg.method == 'WebcastGiftMessage':
            unPackWebcastGiftMessage(msg.payload)
            continue

        # 聊天消息
        if msg.method == 'WebcastChatMessage':
            unPackWebcastChatMessage(msg.payload)
            continue

        # 联谊会消息
        if msg.method == 'WebcastSocialMessage':
            unPackWebcastSocialMessage(msg.payload)
            continue

        # 房间用户发送消息
        if msg.method == 'WebcastRoomUserSeqMessage':
            unPackWebcastRoomUserSeqMessage(msg.payload)
            continue

        # 更新粉丝票
        if msg.method == 'WebcastUpdateFanTicketMessage':
            unPackWebcastUpdateFanTicketMessage(msg.payload)
            continue

        # 公共文本消息
        if msg.method == 'WebcastCommonTextMessage':
            unPackWebcastCommonTextMessage(msg.payload)
            continue

        # 商品改变消息
        if msg.method == 'WebcastProductChangeMessage':
            WebcastProductChangeMessage(msg.payload)
            continue
        # print("未处理信息", msg.method)

def unPackWebcastCommonTextMessage(data):
    commonTextMessage = CommonTextMessage()
    commonTextMessage.ParseFromString(data)
    data = json_format.MessageToDict(commonTextMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    return data


def WebcastProductChangeMessage(data):
    commonTextMessage = ProductChangeMessage()
    commonTextMessage.ParseFromString(data)
    data = json_format.MessageToDict(commonTextMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)


def unPackWebcastUpdateFanTicketMessage(data):
    updateFanTicketMessage = UpdateFanTicketMessage()
    updateFanTicketMessage.ParseFromString(data)
    data = json_format.MessageToDict(updateFanTicketMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    return data


def unPackWebcastRoomUserSeqMessage(data):
    roomUserSeqMessage = RoomUserSeqMessage()
    roomUserSeqMessage.ParseFromString(data)
    data = json_format.MessageToDict(roomUserSeqMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    # sender_msg(log)
    return data


def unPackWebcastSocialMessage(data):
    socialMessage = SocialMessage()
    socialMessage.ParseFromString(data)
    data = json_format.MessageToDict(socialMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    sender_msg('[关注]{}：关注了主播'.format(data["user"]["nickName"]))
    return data


# 普通消息
def unPackWebcastChatMessage(data):
    chatMessage = ChatMessage()
    chatMessage.ParseFromString(data)
    data = json_format.MessageToDict(chatMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    sender_msg('[弹幕]{}：{}'.format(data["user"]["nickName"], data["content"]))
    return data


# 礼物消息
def unPackWebcastGiftMessage(data):
    giftMessage = GiftMessage()
    giftMessage.ParseFromString(data)
    data = json_format.MessageToDict(giftMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    sender_msg('[礼物]{}'.format(data["common"]["describe"].replace(':','：')))
    return data


# xx成员进入直播间消息
def unPackWebcastMemberMessage(data):
    global member_num
    memberMessage = MemberMessage()
    memberMessage.ParseFromString(data)
    data = json_format.MessageToDict(memberMessage, preserving_proto_field_name=True)
    # 直播间人数统计
    member_num = int(data.get("memberCount", 0))
    log = json.dumps(data, ensure_ascii=False)
    sender_msg('[进入]{}：来了'.format(data["user"]["nickName"]))
    
    return data


# 点赞
def unPackWebcastLikeMessage(data):
    likeMessage = LikeMessage()
    likeMessage.ParseFromString(data)
    data = json_format.MessageToDict(likeMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    sender_msg('[点赞]{}：为主播点赞了'.format(data["user"]["nickName"]))
    
    return data

def unPackMatchAgainstScoreMessage(data):
    matchAgainstScoreMessage = MatchAgainstScoreMessage()
    matchAgainstScoreMessage.ParseFromString(data)
    data = json_format.MessageToDict(matchAgainstScoreMessage, preserving_proto_field_name=True)
    log = json.dumps(data, ensure_ascii=False)
    return data

def sendAck(ws, logId, internalExt):
    obj = PushFrame()
    obj.payloadType = 'ack'
    obj.logId = logId
    obj.payloadType = internalExt
    data = obj.SerializeToString()
    # 回复 ACK
    ws.send(data, websocket.ABNF.OPCODE_BINARY)

def onError(ws, error):
    print(ws, error)

def onClose(ws, a, b):
    pid = os.getpid() 
    os.kill(pid, signal.SIGTERM)


def onOpen(ws):
    _thread.start_new_thread(ping, (ws,))

# 发送ping心跳包
def ping(ws):
    while True:
        obj = PushFrame()
        obj.payloadType = 'hb'
        data = obj.SerializeToString()
        # 心跳包
        ws.send(data, websocket.ABNF.OPCODE_BINARY)
        time.sleep(10)


def wssServerStart():
    websocket.enableTrace(False)
    webSocketUrl = 'wss://webcast3-ws-web-lq.douyin.com/webcast/im/push/v2/?app_name=douyin_web&version_code=180800&webcast_sdk_version=1.3.0&update_version_code=1.3.0&compress=gzip&internal_ext=internal_src:dim|wss_push_room_id:' + liveRoomId + '|wss_push_did:7188358506633528844|dim_log_id:20230521093022204E5B327EF20D5CDFC6|fetch_time:1684632622323|seq:1|wss_info:0-1684632622323-0-0|wrds_kvs:WebcastRoomRankMessage-1684632106402346965_WebcastRoomStatsMessage-1684632616357153318&cursor=t-1684632622323_r-1_d-1_u-1_h-1&host=https://live.douyin.com&aid=6383&live_id=1&did_rule=3&debug=false&maxCacheMessageNumber=20&endpoint=live_pc&support_wrds=1&im_path=/webcast/im/fetch/&user_unique_id=7188358506633528844&device_platform=web&cookie_enabled=true&screen_width=1440&screen_height=900&browser_language=zh&browser_platform=MacIntel&browser_name=Mozilla&browser_version=5.0%20(Macintosh;%20Intel%20Mac%20OS%20X%2010_15_7)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/113.0.0.0%20Safari/537.36&browser_online=true&tz_name=Asia/Shanghai&identity=audience&room_id=' + liveRoomId + '&heartbeatDuration=0&signature=00000000'
    h = {
        'cookie': 'ttwid=' + ttwid,
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    ws = websocket.WebSocketApp(
        webSocketUrl, on_message=onMessage, on_error=onError, on_close=onClose,
        on_open=onOpen,
        header=h
    )
    ws.run_forever()


def start_live(url):
    headers = {
        'authority': 'live.douyin.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'max-age=0',
        'cookie': 'xgplayer_user_id=251959789708; passport_assist_user=Cj1YUtyK7x-Br11SPK-ckKl61u5KX_SherEuuGPYIkLjtmV3X8m3EU1BAGVoO541Sp_jwUa8lBlNmbaOQqheGkoKPOVVH42rXu6KEb9WR85pUw4_qNHfbcotEO-cml5itrJowMBlYXDaB-GDqJwNMxMElMoZUycGhzdNVAT4XxCJ_74NGImv1lQgASIBA3Iymus%3D; n_mh=nNwOatDm453msvu0tqEj4bZm3NsIprwo6zSkIjLfICk; LOGIN_STATUS=1; store-region=cn-sh; store-region-src=uid; sid_guard=b177a545374483168432b16b963f04d5%7C1697713285%7C5183999%7CMon%2C+18-Dec-2023+11%3A01%3A24+GMT; ttwid=1%7C9SEGPfK9oK2Ku60vf6jyt7h6JWbBu4N_-kwQdU-SPd8%7C1697721607%7Cc406088cffa073546db29932058720720521571b92ba67ba902a70e5aaffd5d6; odin_tt=1f738575cbcd5084c21c7172736e90f845037328a006beefec4260bf8257290e2d31b437856575c6caeccf88af429213; __live_version__=%221.1.1.6725%22; device_web_cpu_core=16; device_web_memory_size=8; live_use_vvc=%22false%22; csrf_session_id=38b68b1e672a92baa9dcb4d6fd1c5325; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; __ac_nonce=0658d6780004b23f5d0a8; __ac_signature=_02B4Z6wo00f01Klw1CQAAIDAXxndAbr7OHypUNCAAE.WSwYKFjGSE9AfNTumbVmy1cCS8zqYTadqTl8vHoAv7RMb8THl082YemGIElJtZYhmiH-NnOx53mVMRC7MM8xuavIXc-9rE7ZEgXaA13; webcast_leading_last_show_time=1703765888956; webcast_leading_total_show_times=1; webcast_local_quality=sd; xg_device_score=7.90435294117647; live_can_add_dy_2_desktop=%221%22; msToken=sTwrsWOpxsxXsirEl0V0d0hkbGLze4faRtqNZrIZIuY8GYgo2J9a0RcrN7r_l179C9AQHmmloI94oDvV8_owiAg6zHueq7lX6TgbKBN6OZnyfvZ6OJyo2SQYawIB_g==; tt_scid=NyxJTt.vWxv79efmWAzT2ZAiLSuybiEOWF0wiVYs5KngMuBf8oz5sqzpg5XoSPmie930; pwa2=%220%7C0%7C1%7C0%22; download_guide=%223%2F20231228%2F0%22; msToken=of81bsT85wrbQ9nVOK3WZqQwwku95KW-wLfjFZOef2Orr8PRQVte27t6Mkc_9c_ROePolK97lKVG3IL5xrW6GY6mdUDB0EcBPfnm8-OAShXzlELOxBBCdiQYIjCGpQ==; IsDouyinActive=false; odin_tt=7409a7607c84ba28f27c62495a206c66926666f2bbf038c847b27817acbdbff28c3cf5930de4681d3cfd4c1139dd557e; ttwid=1%7C9SEGPfK9oK2Ku60vf6jyt7h6JWbBu4N_-kwQdU-SPd8%7C1697721607%7Cc406088cffa073546db29932058720720521571b92ba67ba902a70e5aaffd5d6',
        'referer': 'https://live.douyin.com/721566130345?cover_type=&enter_from_merge=web_live&enter_method=web_card&game_name=&is_recommend=&live_type=game&more_detail=&room_id=7317569386624125734&stream_type=vertical&title_type=&web_live_tab=all',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
    }
    res = requests.get(url=url, headers=headers)
    global ttwid, roomStore, liveRoomId, liveRoomTitle, live_stream_url
    data = res.cookies.get_dict()
    ttwid = data['ttwid']
    res = res.text
    res_room_info = re.search(r'room\\":{.*\\"id_str\\":\\"(\d+)\\".*,\\"status\\":(\d+).*"title\\":\\"([^"]*)\\"', res)
    if res_room_info:
        room_status = res_room_info.group(2)
        room_title = res_room_info.group(3)
        liveRoomTitle = room_title
        if room_status == '4':
            raise ConnectionError("直播已结束")
    res_room = re.search(r'roomId\\":\\"(\d+)\\"', res)
    live_room_search = re.search(r'owner\\":(.*?),\\"room_auth', res)
    live_room_res = live_room_search.group(1).replace('\\"', '"')
    live_room_info = json.loads(live_room_res)
    print(f"拉取主播账号: {live_room_info}")
    # 直播间id
    liveRoomId = res_room.group(1)
    
    send2unity.start_send_unity()
    wssServerStart()
