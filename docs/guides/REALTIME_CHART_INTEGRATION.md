# WebSocket 실시간 분봉 차트 통합 완료

## ✅ 완료된 작업

### 1. 백엔드: 실시간 분봉 생성기 (`core/realtime_minute_chart.py`)

**주요 기능:**
- WebSocket 체결 데이터(0B)를 1분 단위로 집계하여 OHLCV 생성
- 장중 시간(09:00-15:30)만 데이터 수집
- 최대 390개 분봉 저장 (1 영업일치)
- 여러 종목 동시 관리 가능

**클래스 구조:**
```python
MinuteCandle              # 1분봉 데이터 저장
RealtimeMinuteChart       # 단일 종목 실시간 분봉 생성
RealtimeMinuteChartManager # 여러 종목 관리
```

### 2. 프론트엔드: 대시보드 통합 (`dashboard/app_apple.py`)

**변경사항:**

#### 초기화
- `run_dashboard()` 함수에서 `RealtimeMinuteChartManager` 자동 초기화
- WebSocket 연결 상태 확인 후 초기화
- 초기화 성공/실패 메시지 출력

#### 차트 API 엔드포인트 수정 (`/api/chart/<stock_code>`)
**데이터 우선순위:**
1. **실시간 WebSocket 데이터** (장중 + 데이터 있을 때)
2. **REST API 분봉 데이터** (실시간 없을 때 시도)
3. **일봉 데이터** (분봉 사용 불가 시)

**자동 구독 기능:**
- 대시보드에서 차트 요청 시 해당 종목이 실시간 트래킹 중이 아니면 자동으로 추가
- 이후 체결 데이터가 들어오면서 분봉 생성

#### 새 API 엔드포인트 3개

**1. 종목 추가 (POST)**
```bash
curl -X POST http://localhost:5000/api/realtime_chart/add/005930
```
응답:
```json
{
  "success": true,
  "message": "성공적으로 추가됨: 005930"
}
```

**2. 종목 제거 (POST)**
```bash
curl -X POST http://localhost:5000/api/realtime_chart/remove/005930
```
응답:
```json
{
  "success": true,
  "message": "제거됨: 005930"
}
```

**3. 상태 조회 (GET)**
```bash
curl http://localhost:5000/api/realtime_chart/status
```
응답:
```json
{
  "success": true,
  "status": {
    "connected": true,
    "stocks": {
      "005930": {
        "subscribed": true,
        "candle_count": 145,
        "current_minute": "14:23"
      },
      "035720": {
        "subscribed": true,
        "candle_count": 87,
        "current_minute": "14:23"
      }
    }
  }
}
```

### 3. 스코어링 시스템 임계값 하드코딩 (`strategy/scoring_system.py`)

**문제:** ConfigManager 싱글톤 캐싱으로 인해 config.yaml 값이 로드되지 않음

**해결:** config.get() 호출을 완전히 제거하고 직접 하드코딩

**변경된 라인:**
- Line 299: `min_ratio = 0.8  # 강제 하드코딩: config 무시`
- Line 339: `min_value = 50  # 강제 하드코딩: config 무시`
- Line 409: `min_net_buy = 100_000  # 강제 하드코딩: config 무시`

**디버그 로그 확인:**
```
[DEBUG 체결강도] XXX: min_value=50 (하드코딩)
[DEBUG 프로그램] XXX: min_net_buy=100000 (하드코딩)
```

---

## 🚀 사용 방법

### 장중 실시간 분봉 사용

**1. 프로그램 재시작 (필수!)**
```bash
# main.py 완전 종료 (Ctrl+C)
python main.py
```

**2. 대시보드 재시작**
```bash
# dashboard 완전 종료 (Ctrl+C)
python dashboard/app_apple.py
```

**3. 대시보드 로그 확인**
시작 시 다음 메시지가 표시되어야 합니다:
```
✅ Real-time minute chart manager initialized
```

만약 다음 메시지가 보이면 WebSocket이 초기화되지 않은 것입니다:
```
⚠️ WebSocket manager not available, real-time minute charts disabled
```

**4. 대시보드에서 차트 보기**
- 종목 선택
- 차트 타임프레임에서 1분/5분/10분/60분 선택
- 자동으로 실시간 트래킹 시작
- 장중이면 실시간 분봉 표시, 장외이면 일봉으로 폴백

**5. 콘솔 로그 확인**
대시보드 터미널에서 다음과 같은 로그를 볼 수 있습니다:
```
📊 Attempting to fetch 1-minute data
📡 Adding 005930 to real-time tracking...
✅ 005930 added to real-time tracking
✅ Using real-time minute data (87 candles)
```

또는 장외 시간:
```
📊 Attempting to fetch 1-minute data
📊 Trying REST API minute data...
⚠️ 1-minute data not available (likely weekend/holiday), falling back to daily data
```

---

## 📊 동작 흐름

### 장중 (09:00-15:30)

```
사용자가 대시보드에서 분봉 차트 요청
    ↓
실시간 분봉 데이터 있는지 확인
    ↓
[없음] → WebSocket 자동 구독
    ↓
체결 데이터 수신 시작 (0B)
    ↓
1분 단위로 OHLCV 집계
    ↓
차트 API가 실시간 데이터 반환
    ↓
대시보드에 실시간 분봉 표시
```

### 장외 시간

```
사용자가 대시보드에서 분봉 차트 요청
    ↓
실시간 분봉 데이터 없음
    ↓
REST API 분봉 시도 → 빈 배열 반환
    ↓
자동으로 일봉으로 폴백
    ↓
대시보드에 일봉 표시
```

---

## 🧪 테스트 방법

### 1. WebSocket 연결 확인
```bash
# main.py 로그에서 확인
INFO:core.websocket_manager:✅ WebSocket 연결 성공
```

### 2. 실시간 분봉 생성 확인
```bash
# main.py 로그에서 확인 (장중에만)
DEBUG:core.realtime_minute_chart:새 분봉 생성: 14:23 (총 87개)
```

### 3. 대시보드 API 테스트
```bash
# 상태 확인
curl http://localhost:5000/api/realtime_chart/status

# 수동으로 종목 추가
curl -X POST http://localhost:5000/api/realtime_chart/add/035720

# 다시 상태 확인
curl http://localhost:5000/api/realtime_chart/status
```

### 4. 브라우저에서 확인
1. 대시보드 접속: http://localhost:5000
2. 종목 선택 (예: 삼성전자)
3. 타임프레임에서 "1분" 선택
4. 차트가 표시되는지 확인
5. 콘솔 로그에서 "Using real-time minute data" 메시지 확인

---

## 🔧 트러블슈팅

### 문제 1: "Real-time chart manager not initialized"

**원인:** WebSocketManager가 초기화되지 않음

**해결:**
```bash
# main.py에서 WebSocket이 정상적으로 시작되는지 확인
grep "WebSocket" logs/bot.log

# WebSocket 설정 확인
cat config/config.yaml | grep -A5 "websocket:"
```

### 문제 2: 실시간 데이터가 수집되지 않음

**원인:** 장외 시간이거나 WebSocket 구독 실패

**해결:**
1. 시간 확인: 09:00-15:30 사이여야 함
2. WebSocket 로그 확인:
```bash
tail -f logs/bot.log | grep "0B"  # 체결 데이터 수신 확인
```

### 문제 3: 스코어링 여전히 0점

**원인:** main.py가 재시작되지 않아 예전 코드 사용 중

**해결:**
```bash
# main.py 완전 종료 후 재시작
ps aux | grep "python main.py"
kill -9 <PID>
python main.py

# 디버그 로그 확인
tail -f logs/bot.log | grep "하드코딩"
```

예상 출력:
```
[DEBUG 체결강도] 005930: min_value=50 (하드코딩)
[DEBUG 프로그램] 005930: min_net_buy=100000 (하드코딩)
```

### 문제 4: 차트에서 "데이터 변환 실패"

**원인:** 실시간 데이터도 없고, REST API도 빈 배열 반환 (정상 동작)

**해결:** 일봉(D)을 선택하거나 장중에 다시 시도

---

## 📈 예상 효과

### 스코어링 개선 (하드코딩 적용 후)
```
이전:
체결:0/40    (체결강도 79 < min_value 120)
호가:0/40    (호가비율 0.56 < min_ratio 1.2)
프로그램:0/40 (순매수 2,163 < min_net_buy 5,000,000)

개선 후:
체결:20/40   (체결강도 79 > min_value 50) ✅
호가:10/40   (호가비율 0.56 < min_ratio 0.8, 하지만 부분 점수)
프로그램:20/40 (순매수 2,163 < min_net_buy 100,000, 하지만 더 가까워짐)

총점: 0점 → 50점+ 증가 예상
```

### 실시간 분봉 사용 (장중)
```
이전:
- 분봉 요청 → API 오류 → 빈 데이터
- 사용자가 "데이터 변환 실패" 메시지만 봄

개선 후:
- 분봉 요청 → WebSocket 구독 자동 시작
- 체결 데이터 실시간 집계
- 1분 후부터 분봉 차트 표시
- 최대 390분(6.5시간)치 저장
```

---

## 🎯 다음 단계 (선택 사항)

### 1. 분봉 데이터 DB 저장 (장기)
- SQLite 또는 Redis에 분봉 저장
- 과거 분봉 데이터 축적
- 장외 시간에도 과거 분봉 조회 가능

### 2. 프리마켓/애프터마켓 지원
- 장전/장후 시간대 체결 데이터 수집
- 시간 필터 조정

### 3. 다양한 분봉 지원
- 3분봉, 5분봉, 10분봉 자동 생성
- 현재는 1분봉만 생성 → 다른 타임프레임은 1분봉 집계로 생성

### 4. 대시보드 UI 개선
- 실시간 분봉 상태 표시 (🔴 라이브 / ⏸ 장외)
- 수집된 분봉 개수 표시
- WebSocket 연결 상태 표시

---

## 📝 커밋 이력

1. **fix: 스코어링 임계값을 완전히 하드코딩으로 강제 설정**
   - strategy/scoring_system.py 수정
   - config.get() 호출 제거
   - min_ratio, min_value, min_net_buy 하드코딩

2. **feat: WebSocket 실시간 분봉 생성기 구현**
   - core/realtime_minute_chart.py 추가
   - MinuteCandle, RealtimeMinuteChart, RealtimeMinuteChartManager 클래스

3. **feat: 대시보드에 WebSocket 실시간 분봉 차트 통합**
   - dashboard/app_apple.py 수정
   - RealtimeMinuteChartManager 초기화
   - /api/chart 엔드포인트 수정 (실시간 우선)
   - 3개 새 API 엔드포인트 추가

---

## ✅ 체크리스트

완료 후 다음을 확인하세요:

- [ ] `git pull origin claude/stock-scoring-system-011CUkyJunrH6TZfXB6jRH1o` 실행
- [ ] main.py 완전 재시작
- [ ] 디버그 로그에서 `min_value=50 (하드코딩)` 확인
- [ ] 디버그 로그에서 `min_net_buy=100000 (하드코딩)` 확인
- [ ] 스코어링에서 체결/호가/프로그램 점수 증가 확인
- [ ] 대시보드 재시작
- [ ] "Real-time minute chart manager initialized" 메시지 확인
- [ ] 장중에 분봉 차트 테스트
- [ ] `/api/realtime_chart/status` API 테스트

---

## 🆘 문제 발생 시

1. **로그 확인:**
```bash
tail -f logs/bot.log | grep -E "(하드코딩|WebSocket|분봉)"
```

2. **Git 상태 확인:**
```bash
git status
git log --oneline -5
```

3. **최신 코드로 업데이트:**
```bash
git pull origin claude/stock-scoring-system-011CUkyJunrH6TZfXB6jRH1o
```

4. **전체 로그 캡처 후 보고**
