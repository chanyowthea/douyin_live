# import logging

from config import ROOM_URL
import douyin_live
if __name__ == '__main__':
    douyin_live.start_live(ROOM_URL)
