# campus_life.py
import os
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# ---------------------------------------------------------
# 1. Page Configuration & Font Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="인문사회대 캠퍼스 생활 설문 결과",
    layout="wide"
)

st.title("인문사회대 캠퍼스 생활 설문 결과")

# 한글 폰트 설정 (NanumGothic.ttf 파일 우선 적용)
font_file = "NanumGothic.ttf"

if os.path.exists(font_file):
    fm.fontManager.addfont(font_file)
    font_prop = fm.FontProperties(fname=font_file)
    font_name = font_prop.get_name()
    plt.rc('font', family=font_name)
else:
    plt.rc('font', family='Malgun Gothic')

plt.rc('axes', unicode_minus=False)

# Seaborn 트렌디한 백그라운드 스타일 설정
sns.set_theme(style="whitegrid", font="NanumGothic" if os.path.exists(font_file) else "Malgun Gothic")
plt.rc('axes', unicode_minus=False)

# ---------------------------------------------------------
# 2. CSV File Upload & Data Preview
# ---------------------------------------------------------
st.header("1. CSV 파일 업로드 및 데이터 미리보기")
uploaded_file = st.file_uploader("campus_life.csv 파일을 업로드해주세요.", type=["csv"])

if uploaded_file is not None:
    df_raw = pd.read_csv(uploaded_file)

    st.subheader("원본 데이터 미리보기")
    st.dataframe(df_raw.head())

    # ---------------------------------------------------------
    # 3. Data Preprocessing & Excluded Rows Display
    # ---------------------------------------------------------
    st.header("2. 데이터 전처리 결과")

    numeric_cols = ["통학시간", "공부시간", "스마트폰", "수면시간", "만족도"]

    # 1) 숫자형 타입으로 변환 (잘못된 문자는 NaN 처리)
    df_temp = df_raw.copy()
    for col in numeric_cols:
        df_temp[col] = pd.to_numeric(df_temp[col], errors='coerce')

    # 2) 결측치 및 이상치 검사
    missing_mask = df_temp[numeric_cols].isnull().any(axis=1) | df_temp[["응답ID", "학과", "학년", "한줄의견"]].isnull().any(
        axis=1)

    out_of_bounds_mask = (
            (df_temp["공부시간"] < 0) | (df_temp["공부시간"] > 24) |
            (df_temp["스마트폰"] < 0) | (df_temp["스마트폰"] > 24) |
            (df_temp["수면시간"] < 0) | (df_temp["수면시간"] > 24) |
            (df_temp["만족도"] < 1) | (df_temp["만족도"] > 10) |
            (df_temp["통학시간"] < 0)
    )

    invalid_mask = missing_mask | out_of_bounds_mask
    df_cleaned = df_temp[~invalid_mask].copy()

    excluded_count = invalid_mask.sum()
    valid_count = len(df_cleaned)

    col1, col2, col3 = st.columns(3)
    col1.metric("전체 데이터 수", f"{len(df_raw)}건")
    col2.metric("정상 데이터 수", f"{valid_count}건")
    col3.metric("제외된 데이터 수 (결측/이상치)", f"{excluded_count}건")

    if excluded_count > 0:
        st.caption("※ 제외된 잘못된/누락된 데이터 목록:")
        st.dataframe(df_raw[invalid_mask])

    # ---------------------------------------------------------
    # 4. Department Filter & Satisfaction Summary
    # ---------------------------------------------------------
    st.header("3. 소속 학과 선택 및 분석")

    departments = ["전체"] + list(df_cleaned["학과"].unique())
    selected_dept = st.selectbox("학과를 선택하세요:", departments)

    if selected_dept != "전체":
        df_filtered = df_cleaned[df_cleaned["학과"] == selected_dept]
    else:
        df_filtered = df_cleaned.copy()

    avg_satisfaction = df_filtered["만족도"].mean() if not df_filtered.empty else 0
    st.metric(
        label=f"[{selected_dept}] 선택 인원의 평균 학교생활 만족도",
        value=f"{avg_satisfaction:.2f}점 / 10점"
    )

    # ---------------------------------------------------------
    # 5. Visualizations (Pastel Blue & Vibrant Styling)
    # ---------------------------------------------------------
    st.header("4. 설문 결과 시각화")

    if not df_filtered.empty:
        col_g1, col_g2 = st.columns(2)

        # Graph 1: Line plot (Pastel Blue / Mint / Coral Accent)
        with col_g1:
            st.subheader("생활 시간(공부, 수면, 스마트폰)과 만족도 관계")
            fig1, ax1 = plt.subplots(figsize=(6, 4))

            df_sorted = df_filtered.sort_values(by="만족도")

            # 파스텔 블루 계열 구분을 위한 선명한 파스텔 팔레트
            ax1.plot(df_sorted["만족도"], df_sorted["공부시간"], marker='o', color='#4A90E2', linewidth=2.5, label="공부시간 (시간)")
            ax1.plot(df_sorted["만족도"], df_sorted["수면시간"], marker='s', color='#50E3C2', linewidth=2.5, label="수면시간 (시간)")
            ax1.plot(df_sorted["만족도"], df_sorted["스마트폰"], marker='^', color='#F5A623', linewidth=2.5,
                     label="스마트폰 사용시간 (시간)")

            ax1.set_title(f"[{selected_dept}] 만족도별 주요 생활 시간 분포", fontsize=12, fontweight='bold', pad=12)
            ax1.set_xlabel("학교생활 만족도 (점수: 1~10)", fontsize=10)
            ax1.set_ylabel("시간 (시간/일)", fontsize=10)
            ax1.legend(frameon=True, facecolor='white', edgecolor='none')
            ax1.grid(True, linestyle=":", alpha=0.6)

            st.pyplot(fig1)

        # Graph 2: Heatmap (Soft Pastel Blue Colormap)
        with col_g2:
            st.subheader("주요 항목 간 상관관계 히트맵")
            fig2, ax2 = plt.subplots(figsize=(6, 4))

            corr_matrix = df_filtered[numeric_cols].corr()
            sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap="Blues", cbar=True, ax=ax2,
                        annot_kws={"size": 9}, linewidths=0.5, linecolor='white')

            ax2.set_title(f"[{selected_dept}] 주요 항목 간 상관관계", fontsize=12, fontweight='bold', pad=12)
            st.pyplot(fig2)

        # ---------------------------------------------------------
        # 6. One-line Opinion Analysis (Word Frequency & Sentiment)
        # ---------------------------------------------------------
        st.header("5. 한 줄 의견 분석 (학과 선택 필터 연동)")

        opinions = df_filtered["한줄의견"].dropna().tolist()

        # 긍정/부정 단어 사전
        pos_keywords = ["좋다", "좋음", "만족", "최고", "유익", "쾌적", "친절", "즐겁", "재밌", "편함", "좋아요", "만족스럽"]
        neg_keywords = ["불편", "부족", "별로", "최악", "아쉽", "힘듦", "지루", "소음", "복잡", "개선", "어렵", "불만"]

        pos_count = 0
        neg_count = 0
        words = []

        for op in opinions:
            op_str = str(op)
            words.extend([w.strip() for w in op_str.split() if len(w.strip()) > 1])

            for pos in pos_keywords:
                if pos in op_str:
                    pos_count += 1
            for neg in neg_keywords:
                if neg in op_str:
                    neg_count += 1

        # 긍정/부정 단어 등장 횟수 표시
        col_pos, col_neg, col_total = st.columns(3)
        col_pos.metric("긍정 단어 등장 횟수", f"{pos_count}회")
        col_neg.metric("부정 단어 등장 횟수", f"{neg_count}회")
        total_opinions = len(opinions)
        col_total.metric("분석 대상 의견 수", f"{total_opinions}건")

        # 상위 10개 단어 시각화 (Pastel Blue Gradient)
        st.subheader(f"[{selected_dept}] 한 줄 의견 상위 10개 주요 등장 단어")
        if words:
            word_counts = pd.Series(words).value_counts().head(10)

            fig3, ax3 = plt.subplots(figsize=(8, 4))

            # 파스텔 블루 트렌디 팔레트 적용
            pastel_blue_palette = sns.color_palette("ch:start=.5,rot=-.5", len(word_counts))
            sns.barplot(x=word_counts.values, y=word_counts.index, palette=pastel_blue_palette, ax=ax3)

            ax3.set_title(f"[{selected_dept}] 자주 등장하는 단어 Top 10", fontsize=12, fontweight='bold', pad=12)
            ax3.set_xlabel("빈도수 (회)", fontsize=10)
            ax3.set_ylabel("단어", fontsize=10)

            # 숫자 텍스트 표시
            for i, v in enumerate(word_counts.values):
                ax3.text(v + 0.1, i, str(v), va='center', fontsize=9, color='#333333', fontweight='bold')

            st.pyplot(fig3)
        else:
            st.info("해당 학과의 한 줄 의견 데이터가 없습니다.")

    else:
        st.warning("선택한 학과의 데이터가 존재하지 않습니다.")
