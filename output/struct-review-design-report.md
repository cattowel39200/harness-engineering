# 구조검토 도메인 — 에이전트 & 스킬 설계 보고서

## 1. 에이전트 정의

### 구조검토 AI 에이전트 (`struct-review.harness.yaml`)

```
역할: 구조공학 전문 AI 에이전트
도메인: struct-review
기준: KDS/KCS 설계기준

핵심 원칙:
  1. KDS/KCS 조항번호 반드시 명시
  2. 모든 수치에 단위 표기
  3. 안전율 산출 후 PASS/FAIL 판정
  4. 보수적 판단 (안전측 설계)
  5. 불확실한 가정에 [가정] 표시

가드레일 (절대 금지):
  ✗ 기준 없이 결과만 제시
  ✗ 안전율 미달인데 PASS 판정
  ✗ 단위 누락
  ✗ 불리한 하중조합 누락
  ✗ 경험적 판단만으로 결론

도구:
  ✓ execute_skill_block (스킬블록 실행)
  ✓ lookup_standard (기준 조항 조회)
  ✗ delete_file, execute_code (차단)
```

---

## 2. 스킬블록 DAG (15개 블록, 6개 카테고리)

```
                    ┌─────────────────┐
                    │ design-condition │  ← 설계조건 입력
                    └────────┬────────┘
                             │
            ┌────────┬───────┼───────┬────────┐
            ▼        ▼       ▼       ▼        ▼
       load-dead  load-live load-wind load-seismic
            │        │       │       │
            └────┬───┘───────┘───────┘
                 ▼
          load-combination  ← 하중조합 (극한/사용)
                 │
       ┌─────────┼──────────┬──────────┐
       ▼         ▼          ▼          ▼
    rc-slab   rc-beam   rc-column  retaining-wall
       │         │          │
       │         │          ├──────→ foundation
       │         │          │
       │         │          └──────→ seismic-design
       │         │
       └────┬────┘
            ▼
     crack-deflection  ← 사용성 (균열/처짐)
            │
            │    ┌──────────┐
            │    │detail-check│ ← 배근 상세
            │    └─────┬────┘
            │          │
            └────┬─────┘──── foundation
                 ▼
          review-report  ← 검토서 생성
```

---

## 3. 스킬블록 상세 (15개)

### 카테고리 1: 설계조건 입력 (1블록)

| 블록 | 설명 | 주요 내용 |
|------|------|----------|
| **design-condition** | 설계조건 정의 | 구조물 제원, fck/fy, 피복두께, 노출등급 |

### 카테고리 2: 하중 산정 (5블록)

| 블록 | 설명 | KDS 기준 | 주요 공식 |
|------|------|---------|----------|
| **load-dead** | 고정하중 | KDS 41 10 15 | RC 24kN/㎥, 마감 1.0~1.5kN/㎡ |
| **load-live** | 활하중 | KDS 41 10 15 T4.2 | 주거2.0, 사무실2.5, 상점4.0 kN/㎡ |
| **load-wind** | 풍하중 | KDS 41 10 15 | q=0.5×1.225×V², 풍속압×풍압계수 |
| **load-seismic** | 지진하중 | KDS 41 17 00 | Cs=SDS/(R/Ie), V=Cs×W |
| **load-combination** | 하중조합 | KDS 41 12 00 5.2 | 1.2D+1.6L, 1.2D+1.0E 등 |

### 카테고리 3: 부재 검토 (5블록)

| 블록 | 설명 | KDS 기준 | 주요 검토 |
|------|------|---------|----------|
| **rc-slab** | RC 슬래브 | KDS 41 12 00 | 휨(φMn), 전단(φVc), 최소두께, 배근 |
| **rc-beam** | RC 보 | KDS 41 12 00 | 휨, 전단(Vc+Vs), 처짐, 균열폭 |
| **rc-column** | RC 기둥 | KDS 41 12 00 Ch.6 | P-M 상호작용, 세장비, 좌굴 |
| **foundation** | 기초 | KDS 11 50 00 | 지지력, 전도, 활동, 침하, 뚫림전단 |
| **retaining-wall** | 옹벽 | KDS 11 80 05 | 토압(Rankine), 전도/활동/지지력 |

### 카테고리 4: 특수 검토 (3블록)

| 블록 | 설명 | KDS 기준 | 주요 검토 |
|------|------|---------|----------|
| **seismic-design** | 내진설계 | KDS 41 17 00 | SDC, 층간변위, P-Δ, 내진상세 |
| **crack-deflection** | 사용성 | KDS 41 12 00 4.2 | 균열폭(≤0.3mm), 처짐(L/240) |
| **detail-check** | 배근 상세 | KDS 41 12 00 Ch.8 | 최소철근비, 정착길이, 이음길이 |

### 카테고리 5: 검토서 출력 (1블록)

| 블록 | 설명 | 내용 |
|------|------|------|
| **review-report** | 검토서 생성 | 8장 구성 표준 양식 (개요~기술사검토란) |

---

## 4. 템플릿 (4개)

| 템플릿 | 대상 | 블록 수 | 가격 |
|--------|------|---------|------|
| **rc-building** | RC 건축물 전체 | 14 | 80만원~ |
| **foundation-only** | 기초 설계 | 6 | 50만원~ |
| **retaining-wall-only** | 옹벽 구조 | 6 | 50만원~ |
| **seismic-evaluation** | 내진성능평가 | 6 | 80만원~ |

---

## 5. 실행 예시: RC 건축물 전체 검토

```
사용자: "5층 RC 아파트 구조검토 해주세요. fck=24MPa, fy=400MPa"

에이전트 실행 순서:

[1] design-condition
    → 5층, fck=24MPa, fy=400MPa, 피복 40mm

[2] load-dead → DL = 자중(24×0.2) + 마감(1.5) + 칸막이(1.0) = 7.3 kN/㎡
[3] load-live → LL = 2.0 kN/㎡ (주거)
[4] load-wind → W = q×Cf (지역별 산정)
[5] load-seismic → V = 0.073W (서울, 지반S3, R=5)

[6] load-combination
    → 지배: 1.2(7.3) + 1.6(2.0) = 11.96 kN/㎡ (극한)
    → 지배: 7.3 + 2.0 = 9.3 kN/㎡ (사용)

[7] rc-slab → Mu=38.2kN·m, φMn=45.6kN·m → Mu/φMn=0.84 → PASS ✅
[8] rc-beam → Vu=185kN, φVn=245kN → 0.76 → PASS ✅
[9] rc-column → Pu=2,400kN, φPn=3,100kN → 0.77 → PASS ✅
[10] foundation → σ=285kN/㎡, qa=300kN/㎡ → 0.95 → PASS ✅
[11] seismic-design → Δ/h=0.8% < 1.5% → PASS ✅
[12] crack-deflection → w=0.25mm < 0.3mm → PASS ✅, δ=12mm < 25mm → PASS ✅
[13] detail-check → ρ=0.0085 > ρmin=0.0035 → PASS ✅
[14] review-report → 구조검토서 생성 (8장 양식)

결과:
┌────────────┬──────────┬──────────┬────────┬──────┐
│ 부재       │ 검토항목  │ 계산값   │ 허용값  │ 판정 │
├────────────┼──────────┼──────────┼────────┼──────┤
│ 슬래브     │ 휨강도   │ 0.84     │ ≤1.0   │ PASS │
│ 보         │ 전단강도 │ 0.76     │ ≤1.0   │ PASS │
│ 기둥       │ 축력강도 │ 0.77     │ ≤1.0   │ PASS │
│ 기초       │ 지지력   │ 0.95     │ ≤1.0   │ PASS │
│ 내진       │ 층간변위 │ 0.8%     │ ≤1.5%  │ PASS │
│ 균열       │ 균열폭   │ 0.25mm   │ ≤0.3mm │ PASS │
│ 처짐       │ 장기처짐 │ 12mm     │ ≤25mm  │ PASS │
│ 배근       │ 철근비   │ 0.0085   │ ≥0.0035│ PASS │
└────────────┴──────────┴──────────┴────────┴──────┘

종합 판정: 전 항목 PASS — 구조안전 적합
```

---

## 6. 플랫폼 연동 포인트

```
[의뢰인이 "RC 구조검토" 의뢰]
     ↓
프로젝트 상태: "ai_review"
     ↓
하네스 엔진이 struct-review.harness.yaml 로드
     ↓
rc-building 템플릿의 14개 블록 순차 실행
     ↓
각 블록의 skills/*.md 규칙에 따라 계산
     ↓
PASS/FAIL 결과를 세션 컨텍스트에 저장
     ↓
review-report 블록이 검토서 생성
     ↓
프로젝트 상태: "engineer_review"
     ↓
기술사에게 알림 → /engineer/reviews/[id] 에서 검증
     ↓
기술사 확인 선서 + 날인
     ↓
QR 코드 포함 검토서 납품
```

---

## 7. 파일 목록 (생성 완료)

### 하네스 (1개)
```
harnesses/struct-review.harness.yaml  ← 에이전트 규칙서
```

### 도메인 (21개)
```
domains/struct-review/
├── domain.yaml                  ← 도메인 매니페스트
├── skillweb.json               ← 15블록 DAG + 4템플릿
├── skills/                     ← 15개 스킬블록
│   ├── design-condition.md     (설계조건)
│   ├── load-dead.md            (고정하중)
│   ├── load-live.md            (활하중)
│   ├── load-wind.md            (풍하중)
│   ├── load-seismic.md         (지진하중)
│   ├── load-combination.md     (하중조합)
│   ├── rc-slab.md              (슬래브 검토)
│   ├── rc-beam.md              (보 검토)
│   ├── rc-column.md            (기둥 검토)
│   ├── foundation.md           (기초 검토)
│   ├── retaining-wall.md       (옹벽 검토)
│   ├── seismic-design.md       (내진설계)
│   ├── crack-deflection.md     (사용성)
│   ├── detail-check.md         (배근 상세)
│   └── review-report.md        (검토서 생성)
└── templates/                  ← 4개 템플릿
    ├── rc-building.md          (RC 건축물 전체)
    ├── foundation-only.md      (기초)
    ├── retaining-wall-only.md  (옹벽)
    └── seismic-evaluation.md   (내진평가)
```

### 총 파일 수: 22개 (하네스 1 + 도메인 21)
