---
name: 구조계산서 조립
category: output
requires: [report-cover, report-load, report-member, report-serviceability, report-detail, report-summary, report-engineer]
provides: [review-document, safety-confirmation]
---

# 구조계산서 조립

개별 보고서 스킬(표지~기술사란)에서 작성된 각 편을 하나의 구조계산서로 조립한다.

---

## 규칙

1. 아래 순서대로 편을 조립한다. 순서 변경 금지.
2. 각 편이 완성되지 않은 채로 조립하지 않는다.
3. 목차를 자동 생성한다.

---

## 조립 순서

```
표지           ← report-cover
목차           ← 자동 생성
제1장 개요      ← report-cover
제2장 설계조건   ← report-cover
제3장 하중산정   ← report-load
제4장 슬래브     ← report-member
제5장 보        ← report-member
제6장 기둥      ← report-member
제7장 기초/옹벽  ← report-member
제8장 내진설계   ← report-member (해당시)
제9장 사용성    ← report-serviceability
제10장 배근상세  ← report-detail
제11장 종합판정  ← report-summary
제12장 기술사란  ← report-engineer
```

## 구조물별 생략 가능 장

| 구조물 | 생략 가능 장 |
|--------|-----------|
| 옹벽/홍수방지벽 | 제4장(슬래브), 제5장(보), 제8장(내진) |
| 기초 | 제4장(슬래브), 제5장(보), 제8장(내진) |
| RC 건축물 | 없음 (전 장 작성) |

## 체크리스트
- [ ] 표지 포함
- [ ] 목차 생성
- [ ] 전체 장 순서대로 조립
- [ ] 빠진 장 없음
- [ ] 페이지 번호 연속
