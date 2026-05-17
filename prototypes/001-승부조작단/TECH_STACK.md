# 🛠️ 기술 스택 & 구현 계획

## 📌 결론 먼저

**추천 스택: Godot 4 (GDScript)**

---

## 🔍 엔진 비교 검토

### Option A: Godot 4 ✅ 추천
| 항목 | 평가 |
|------|------|
| 픽셀 아트 지원 | ✅ 매우 좋음 (CanvasItem, Viewport 스케일링) |
| 미니게임 구조 구현 | ✅ Scene 시스템이 딱 맞음 |
| 타이밍 게임 | ✅ 정밀한 프레임 제어 가능 |
| 무료 & 오픈소스 | ✅ |
| 학습 난이도 | 중간 (파이썬 비슷한 GDScript) |
| AI 이미지 파이프라인 연동 | ✅ 외부 툴로 에셋 생성 후 import |
| 웹 배포 | ✅ HTML5 export 지원 |
| 모바일 | ✅ 추후 가능 |

### Option B: Pygame (Python)
| 항목 | 평가 |
|------|------|
| 진입 장벽 | ✅ 낮음 |
| 픽셀 아트 | ✅ 가능 |
| 배포 | ❌ 번거로움 (exe 패키징 복잡) |
| 씬 관리 | ❌ 직접 구현해야 함 |
| 결론 | 프로토타입에는 OK, 장기 개발엔 비추 |

### Option C: Unity
| 항목 | 평가 |
|------|------|
| 픽셀 아트 | 가능하지만 설정 번거로움 |
| 라이선스 | ❌ 런타임 비용 이슈 (2023년 논란) |
| 결론 | 굳이 선택할 이유 없음 |

### Option D: PICO-8 / TIC-80
| 항목 | 평가 |
|------|------|
| 컨셉 핏 | ✅ 허접한 도트 그래픽에 완벽 |
| 제약 | 해상도/색상/크기 엄격히 제한 |
| 결론 | 잼/데모용으로 고려 가능, 본 개발엔 한계 |

---

## 🎮 Godot 4 구현 설계

### 프로젝트 구조
```
match-fixers/
├── project.godot
├── scenes/
│   ├── Main.tscn          # 메인 허브 씬
│   ├── BriefingScreen.tscn # 의뢰서 화면
│   ├── ResultScreen.tscn   # 결과 화면
│   └── minigames/
│       ├── SubwayGame.tscn
│       ├── BaseballGame.tscn
│       └── ...
├── scripts/
│   ├── core/
│   │   ├── GameManager.gd  # 미니게임 전환, 점수, 흐름 관리
│   │   ├── TimingSystem.gd # 타이밍 판정 코어
│   │   └── MinigameBase.gd # 모든 미니게임이 상속하는 베이스 클래스
│   └── minigames/
│       ├── SubwayGame.gd
│       └── ...
├── assets/
│   ├── sprites/
│   ├── audio/
│   └── ui/
└── resources/
    └── mission_data/       # 의뢰 데이터 (JSON or Resource)
```

### 핵심 시스템: MinigameBase

```gdscript
# MinigameBase.gd
class_name MinigameBase
extends Node2D

signal minigame_completed(success: bool, score: int)

@export var time_limit: float = 15.0
@export var mission_grade: String = "daily"  # daily / small / big

var elapsed_time: float = 0.0
var is_active: bool = false

func start_game():
    is_active = true
    _on_game_start()

func _process(delta):
    if not is_active:
        return
    elapsed_time += delta
    if elapsed_time >= time_limit:
        _on_time_over()

func complete(success: bool, score: int = 0):
    is_active = false
    minigame_completed.emit(success, score)

func _on_game_start():
    pass  # 각 미니게임에서 override

func _on_time_over():
    complete(false, 0)
```

### 타이밍 판정 시스템

```gdscript
# TimingSystem.gd
class_name TimingSystem

enum Grade { PERFECT, GOOD, BAD, MISS }

static func judge(input_time: float, target_time: float) -> Grade:
    var diff = abs(input_time - target_time)
    if diff < 0.05:   return Grade.PERFECT
    elif diff < 0.12: return Grade.GOOD
    elif diff < 0.25: return Grade.BAD
    else:             return Grade.MISS
```

---

## 🖼️ AI 이미지 리소스 수급 전략

### 핵심 문제
도트 그래픽 특성상 AI 이미지를 **직접 사용하기 어려움** → 하지만 **워크플로우 구성으로 해결 가능**

### 추천 파이프라인

```
아이디어/시나리오
    ↓
[Claude / ChatGPT] - 씬 구성, 캐릭터 묘사 텍스트 작성
    ↓
[Midjourney / DALL-E 3 / Stable Diffusion] - 레퍼런스 이미지 생성
    ↓
[Aseprite] - 도트 아트로 변환/트레이싱 (핵심 작업)
    ↓
[Godot] - 스프라이트 import, 애니메이션 설정
```

### AI 도트 변환 도구들

| 도구 | 용도 | 비용 |
|------|------|------|
| **Aseprite** | 도트 아트 편집기 (업계 표준) | $20 일회성 |
| **Pixellab (앱)** | AI로 도트 직접 생성 | 월정액 |
| **Stable Diffusion + pixel art LoRA** | AI로 도트 스타일 이미지 생성 | 무료 (로컬) |
| **img2pixel 류 웹서비스** | 일반 이미지 → 도트 변환 | 무료~소액 |

### 현실적인 워크플로우

1. **씬 레이아웃**: Claude로 "지하철 자리 쟁탈전" 씬 구성 텍스트 작성
2. **레퍼런스 생성**: Midjourney로 2D 플랫 스타일 이미지 생성
3. **도트화**: Aseprite에서 32x32~64x64 규격으로 트레이싱
4. **애니메이션**: 2~4프레임 루프 애니메이션 (허접함이 오히려 매력)

### 캐릭터 스프라이트 전략
- 기본 사이즈: 32x48px
- 색상 제한: 스테이지당 8색 팔레트
- 애니메이션: 대기(2f), 동작(3~4f), 반응(2f) - 최소화해서 허접미 극대화

---

## 🚀 프로토타입 로드맵

### Phase 0 - 환경 설정 (1일)
- [ ] Godot 4 설치
- [ ] 프로젝트 생성, 픽셀 아트 설정 (viewport 320x180, nearest filter)
- [ ] GitHub 저장소 생성

### Phase 1 - 코어 시스템 (1~2주)
- [ ] MinigameBase 클래스 구현
- [ ] 씬 전환 시스템 (의뢰서 → 게임 → 결과)
- [ ] 타이밍 판정 시스템
- [ ] 빨간/파란 테두리 UI 시스템

### Phase 2 - 첫 미니게임 (2~3주)
- [ ] **지하철 자리 쟁탈전** 구현 (가장 단순한 것부터)
  - 배경: 지하철 내부 (도트)
  - 캐릭터 2명 (빨강/파랑 테두리)
  - 문 열리는 타이밍에 맞춰 탭
  - 성공/실패 연출
- [ ] 임시 사각형 그래픽으로 게임플레이 먼저 검증

### Phase 3 - 그래픽 교체 & 두 번째 미니게임 (3~4주)
- [ ] AI + Aseprite로 실제 스프라이트 제작
- [ ] 두 번째 미니게임 추가 (가위바위보 or 삼각김밥)
- [ ] 의뢰서 UI 완성

### Phase 4 - 데모 완성
- [ ] 미니게임 5개
- [ ] 스토리/의뢰 흐름 완성
- [ ] itch.io 업로드

---

## 💰 예산 예상

| 항목 | 비용 |
|------|------|
| Godot 4 | 무료 |
| Aseprite | $20 |
| Midjourney | $10/월 (필요할 때) |
| 사운드 (itch.io 무료 에셋) | 무료 |
| **합계** | **$20~30** |

---

## ⚠️ 리스크 & 대응

| 리스크 | 대응 |
|--------|------|
| 도트 아트 퀄리티 | 의도적 허접미 → 오히려 강점으로 활용 |
| 미니게임 아이디어 고갈 | 일상생활에서 계속 발굴 가능, 초기엔 10개 목표 |
| 혼자 개발 번아웃 | Phase별로 플레이 가능한 빌드 유지, 작은 성취감 |
| AI 이미지 저작권 | 트레이싱/재창작이므로 리스크 최소화 |
