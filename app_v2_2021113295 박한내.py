import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import RandomForestClassifier
import base64

# --- 1. [FR4] 교육학 분석 및 데이터 과학적 VARK 모델링 ---
def calculate_educational_metrics(df):
    # 정규화: 단위가 다른 지표들을 0~1 사이로 변환 (비교 가능성 확보)
    clicks_norm = df['clicks'] / df['clicks'].max()
    time_norm = df['time_spent'] / df['time_spent'].max()
    inter_norm = df['interactions'] / df['interactions'].max()
    
    # VARK 유형별 점수 산출 로직
    # Visual: 탐색적 클릭 활동량 우세
    v_score = clicks_norm
    # Aural: 낮은 조작량 대비 긴 학습 유지 시간 (영상/청취 패턴)
    a_score = (1 - clicks_norm) * time_norm
    # Read/Write: 텍스트 분석을 위한 긴 절대 학습 시간
    r_score = time_norm
    # Kinesthetic: 능동적 상호작용 및 퀴즈 참여도 우세
    k_score = inter_norm
    
    vark_scores = pd.DataFrame({'Visual': v_score, 'Aural': a_score, 'Read/Write': r_score, 'Kinesthetic': k_score})
    df['VARK'] = vark_scores.idxmax(axis=1) # 가장 높은 점수의 유형 할당

    # SRL_Index: (학습시간/120 + 상호작용 + 성공)/3 [cite: 37]
    df['SRL_Index'] = (df['time_spent']/120 + df['interactions'] + df['success']) / 3
    
    # ZPD 구간 계산: 평균 ± 표준편차 [cite: 37]
    avg, std = df['quiz_score'].mean(), df['quiz_score'].std()
    zpd_range = (avg - std, avg + std)
    
    # [US-003] 위험 감지 플래그: 점수 < 50 또는 참여도 < 0.3 
    df['Status'] = np.where((df['quiz_score'] < 50) | (df['SRL_Index'] < 0.3), '🚨 고위험', '✅ 정상')
    return df, zpd_range

# --- 2. [FR6] 보고서 생성 기능 ---
def get_report_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="Weekly_Report.csv">📄 주간 분석 보고서 다운로드</a>'

# --- 3. 메인 대시보드 UI ---
st.set_page_config(page_title="AI Co-teacher", layout="wide")
st.title("🍎 AI Co-teacher: AI 학습 데이터 분석 대시보드")
st.markdown("작성자: 2021113295 영어영문학과 박한내") # [cite: 42]

# [FR1] 데이터 관리 (US-001) [cite: 37, 54]
st.sidebar.header("📂 데이터 관리")
uploaded_file = st.sidebar.file_uploader("학생 데이터 업로드 (CSV)", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("데이터 업로드 완료")
else:
    # 샘플 데이터 생성 (요구사항 기반 지표 포함)
    data = {
        'student_id': [f'STU_{i:03d}' for i in range(1, 13)],
        'quiz_score': [85, 45, 90, 30, 78, 55, 42, 95, 62, 38, 82, 58],
        'clicks': np.random.randint(20, 200, 12),
        'time_spent': np.random.randint(30, 200, 12),
        'interactions': np.random.randint(1, 15, 12),
        'success': [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1]
    }
    df = pd.DataFrame(data)

df, (zpd_low, zpd_high) = calculate_educational_metrics(df)

# [FR2] KPI 카드 요약 (UC-001) [cite: 37, 69]
c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 총 학생 수", f"{len(df)}명")
c2.metric("평균 성적", f"{df['quiz_score'].mean():.1f}")
c3.metric("평균 SRL지수", f"{df['SRL_Index'].mean():.2f}")
c4.metric("학습 성공률", f"{(df['success'].sum()/len(df))*100:.1f}%")

# --- 4. 시각화 탭 구성 ---
tab1, tab2, tab3 = st.tabs(["📊 성과 추적 (ZPD)", "🚨 위험 학생 감지", "🤖 AI 예측 분석"])

with tab1: # UC-001 [cite: 69]
    st.subheader("학생별 퀴즈 점수 및 ZPD 적정 구간")
    fig = px.bar(df, x='student_id', y='quiz_score', color='quiz_score', hover_data=['VARK'])
    fig.add_hline(y=zpd_low, line_dash="dash", line_color="green", annotation_text="ZPD 하한")
    fig.add_hline(y=zpd_high, line_dash="dash", line_color="red", annotation_text="ZPD 상한")
    st.plotly_chart(fig, use_container_width=True)

with tab2: # UC-002 [cite: 71]
    st.subheader("실시간 학업 위험 알림")
    fig_risk = px.scatter(df, x='SRL_Index', y='quiz_score', color='Status', size='clicks', hover_name='student_id')
    st.plotly_chart(fig_risk, use_container_width=True)
    risk_df = df[df['Status'] == '🚨 고위험']
    if not risk_df.empty:
        st.warning(f"현재 {len(risk_df)}명의 고위험군 학생이 감지되었습니다.")
        st.table(risk_df[['student_id', 'quiz_score', 'SRL_Index', 'VARK']])

with tab3: # FR3 [cite: 37]
    st.subheader("AI 기반 학습 성공 요인 분석")
    X = df[['quiz_score', 'clicks', 'time_spent', 'interactions', 'SRL_Index']]
    y = df['success']
    rf = RandomForestClassifier(n_estimators=100, random_state=42).fit(X, y)
    imp_df = pd.DataFrame({'특성': X.columns, '중요도': rf.feature_importances_}).sort_values('중요도', ascending=False)
    st.plotly_chart(px.bar(imp_df, x='중요도', y='특성', orientation='h', title="성패 결정 주요 데이터"), use_container_width=True)

# [FR5 / UC-003] 개인화 추천 및 메시징 [cite: 37, 73]
st.divider()
st.subheader("💬 개인화 추천 및 교사 도구")
target = st.selectbox("학생 선택", df['student_id'].unique())
info = df[df['student_id'] == target].iloc[0]

col_l, col_r = st.columns(2)
with col_l:
    st.info(f"**[{target}] 추천 전략**\n\n- 학습 유형: {info['VARK']}\n- SRL 수준: {info['SRL_Index']:.2f}")
    if info['Status'] == '🚨 고위험':
        st.error(f"처방: {info['VARK']} 유형 맞춤 기초 보충 자료 제공 및 1:1 면담 필요")
    else:
        st.success(f"처방: {info['VARK']} 유형 심화 프로젝트 과제 권장")

with col_r:
    st.text_area("피드백 메시지 입력 (US-005)", placeholder="학생에게 보낼 따뜻한 조언을 입력하세요.")
    if st.button("메시지 전송"):
        st.success(f"{target} 학생에게 피드백이 전송되었습니다.")

# [FR6] 보고서 생성 (US-006) [cite: 37, 61]
st.sidebar.divider()
if st.sidebar.button("📄 주간 보고서 생성"):
    st.sidebar.markdown(get_report_download_link(df), unsafe_allow_html=True)
