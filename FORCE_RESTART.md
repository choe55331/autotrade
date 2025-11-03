# 🚨 강제 재시작 가이드

## 문제 해결 완료

### 1️⃣ Python 캐시 삭제 ✅
- 모든 `__pycache__` 디렉토리 삭제
- 모든 `.pyc` 파일 삭제
- 이제 최신 소스 코드를 사용합니다

### 2️⃣ 장중 시간 수정 ✅
- 기존: 09:00 ~ 15:30 (정규 장만)
- 변경: **08:00 ~ 20:00** (프리마켓/애프터마켓 포함)

### 3️⃣ 하드코딩 확인 ✅
파일 내용:
```python
# strategy/scoring_system.py
min_value = 50  # 강제 하드코딩: config 무시
min_net_buy = 100_000  # 강제 하드코딩: config 무시
```

---

## 🔥 재시작 방법 (필수!)

### 1단계: 모든 프로세스 완전 종료

```bash
# main.py 강제 종료
pkill -9 -f "python.*main.py"

# dashboard 강제 종료
pkill -9 -f "python.*app_apple.py"

# 종료 확인 (아무것도 출력 안되면 OK)
ps aux | grep -E "(main\.py|app_apple\.py)" | grep -v grep
```

### 2단계: Python 캐시 재확인

```bash
# 캐시 디렉토리 확인 (아무것도 출력 안되면 OK)
find . -type d -name "__pycache__" 2>/dev/null

# 혹시 남아있으면 다시 삭제
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
```

### 3단계: main.py 시작

```bash
python main.py
```

**예상 로그 (반드시 확인!):**

✅ **스코어링 하드코딩 적용됨:**
```
[DEBUG 체결강도] 005930: min_value=50 (하드코딩)
[DEBUG 프로그램] 005930: min_net_buy=100000 (하드코딩)
```

✅ **초기 자본금 정상:**
```
💰 초기 자본금: 888,900원 (주문가능: 888,900, 총평가: 0)
```

✅ **리스크 모드 정상:**
```
🛡️ 동적 리스크 관리자 초기화 완료 (초기자본: 888,900원, 모드: normal)
```

❌ **만약 이렇게 나오면 실패:**
```
[DEBUG 체결강도] 005930: min_value=120, config에서 로드=120
```
→ 이 경우 다시 연락주세요!

### 4단계: 대시보드 시작 (별도 터미널)

```bash
python dashboard/app_apple.py
```

**예상 로그:**
```
✅ Real-time minute chart manager initialized
```

---

## 🧪 테스트 방법

### 1. 스코어링 점수 확인

로그에서 다음을 찾아보세요:
```
[DEBUG 체결강도] XXX: execution_intensity=82.7 (type=<class 'float'>)
[DEBUG 체결강도] XXX: min_value=50 (하드코딩)
[DEBUG 체결강도] XXX: 82.7 → 20.0점  ← 0점이 아님!
```

기대 결과:
- 체결강도 50-70: 10점
- 체결강도 70-100: 20점
- 체결강도 100-150: 30점
- 체결강도 150+: 40점

### 2. 프로그램 매매 점수 확인

```
[DEBUG 프로그램] XXX: program_net_buy=2163 (type=<class 'int'>)
[DEBUG 프로그램] XXX: min_net_buy=100000 (하드코딩)
[DEBUG 프로그램] XXX: 2,163원 → 0.0점  ← 이건 정상 (10만원 미만)
```

10만원 이상일 때:
- 10만원-100만원: 10점
- 100만원-300만원: 20점
- 300만원-500만원: 30점
- 500만원+: 40점

### 3. 실시간 분봉 시간 확인

08:00-19:59 사이에는 실시간 분봉 수집됨:
```
DEBUG:core.realtime_minute_chart:새 분봉 생성: 19:45 (총 705개)
```

20:00 이후에는 수집 안됨 (정상):
```
(로그 없음)
```

---

## ❌ 만약 여전히 안되면

### 디버깅 1: 실행 중인 파일 확인

```bash
ps aux | grep python
```

출력에서 어떤 경로의 main.py가 실행 중인지 확인하세요.

### 디버깅 2: 실제 로드된 모듈 확인

main.py 시작 후:
```python
# Python 인터프리터에서
import strategy.scoring_system
print(strategy.scoring_system.__file__)
```

출력이 `/home/user/autotrade/strategy/scoring_system.py`가 아니면 문제!

### 디버깅 3: 파일 내용 직접 확인

```bash
# 하드코딩이 제대로 되어있는지 확인
grep -A 2 "min_value = 50" strategy/scoring_system.py
grep -A 2 "min_net_buy = 100_000" strategy/scoring_system.py
```

둘 다 출력되어야 함!

### 디버깅 4: 타임스탬프 확인

```bash
ls -lh strategy/scoring_system.py
ls -lh strategy/__pycache__/scoring_system.cpython-311.pyc 2>/dev/null
```

첫 번째 파일이 더 최신이어야 하고, 두 번째 파일은 없어야 함!

---

## 🆘 긴급 연락 사항

다음 정보를 보내주세요:

1. **재시작 후 처음 10줄 로그:**
```bash
python main.py 2>&1 | head -20
```

2. **스코어링 디버그 로그:**
```bash
tail -100 logs/bot.log | grep "DEBUG.*체결강도"
```

3. **파일 타임스탬프:**
```bash
ls -lh strategy/scoring_system.py
find . -name "scoring_system.cpython-311.pyc"
```

4. **캐시 디렉토리:**
```bash
find . -type d -name "__pycache__"
```

---

## 📋 체크리스트

재시작 전:
- [ ] pkill로 모든 프로세스 종료
- [ ] __pycache__ 디렉토리 삭제 확인
- [ ] .pyc 파일 삭제 확인

재시작 후:
- [ ] `min_value=50 (하드코딩)` 로그 확인
- [ ] `min_net_buy=100000 (하드코딩)` 로그 확인
- [ ] 초기 자본금 정상 확인
- [ ] 체결강도 점수가 0점 아님 확인

---

**지금 바로 재시작해보세요!**
