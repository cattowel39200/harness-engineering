# Harness Engineering Platform (Local Mode)

이 프로젝트는 **하네스 엔지니어링 시스템**입니다.
사용자가 프롬프트를 입력하면, Claude가 하네스(규칙서)와 스킬블록을 읽고 그에 따라 응답합니다.

## 작동 방식

1. 사용자가 요청하면, 해당 도메인의 **하네스 파일**(`harnesses/*.harness.yaml`)을 읽습니다
2. 하네스의 **role**(역할), **guardrails**(제약), **hooks**(자동규칙)을 따릅니다
3. 필요한 **스킬블록**(`domains/*/skills/*.md`)을 읽고 그 지침대로 작업합니다
4. 스킬블록의 **DAG 순서**(skillweb.json의 requires 체인)를 지킵니다
5. 결과물은 **output/** 폴더에 마크다운으로 저장합니다

## 하네스 시스템 규칙 (필수)

### 에이전트 시작 시
- 사용자의 첫 요청을 받으면 `harnesses/biz-skill.harness.yaml`을 읽습니다
- 하네스의 `role.identity`에 따라 행동합니다
- 하네스의 `guardrails`를 절대 위반하지 않습니다

### 스킬블록 실행 시
1. `domains/{domain}/skillweb.json`에서 DAG 의존성을 확인합니다
2. **requires가 충족된 블록만** 실행합니다 (선행블록 미완료 시 안내)
3. 블록 파일(`skills/*.md`)을 읽고 그 안의 **규칙, 프레임워크, 템플릿**을 따릅니다
4. 실행 완료 후 **provides 산출물**을 기록합니다
5. 다음 실행 가능 블록을 제안합니다

### 특정 지원사업이 있으면
- `domains/{domain}/templates/*.md`에서 해당 템플릿을 먼저 읽습니다
- 템플릿에 정의된 블록 순서를 따릅니다

## 프로젝트 구조

```
harness-engineering/
├── CLAUDE.md                  ← 이 파일 (시스템 규칙)
├── harnesses/                 ← 하네스(규칙서) 정의
│   └── biz-skill.harness.yaml    ← 사업스킬 에이전트 규칙서
├── domains/                   ← 도메인 플러그인
│   ├── biz-skill/             ← 사업화 스킬웹
│   │   ├── domain.yaml
│   │   ├── skillweb.json          ← 스킬 DAG 그래프
│   │   ├── skills/ (18개)         ← 스킬블록 지침서
│   │   └── templates/ (6개)       ← 지원사업별 템플릿
│   └── struct-review/         ← AI 구조검토 (향후)
│       └── domain.yaml
├── output/                    ← 생성된 산출물 저장
└── sessions/                  ← 세션별 진행상태 저장
```

## 사용 예시

사용자: "AI 구조검토 SaaS로 예비창업패키지 신청하려합니다"
→ Claude: harness 읽기 → 상태파악 → 해당 template 확인 → 블록 순차 실행

사용자: "시장분석 해줘"
→ Claude: skillweb.json에서 market-analysis 블록의 requires 확인 → 선행블록 충족 시 skills/market-analysis.md 읽고 수행

## 응답 형식

```
📋 하네스 에이전트 분석
- 현재 단계: [파악된 단계]
- 선택 블록: [블록 목록]
- 대상 사업: [추천/지정된 지원사업]

🔧 [블록명] 실행 중...
[스킬블록 지침에 따른 산출물]

✅ 완료
- 산출물: [생성된 파일 목록]
- 다음 단계: [실행 가능한 블록 목록]
```
