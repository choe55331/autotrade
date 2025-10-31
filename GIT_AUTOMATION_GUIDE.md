# Git 자동화 가이드 🚀

이 가이드는 Git 작업을 자동화하여 GitHub Desktop 없이도 쉽게 push/pull을 할 수 있게 도와줍니다.

## 📋 제공되는 스크립트

### 1. `git_sync.bat` - 자동 동기화
로컬 변경사항 없이 최신 코드를 받아오고 푸시만 하고 싶을 때 사용합니다.

**사용법:**
```bash
git_sync.bat
```

**동작:**
1. 현재 브랜치 확인
2. 미커밋 변경사항 체크
3. 원격에서 최신 변경사항 가져오기 (fetch)
4. Rebase로 pull
5. 로컬 커밋을 원격으로 push

### 2. `git_commit_and_sync.bat` - 커밋 후 동기화
파일을 수정한 후 한번에 커밋하고 동기화하고 싶을 때 사용합니다.

**사용법:**
```bash
git_commit_and_sync.bat "커밋 메시지를 여기에 작성"
```

**예시:**
```bash
git_commit_and_sync.bat "fix: 버그 수정"
git_commit_and_sync.bat "feat: 새로운 기능 추가"
git_commit_and_sync.bat "docs: 문서 업데이트"
```

**동작:**
1. 모든 변경사항 staging (git add -A)
2. 커밋 생성
3. 원격에서 최신 변경사항 가져오기
4. Rebase로 pull
5. 원격으로 push

## 🎯 사용 시나리오

### 시나리오 1: 다른 곳에서 코드를 수정했고, 로컬에 반영하고 싶을 때
```bash
git_sync.bat
```

### 시나리오 2: 로컬에서 코드를 수정했고, GitHub에 올리고 싶을 때
```bash
git_commit_and_sync.bat "작업 내용 설명"
```

### 시나리오 3: 매일 작업 시작 전
```bash
# 최신 코드 받아오기
git_sync.bat
```

### 시나리오 4: 작업 완료 후
```bash
# 변경사항 커밋 & 푸시
git_commit_and_sync.bat "오늘 작업 내용 정리"
```

## 🔄 자동 동기화 설정 (선택사항)

매번 수동으로 실행하기 귀찮다면, Windows 작업 스케줄러로 자동화할 수 있습니다.

### 방법 1: 작업 스케줄러 설정

1. **Windows 검색**에서 "작업 스케줄러" 실행
2. **작업 만들기** 클릭
3. **일반** 탭:
   - 이름: "AutoTrade Git Sync"
   - 설명: "자동으로 git pull/push"
4. **트리거** 탭:
   - 새로 만들기
   - "로그온 시" 또는 "하루에 한 번" 선택
5. **동작** 탭:
   - 새로 만들기
   - 프로그램/스크립트: `C:\Users\USER\Desktop\autotrade\git_sync.bat`
   - 시작 위치: `C:\Users\USER\Desktop\autotrade`
6. **확인** 클릭

### 방법 2: VS Code 통합

VS Code를 사용한다면 `.vscode/tasks.json`에 추가:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Git Sync",
      "type": "shell",
      "command": "git_sync.bat",
      "problemMatcher": [],
      "group": {
        "kind": "build",
        "isDefault": false
      }
    },
    {
      "label": "Git Commit & Sync",
      "type": "shell",
      "command": "git_commit_and_sync.bat",
      "args": ["${input:commitMessage}"],
      "problemMatcher": []
    }
  ],
  "inputs": [
    {
      "id": "commitMessage",
      "type": "promptString",
      "description": "커밋 메시지를 입력하세요",
      "default": "update"
    }
  ]
}
```

그러면 `Ctrl+Shift+P` → "Tasks: Run Task" → "Git Sync" 또는 "Git Commit & Sync" 선택

## 💡 팁

### 1. 빠른 접근을 위한 단축키 만들기
배치 파일의 바로가기를 만들고 단축키를 할당할 수 있습니다:

1. `git_sync.bat` 우클릭 → **바로가기 만들기**
2. 바로가기 우클릭 → **속성**
3. **바로 가기 키**: `Ctrl+Alt+G` 등 설정
4. **확인**

### 2. PowerShell에서 사용하기
PowerShell을 선호한다면:
```powershell
# Sync
.\git_sync.bat

# Commit and Sync
.\git_commit_and_sync.bat "커밋 메시지"
```

### 3. Git Alias 설정
Git 명령어를 더 짧게 만들기:
```bash
git config --global alias.sync '!git pull --rebase && git push'
git config --global alias.save '!git add -A && git commit -m'
```

사용:
```bash
git sync
git save "메시지" && git sync
```

## ⚠️ 주의사항

1. **Merge Conflict 발생 시**:
   - 스크립트가 자동으로 중단됩니다
   - 수동으로 conflict를 해결해야 합니다
   - 해결 후 다시 스크립트 실행

2. **큰 파일 커밋 시**:
   - Git LFS 사용을 권장합니다
   - 100MB 이상 파일은 GitHub에서 차단됩니다

3. **민감한 정보**:
   - `.env`, `credentials.json` 등은 `.gitignore`에 추가
   - 절대 커밋하지 마세요!

4. **작업 중 동기화**:
   - 작업 중에는 sync하지 않는 것을 권장
   - 커밋 가능한 상태일 때만 sync

## 🔧 문제 해결

### "Permission denied" 에러
```bash
git config --global credential.helper wincred
```

### 스크립트 실행 안 됨
관리자 권한으로 실행:
- 배치 파일 우클릭 → **관리자 권한으로 실행**

### Rebase 실패
```bash
git rebase --abort
git pull origin <branch-name>
# 수동으로 conflict 해결 후
git push
```

## 📚 추가 리소스

- [Git 공식 문서](https://git-scm.com/doc)
- [Pro Git 책 (한글)](https://git-scm.com/book/ko/v2)
- [GitHub Desktop 대안들](https://git-scm.com/downloads/guis)

---

**더 궁금한 점이 있으면 언제든지 물어보세요!** 💬
