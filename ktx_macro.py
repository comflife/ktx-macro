#!/usr/bin/env python3
"""
KTX Macro - 지정 시간대 자동 검색 및 예약 스크립트

문제 발생 시 k-skill의 ktx_booking.py를 참고하여 anti-bot 패치를 적용하세요.
"""

import os
import time
import argparse
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from korail2 import Korail, TrainType
except ImportError:
    logger.error("korail2가 설치되어 있지 않습니다. pip install korail2")
    raise

KORAIL_ID = os.getenv("KORAIL_ID")
KORAIL_PW = os.getenv("KORAIL_PW")

if not KORAIL_ID or not KORAIL_PW:
    raise ValueError("KORAIL_ID 와 KORAIL_PW 환경변수를 .env 파일에 설정해주세요.")


def parse_time(t: str) -> str:
    """HHMMSS or HH:MM 형식을 HHMMSS로 정규화"""
    t = t.replace(":", "")
    return t.zfill(6)


def is_time_in_range(dep_time: str, start: str, end: str) -> bool:
    """dep_time (HH:MM or HHMM) 이 start~end 범위 내인지 확인"""
    dep_clean = dep_time.replace(":", "")
    return start <= dep_clean <= end


class KTXMacro:
    def __init__(self):
        self.korail = Korail(KORAIL_ID, KORAIL_PW)
        logger.info("Korail 로그인 성공")

    def search_trains(self, date: str, dep: str, arr: str, start_time: str, end_time: str):
        """ 시간대 내 예약 가능 열차 검색 """
        start = parse_time(start_time)
        end = parse_time(end_time)

        try:
            # TrainType.KTX 사용 (KTX 전용)
            trains = self.korail.search_train(
                dep=dep,
                arr=arr,
                date=date,
                train_type=TrainType.KTX
            )
        except Exception as e:
            logger.error(f"검색 중 에러: {e}")
            return []

        available = []
        for train in trains:
            # train.dep_time 은 '08:05' 형식이라 가정
            if hasattr(train, 'dep_time') and is_time_in_range(train.dep_time, start, end):
                # 좌석 있는지 검색 (방법은 korail2 버전에 따라 다름)
                if self._has_available_seat(train):
                    available.append(train)
                    logger.info(f"가능 열차 발견: {train.train_no} | {train.dep_time} ~ {getattr(train, 'arr_time', '')}")

        return available

    def _has_available_seat(self, train) -> bool:
        """ 좌석 있는지 간단 확인 (korail2 버전에 따라 조정 필요) """
        # 대부분의 구현에서는 train.seat_available() 또는 유사 메서드 존재
        if hasattr(train, 'seat_available'):
            return train.seat_available()
        # 백업: 문자열 표현에 '예약가능' 혹은 '잔여'가 있는지
        train_str = str(train)
        return '예약가능' in train_str or '잔여' in train_str or 'available' in train_str.lower()

    def try_reserve(self, train):
        """ 예약 시도 """
        try:
            # ReserveOption 사용 가능 (GENERAL_FIRST 등)
            reservation = self.korail.reserve(train)
            logger.info(f"예약 성공! 예약번호: {getattr(reservation, 'rsv_id', 'N/A')}")
            return reservation
        except Exception as e:
            logger.error(f"예약 실패: {e}")
            return None

    def run(self, date: str, dep: str, arr: str, start_time: str, end_time: str, interval: int = 8, max_attempts: int = 500):
        logger.info(f"KTX 매크로 시작: {date} {dep} -> {arr} ({start_time} ~ {end_time})")
        logger.info(f"검색 간격: {interval}초 | 최대 시도: {max_attempts}회")

        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            logger.info(f"[{attempt}/{max_attempts}] 검색 중...")

            available_trains = self.search_trains(date, dep, arr, start_time, end_time)

            if available_trains:
                target = available_trains[0]  # 첫 번째 가능 열차 선택 (필요시 추후 좌석 선택 로직 추가)
                logger.info(f"예약 시도 중: {target}")

                result = self.try_reserve(target)
                if result:
                    logger.info("성공적으로 예약 완료!")
                    # TODO: Telegram, 사운드 알림 등 추가
                    return result

            time.sleep(interval)

        logger.warning("최대 시도 횟수 도달. 종료")
        return None


def main():
    parser = argparse.ArgumentParser(description="KTX 시간대 자동 예약 매크로")
    parser.add_argument("--date", required=True, help="예약 날짜 (YYYYMMDD, 예: 20260710)")
    parser.add_argument("--dep", required=True, help="출발역 (예: 서울)")
    parser.add_argument("--arr", required=True, help="도착역 (예: 부산)")
    parser.add_argument("--start-time", default="080000", help="시작 시간 (HHMMSS or HH:MM)")
    parser.add_argument("--end-time", default="235959", help="종료 시간 (HHMMSS or HH:MM)")
    parser.add_argument("--interval", type=int, default=8, help="검색 간격 (초)")
    parser.add_argument("--max-attempts", type=int, default=1000, help="최대 시도 횟수")

    args = parser.parse_args()

    macro = KTXMacro()
    macro.run(
        date=args.date,
        dep=args.dep,
        arr=args.arr,
        start_time=args.start_time,
        end_time=args.end_time,
        interval=args.interval,
        max_attempts=args.max_attempts
    )


if __name__ == "__main__":
    main()
