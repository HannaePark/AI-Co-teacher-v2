# 🍎 AI Co-teacher: AI 학습 데이터 분석 대시보드
**컴퓨팅사고와 SW코딩 기말 프로젝트** **작성자:** 2021113295 영어영문학과 박한내  

## 1. 프로젝트 소개 (Introduction)
본 프로젝트는 언어 교육 환경에서 발생하는 학생들의 다양한 학습 데이터(클릭 수, 퀴즈 점수, 상호작용, 학습 시간 등)를 실시간으로 분석하여 교사의 교수 의사결정을 돕는 **AI 학습 분석 대시보드**입니다.

## 2. 핵심 교육학 알고리즘 (Pedagogical Logic)
명세서(SRS)에 정의된 교육학적 이론을 데이터 과학적으로 구현하였습니다.
* **ZPD (근접발달영역)**: 학생 점수의 평균과 표준편차를 활용해 적정 난이도 구간을 시각화합니다.
* **VARK 모델**: 행동 데이터를 정규화하여 시각(V), 청각(A), 읽기/쓰기(R), 운동(K) 학습 스타일을 분류합니다.
* **SRL_Index (자기조절학습)**: `(학습시간/120 + 상호작용 + 성공여부) / 3` 공식을 통해 자율 학습 역량을 수치화합니다.

## 3. 주요 기능 (Key Features)
* **실시간 KPI**: 총 학생 수, 평균 점수, 성공률 등 핵심 지표 요약.
* **위험 학생 감지**: 점수 50점 미만 또는 참여도 0.3 미만 학생 자동 식별 및 경고.
* **AI 예측 분석**: RandomForest 모델을 이용한 학습 성공 기여 요인 도출.
* **개인화 추천**: 학생별 유형에 따른 맞춤형 개입 전략 및 메시징 도구.

## 4. 실행 방법 (How to Run)
1. 라이브러리 설치: `pip install streamlit pandas numpy plotly scikit-learn`
2. 대시보드 실행: `streamlit run app.py`

## 5. 실시간 대시보드 접속 링크 Live Dashboard URL
[https://ai-co-teacher-v2-4qja5xbnt4rxjphkmybpy6.streamlit.app/](https://ai-co-teacher-v2-4qja5xbnt4rxjphkmybpy6.streamlit.app/)

## 📂 대쉬보드 데이터 입력 명세 (CSV Header Specification)
본 시스템의 학습 분석 및 AI 모델 작동을 위해 업로드하는 CSV 파일은 반드시 아래의 헤더(Header) 구조를 포함.

| 컬럼명 | 데이터 타입 | 설명 | 교육학적 활용 지표 |
| :--- | :--- | :--- | :--- |
| **`student_id`** | String | 학생 고유 식별 코드 (예: STU_001) | 학생별 개별 모니터링 |
| **`quiz_score`** | Integer | 퀴즈 성적 (0~100) | ZPD 구간 산출 및 위험 감지 |
| **`clicks`** | Integer | 시스템 내 클릭 횟수 | VARK(시각/청각) 유형 분류 |
| **`time_spent`** | Integer | 총 학습 체류 시간 (분) | SRL 지수 산출 및 읽기/쓰기 유형 분석 |
| **`interactions`** | Integer | 능동적 상호작용 횟수 | SRL 지수 및 운동(K) 유형 분석 |
| **`success`** | Boolean | 학습 성공 여부 (1:성공, 0:실패) | AI(RandomForest) 예측 모델 학습 |

### 💡 데이터 샘플 (예시)
```csv
student_id,quiz_score,clicks,time_spent,interactions,success
STU_001,85,120,150,15,1
STU_002,42,45,60,5,0
STU_003,90,180,200,18,1
