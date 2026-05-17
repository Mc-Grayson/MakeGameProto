# 🚇 첫 번째 미니게임: 지하철 자리 쟁탈전

## 의뢰 브리핑 텍스트
```
의뢰인: 박씨 아줌마 (45세)
의뢰 내용: 퇴근길 지하철에서 창가 자리를 꼭 앉아야겠습니다.
           옆에 발 빠른 아저씨가 있어서요.
보수: 3,500원
난이도: ⚡ 일상
제한 시간: 10초
```

## 게임 플로우
```
[의뢰서 화면] 3초
    ↓
[게임 시작] 지하철 문 닫힌 상태
    ↓
[카운트다운] "띵동... 다음 역은..."
    ↓
[문 열림 직전] 빨간(박씨) / 파란(아저씨) 테두리 표시
    ↓
[입력 타이밍] 문 열리는 순간 TAP
    ↓  (파란 아저씨 발 앞 가방이 살짝 튀어나오는 연출)
[성공] 박씨 아줌마 자리에 앉는 애니메이션 + "성공!" 연출
[실패] 아저씨가 먼저 앉음 + "이번엔... 실패" 연출
    ↓
[결과 화면] 보수 지급 or 위약금
```

## 판정 기준
- PERFECT (문 열리는 프레임 ±3f): 가방이 완벽하게 걸림 → 아저씨 완전히 차단
- GOOD (±8f): 가방이 살짝 걸림 → 아저씨가 비틀거리다가 박씨가 먼저 앉음
- BAD (±15f): 너무 이르거나 늦음 → 아저씨가 눈치채고 피함
- MISS: 아무것도 안 함 → 아저씨가 당당히 착석

## 씬 구성요소
- 배경: 지하철 내부 (좌석 배열, 손잡이)
- 캐릭터A (빨강): 박씨 아줌마 (단발, 가방 멘 아줌마)
- 캐릭터B (파랑): 경쟁자 아저씨 (양복, 서류가방)
- 빈 좌석 (창가)
- 지하철 문
- 염력 이펙트: 가방이 살짝 빛나는 효과

## 사운드 큐
- 지하철 달리는 소리 (루프)
- 띵동 안내음
- 문 열리는 소리
- 성공: 경쾌한 효과음
- 실패: 축 처지는 효과음

## 스프라이트 목록
| 파일명 | 크기 | 프레임 수 | 설명 |
|--------|------|-----------|------|
| bg_subway.png | 320x180 | 1 | 지하철 배경 |
| char_auntie_idle.png | 32x48 | 2 | 박씨 대기 |
| char_auntie_run.png | 32x48 | 3 | 박씨 달리기 |
| char_auntie_sit.png | 32x48 | 2 | 박씨 착석 |
| char_man_idle.png | 32x48 | 2 | 아저씨 대기 |
| char_man_run.png | 32x48 | 3 | 아저씨 달리기 |
| char_man_sit.png | 32x48 | 2 | 아저씨 착석 |
| door_subway.png | 48x90 | 4 | 문 열림 |
| effect_telekinesis.png | 32x32 | 4 | 염력 이펙트 |
| ui_border_red.png | 40x52 | 1 | 빨간 테두리 |
| ui_border_blue.png | 40x52 | 1 | 파란 테두리 |

## GDScript 구조 스케치

```gdscript
# SubwayGame.gd
extends MinigameBase

enum State { WAITING, COUNTDOWN, DOOR_OPEN, RESULT }

var current_state: State = State.WAITING
var door_open_time: float = 0.0
var input_received: bool = false

func _on_game_start():
    time_limit = 10.0
    # 지하철 소리 시작
    # 카운트다운 시작 (3초 후 문 열림)
    await get_tree().create_timer(3.0).timeout
    _open_door()

func _open_door():
    current_state = State.DOOR_OPEN
    door_open_time = elapsed_time
    # 문 열림 애니메이션 재생

func _input(event):
    if current_state != State.DOOR_OPEN:
        return
    if event is InputEventMouseButton and event.pressed:
        _judge_timing()

func _judge_timing():
    input_received = true
    var diff = elapsed_time - door_open_time
    var grade = TimingSystem.judge(diff, 0.0)
    match grade:
        TimingSystem.Grade.PERFECT, TimingSystem.Grade.GOOD:
            _play_success_animation()
            complete(true, grade)
        _:
            _play_fail_animation()
            complete(false, grade)
```
