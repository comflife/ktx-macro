# ktx-macro

KTX 매크로 자동 예매 프로젝트

## 기능
- 지정한 날짜, 출발역, 도착역, 시간대(언제부터 언제까지) 내에서 예약 가능한 KTX 열차를 지속적으로 검색
- 발견 시 자동 예약 시도
- korail2 라이브러리 기반 (API 방식)

## 설치 및 사용 법

### 1. 클론
```bash
git clone https://github.com/comflife/ktx-macro.git
cd ktx-macro
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정
`.env` 파일 생성 또는 환경변수 설정:
```
KORAIL_ID=아이디
KORAIL_PW=비밀번호
```

### 4. 실행
```bash
python ktx_macro.py --date 20260710 --dep 서울 --arr 부산 --start-time 080000 --end-time 120000 --interval 8
```

## 주의사항
- 이 스크립트는 **개인적 용도**로만 사용하세요.
- Korail 서비스 약관(Terms of Service)을 위반할 수 있으니 자체 책임을 집니다.
- Anti-bot 기능이 강화되어 있어 실행 시 에러가 발생할 수 있습니다.
- 최신 우회 기법은 [k-skill 프로젝트](https://github.com/NomaDamas/k-skill)의 `scripts/ktx_booking.py` 를 참고하세요. (Dynapath anti-bot 우회 헤더 패치 포함)
- 결제 까지는 지원하지 않습니다 (예약 까지).

## 참고 프로젝트
- https://github.com/NomaDamas/k-skill (ktx-booking 기능)
- https://github.com/carpedm20/korail2
- 기타 KTX 매크로 프로젝트들

## 로드맵
- 기본 매크로 구현
- Telegram/Discord 알림 기능 추가 계획
- 좌석 선택 (일반실/특실, 호차 지정, 콘센트 좌석) 기능
