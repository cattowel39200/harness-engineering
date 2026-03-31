# 하네스 엔지니어링 — 60개 테스트 시나리오

## 관리자 시나리오 (A01~A20)

| ID | 시나리오 | 페이지 | 검증 항목 |
|----|---------|--------|----------|
| A01 | 관리자 로그인 | /login | "관리자로 로그인" 클릭 → /admin/dashboard 이동 |
| A02 | 대시보드 통계 확인 | /admin/dashboard | 6개 통계 카드 (회원, 기술사, 매출, 프로젝트, 대기건, 승인대기) |
| A03 | 기술사 승인 대기 알림 | /admin/dashboard | "기술사 승인 대기 1명" 알림 배너 표시 |
| A04 | 최근 프로젝트 테이블 | /admin/dashboard | 4건 프로젝트, 제목/의뢰인/유형/상태/금액/날짜 표시 |
| A05 | 프로젝트 상태 뱃지 색상 | /admin/dashboard | 완료(녹색), 기술사검증중(주황), AI검토중(보라), 결제대기(노랑) |
| A06 | 회원관리 페이지 접근 | /admin/users | 전체 회원 목록 테이블 표시 |
| A07 | 회원 역할별 필터 | /admin/users | 전체/의뢰인/기술사/관리자 탭 필터 |
| A08 | 기술사 관리 페이지 | /admin/engineers | 기술사 목록 (자격종목, 사무소, 상태, 완료건수, 평점) |
| A09 | 기술사 승인 버튼 | /admin/engineers | 승인대기 기술사에 "승인"/"거절" 버튼 표시 |
| A10 | 기술사 승인 실행 | /admin/engineers | "승인" 클릭 → 상태 변경 확인 |
| A11 | 프로젝트 관리 페이지 | /admin/projects | 전체 프로젝트 목록 + 상태 필터 탭 |
| A12 | 프로젝트 상태 필터 | /admin/projects | 전체/진행중/완료/취소 탭 전환 |
| A13 | 결제 내역 페이지 | /admin/payments | 결제 내역 탭 - 테이블 표시 |
| A14 | 기술사 정산 탭 | /admin/payments | "기술사 정산" 탭 전환 - 정산 테이블 |
| A15 | 결제 합계 표시 | /admin/payments | 총 결제금액 합산 표시 |
| A16 | 사이드바 네비게이션 | /admin/* | 5개 메뉴 전체 클릭 이동 |
| A17 | 현재 메뉴 하이라이트 | /admin/* | 현재 페이지 메뉴 파란색 강조 |
| A18 | 사용자 정보 표시 | /admin/* | 좌측 하단 "관리자" 이름 + 역할 뱃지 |
| A19 | 로그아웃 | /admin/* | "로그아웃" 클릭 → /login 이동 |
| A20 | 관리하기 링크 연결 | /admin/dashboard | "관리하기 →" 클릭 → /admin/engineers 이동 |

## 고객(의뢰인) 시나리오 (C01~C20)

| ID | 시나리오 | 페이지 | 검증 항목 |
|----|---------|--------|----------|
| C01 | 의뢰인 로그인 | /login | "의뢰인으로 로그인" → /dashboard 이동 |
| C02 | 대시보드 통계 | /dashboard | 4개 카드 (총 프로젝트, 진행중, 완료, 총 결제액) |
| C03 | 최근 프로젝트 테이블 | /dashboard | 프로젝트명/구조유형/상태/금액/의뢰일 표시 |
| C04 | 최근 활동 타임라인 | /dashboard | 시간순 활동 목록 표시 |
| C05 | 프로젝트 목록 페이지 | /dashboard/projects | 프로젝트 카드 목록 |
| C06 | 프로젝트 필터 탭 | /dashboard/projects | 전체/진행중/완료/취소 필터 |
| C07 | 새 의뢰 Step1 | /dashboard/projects/new | 구조물 6종 유형 선택 카드 + 가격 |
| C08 | 새 의뢰 Step2 | /dashboard/projects/new | 제목/설명 입력 폼 |
| C09 | 새 의뢰 Step3 | /dashboard/projects/new | 파일 업로드 영역 |
| C10 | 새 의뢰 Step4 | /dashboard/projects/new | 견적 요약 (기본료/부가세/합계) + 결제 버튼 |
| C11 | 의뢰 완료 모달 | /dashboard/projects/new | 결제 후 "의뢰 완료" 성공 모달 |
| C12 | 프로젝트 상세 접근 | /dashboard/projects/[id] | 프로젝트 헤더 (제목, 상태, 유형, 날짜) |
| C13 | 진행상태 타임라인 | /dashboard/projects/[id] | 수직 타임라인 (상태별 색상 점) |
| C14 | AI 검토 결과 표시 | /dashboard/projects/[id] | KDS 기준 검토 결과 텍스트 |
| C15 | 첨부파일 목록 | /dashboard/projects/[id] | 파일명, 크기 표시 |
| C16 | 비용 정보 | /dashboard/projects/[id] | 기본료/부가세/합계 우측 표시 |
| C17 | 담당 기술사 정보 | /dashboard/projects/[id] | 기술사명, 자격, 사무소, 평점 |
| C18 | 결제 내역 페이지 | /dashboard/payments | 결제 테이블 + 합계 카드 |
| C19 | 설정 페이지 | /dashboard/settings | 정보수정, 비밀번호, 알림 토글, 탈퇴 |
| C20 | 사이드바 전체 메뉴 | /dashboard/* | 6개 메뉴 이동 + 하이라이트 |

## 기술사 시나리오 (E01~E20)

| ID | 시나리오 | 페이지 | 검증 항목 |
|----|---------|--------|----------|
| E01 | 기술사 로그인 | /login | "기술사로 로그인" → /engineer/dashboard 이동 |
| E02 | 대시보드 통계 | /engineer/dashboard | 4개 카드 (대기, 완료, 수입, 평점) |
| E03 | 검토 대기 건 목록 | /engineer/dashboard | 대기 건 카드 (제목, 금액) |
| E04 | 최근 완료 목록 | /engineer/dashboard | 완료 건 카드 + "완료" 뱃지 |
| E05 | 검토 대기열 보기 링크 | /engineer/dashboard | "검토 대기열 보기 >" → /engineer/reviews 이동 |
| E06 | 검토 대기열 탭 | /engineer/reviews | 대기중/진행중/완료 3개 탭 + 건수 |
| E07 | 대기 건 카드 정보 | /engineer/reviews | 제목, 유형뱃지, 의뢰인, 검토비, 요청일 |
| E08 | 수락/거절/상세보기 버튼 | /engineer/reviews | 3개 버튼 표시 |
| E09 | 상세보기 클릭 | /engineer/reviews | → /engineer/reviews/[id] 이동 |
| E10 | 검토 수행 헤더 | /engineer/reviews/[id] | "구조검토 수행" + 프로젝트명 |
| E11 | AI 검토 결과 표시 | /engineer/reviews/[id] | 적용기준 KDS 번호 + 보조기준 |
| E12 | 체크리스트 항목 | /engineer/reviews/[id] | 8개 검토항목 (체크박스 + PASS/FAIL) |
| E13 | 체크리스트 통과율 | /engineer/reviews/[id] | "6/8 통과" 표시 |
| E14 | 검토 의견 입력란 | /engineer/reviews/[id] | textarea 폼 |
| E15 | 프로젝트 정보 (우측) | /engineer/reviews/[id] | 프로젝트명/유형/의뢰인/의뢰일 |
| E16 | 예상 수입 표시 | /engineer/reviews/[id] | 125,000원 (총 검토비의 25%) |
| E17 | 검토 소요시간 | /engineer/reviews/[id] | 타이머 00:23:47 표시 |
| E18 | 승인(날인)/수정요청/반려 | /engineer/reviews/[id] | 녹색/노란색/빨간색 3개 버튼 |
| E19 | 정산 페이지 | /engineer/earnings | 수입 합계 카드 + 정산 테이블 |
| E20 | 프로필 페이지 | /engineer/profile | 자격정보, 평점, 전문분야, 편집 폼 |
