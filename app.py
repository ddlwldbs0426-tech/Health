
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --------------------------------------------------
# 1. 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="건강나이 연구소",
    page_icon="🏥",
    layout="wide"
)

# --------------------------------------------------
# 2. 디자인
# --------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background: linear-gradient(180deg, #eefaff 0%, #f7fbff 45%, #ffffff 100%);
}

.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1250px;
}

.hero {
    background: linear-gradient(120deg, #168eea 0%, #28c6c9 100%);
    padding: 32px;
    border-radius: 24px;
    color: white;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(31, 150, 205, 0.18);
}

.hero h1 {
    font-size: 34px;
    font-weight: 800;
    margin: 0 0 10px 0;
}

.hero p {
    font-size: 16px;
    margin: 0;
    line-height: 1.7;
}

.section-title {
    color: #174b75;
    font-size: 23px;
    font-weight: 800;
    margin-top: 20px;
    margin-bottom: 12px;
}

.info-card {
    background: white;
    border: 1px solid #dceef7;
    border-radius: 18px;
    padding: 20px;
    box-shadow: 0 4px 14px rgba(48, 112, 145, 0.06);
    height: 100%;
}

.info-label {
    color: #66869a;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
}

.info-number {
    color: #1379c6;
    font-size: 30px;
    font-weight: 800;
}

.info-description {
    color: #597487;
    font-size: 13px;
    margin-top: 7px;
    line-height: 1.5;
}

.notice {
    background: #fff8e7;
    border: 1px solid #f5dfa0;
    border-radius: 14px;
    padding: 16px;
    color: #77571b;
    line-height: 1.7;
    margin: 14px 0;
}

.soft-blue {
    background: #eaf7ff;
    border: 1px solid #cfeaff;
    border-radius: 15px;
    padding: 17px;
    color: #205879;
    line-height: 1.7;
}

.stButton > button {
    background: linear-gradient(100deg, #168eea, #21b9c8);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.7rem 1rem;
    font-weight: 700;
}

.stButton > button:hover {
    color: white;
    border: none;
    filter: brightness(1.04);
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #dceef7;
    padding: 16px;
    border-radius: 16px;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 3. 시연용 연령별 기준 프로필
#    실제 조사 데이터가 아닌 가상 모델
# --------------------------------------------------
METRICS = {
    "수축기 혈압": {
        "unit": "mmHg",
        "low": 70,
        "high": 220,
        "weight": 1.0
    },
    "이완기 혈압": {
        "unit": "mmHg",
        "low": 40,
        "high": 130,
        "weight": 0.8
    },
    "공복 혈당": {
        "unit": "mg/dL",
        "low": 50,
        "high": 300,
        "weight": 1.0
    },
    "HDL 콜레스테롤": {
        "unit": "mg/dL",
        "low": 10,
        "high": 150,
        "weight": 0.7
    },
    "중성지방": {
        "unit": "mg/dL",
        "low": 20,
        "high": 1000,
        "weight": 0.7
    },
    "허리둘레": {
        "unit": "cm",
        "low": 40,
        "high": 180,
        "weight": 0.7
    }
}

# 측정값의 일반적인 개인차를 반영하기 위한
# 시연용 표준편차 설정. 의학적 기준값이 아님.
NOISE = {
    "수축기 혈압": 12.0,
    "이완기 혈압": 8.0,
    "공복 혈당": 10.0,
    "HDL 콜레스테롤": 12.0,
    "중성지방": 35.0,
    "허리둘레": 11.0
}


def expected_profile(age, sex):
    """
    나이에 따른 가상의 평균 건강 지표를 생성한다.
    이 수식은 실제 인구 조사나 의학 연구에서 추출한
    회귀식이 아니라 프로그램 시연을 위한 가정이다.
    """
    t = age - 18

    if sex == "남":
        hdl_base = 53
        waist_base = 80
        waist_slope = 0.20
    else:
        hdl_base = 62
        waist_base = 69
        waist_slope = 0.18

    return {
        "수축기 혈압": 112 + 0.35 * t,
        "이완기 혈압": 70 + 0.08 * t,
        "공복 혈당": 86 + 0.16 * t,
        "HDL 콜레스테롤": hdl_base - 0.07 * t,
        "중성지방": 85 + 0.65 * t,
        "허리둘레": waist_base + waist_slope * t
    }


def predict_body_age(user_values, sex):
    """
    사용자 측정값과 각 나이의 가상 평균 프로필 사이의
    표준화 거리를 계산하고, 가장 가까운 나이를 선택한다.

    이는 시연용 유사도 모델이며 검증된 생물학적 나이
    예측 알고리즘이 아니다.
    """
    ages = np.arange(18, 81)
    records = []

    for age in ages:
        profile = expected_profile(age, sex)
        weighted_squared_distance = 0
        total_weight = 0

        for name, user_value in user_values.items():
            weight = METRICS[name]["weight"]
            scale = NOISE[name]

            difference = (user_value - profile[name]) / scale

            weighted_squared_distance += weight * difference ** 2
            total_weight += weight

        distance = np.sqrt(
            weighted_squared_distance / total_weight
        )

        records.append({
            "나이": int(age),
            "거리": float(distance)
        })

    distances = pd.DataFrame(records)
    predicted_age = int(
        distances.loc[distances["거리"].idxmin(), "나이"]
    )

    return predicted_age, distances


def get_age_difference_text(difference):
    if difference <= -10:
        return "입력한 실제 나이보다 상당히 낮게 추정되었어요."
    elif difference <= -3:
        return "입력한 실제 나이보다 낮게 추정되었어요."
    elif difference < 3:
        return "입력한 실제 나이와 비슷하게 추정되었어요."
    elif difference < 10:
        return "입력한 실제 나이보다 높게 추정되었어요."
    else:
        return "입력한 실제 나이보다 상당히 높게 추정되었어요."


# --------------------------------------------------
# 4. 화면 상단
# --------------------------------------------------
st.markdown("""
<div class="hero">
    <h1>🏥 건강나이 연구소</h1>
    <p>
        실제 나이만으로는 알기 어려운 건강 지표의 연령별 특성을 살펴보세요.<br>
        입력한 수치를 가상의 연령별 프로필과 비교해
        신체 나이를 추정하는 연구 시연 프로그램입니다.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="soft-blue">
<b>🔬 프로그램의 목적</b><br>
혈압, 혈당, 콜레스테롤, 허리둘레 등의 측정값이
어느 연령대의 가상 평균 프로필과 가장 비슷한지 계산합니다.
건강 순위를 매기는 것이 아니라, 건강 지표의 조합을
바탕으로 연령을 추정하는 원리를 보여주는 것이 목적입니다.
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 5. 입력 화면
# --------------------------------------------------
st.markdown(
    '<div class="section-title">🩺 건강 정보 입력</div>',
    unsafe_allow_html=True
)

st.write(
    "건강검진 결과나 측정값을 입력해 주세요. "
    "측정하지 않은 값을 임의로 입력하면 추정 결과의 의미가 줄어들 수 있어요."
)

with st.form("health_form"):
    col1, col2 = st.columns(2)

    with col1:
        actual_age = st.number_input(
            "실제 나이",
            min_value=18,
            max_value=80,
            value=30,
            step=1
        )

    with col2:
        sex = st.selectbox(
            "비교 프로필",
            ["여", "남"],
            help="시연용 기준 프로필을 선택합니다."
        )

    st.markdown("#### 건강 지표")

    c1, c2, c3 = st.columns(3)

    with c1:
        systolic = st.number_input(
            "수축기 혈압 (mmHg)",
            min_value=70,
            max_value=220,
            value=120
        )
        glucose = st.number_input(
            "공복 혈당 (mg/dL)",
            min_value=50,
            max_value=300,
            value=95
        )

    with c2:
        diastolic = st.number_input(
            "이완기 혈압 (mmHg)",
            min_value=40,
            max_value=130,
            value=80
        )
        hdl = st.number_input(
            "HDL 콜레스테롤 (mg/dL)",
            min_value=10,
            max_value=150,
            value=55
        )

    with c3:
        triglycerides = st.number_input(
            "중성지방 (mg/dL)",
            min_value=20,
            max_value=1000,
            value=100
        )
        waist = st.number_input(
            "허리둘레 (cm)",
            min_value=40,
            max_value=180,
            value=80
        )

    submitted = st.form_submit_button(
        "✨ 신체 나이 추정하기",
        use_container_width=True
    )

# --------------------------------------------------
# 6. 추정 결과
# --------------------------------------------------
if submitted:
    user_values = {
        "수축기 혈압": float(systolic),
        "이완기 혈압": float(diastolic),
        "공복 혈당": float(glucose),
        "HDL 콜레스테롤": float(hdl),
        "중성지방": float(triglycerides),
        "허리둘레": float(waist)
    }

    predicted_age, distances = predict_body_age(
        user_values,
        sex
    )

    age_difference = predicted_age - int(actual_age)

    st.markdown("---")
    st.markdown(
        '<div class="section-title">📊 추정 결과</div>',
        unsafe_allow_html=True
    )

    result_col1, result_col2, result_col3 = st.columns(3)

    with result_col1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">입력한 실제 나이</div>
            <div class="info-number">{int(actual_age)}세</div>
            <div class="info-description">
                사용자가 입력한 나이
            </div>
        </div>
        """, unsafe_allow_html=True)

    with result_col2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">모델 추정 신체 나이</div>
            <div class="info-number">{predicted_age}세</div>
            <div class="info-description">
                가상 연령별 프로필과 가장 가까운 나이
            </div>
        </div>
        """, unsafe_allow_html=True)

    with result_col3:
        if age_difference < 0:
            difference_text = f"{age_difference}세"
        elif age_difference > 0:
            difference_text = f"+{age_difference}세"
        else:
            difference_text = "0세"

        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">실제 나이와의 차이</div>
            <div class="info-number">{difference_text}</div>
            <div class="info-description">
                추정 신체 나이 − 실제 나이
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    st.markdown(
        f"**결과 해석:** {get_age_difference_text(age_difference)}"
    )

    st.markdown("""
    <div class="notice">
    <b>꼭 확인해 주세요.</b><br>
    이 결과는 실제 건강검진 자료로 검증된 생물학적 나이가 아닙니다.
    가상의 수식으로 만든 연령별 프로필 중 입력값과 가장 가까운 것을
    선택한 시연 결과입니다. 신체 나이가 실제 나이보다 낮다고 해서
    반드시 건강하다는 뜻은 아니며, 높다고 해서 질병이 있다는 뜻도 아닙니다.
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------
    # 7. 나이별 유사도
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">📈 나이별 프로필 유사도</div>',
        unsafe_allow_html=True
    )

    st.write(
        "아래 그래프는 각 나이의 가상 평균 프로필과 "
        "입력한 건강 지표 사이의 차이를 나타냅니다. "
        "거리 값이 작을수록 입력값과 더 비슷합니다."
    )

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=distances["나이"],
        y=distances["거리"],
        mode="lines",
        name="프로필 차이",
        line=dict(color="#1c9fd1", width=3),
        fill="tozeroy",
        fillcolor="rgba(28,159,209,0.10)"
    ))

    fig.add_vline(
        x=predicted_age,
        line_dash="dash",
        line_color="#f29b38",
        annotation_text=f"추정 {predicted_age}세",
        annotation_position="top"
    )

    fig.update_layout(
        xaxis_title="비교 프로필의 나이",
        yaxis_title="표준화된 차이 (작을수록 유사)",
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=45, b=15),
        height=380,
        showlegend=False
    )

    fig.update_xaxes(
        dtick=5,
        gridcolor="#eaf1f5"
    )
    fig.update_yaxes(
        gridcolor="#eaf1f5",
        rangemode="tozero"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------------------------------------
    # 8. 지표별 입력값과 추정 프로필 비교
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">🧪 지표별 비교</div>',
        unsafe_allow_html=True
    )

    actual_profile = expected_profile(int(actual_age), sex)
    predicted_profile = expected_profile(predicted_age, sex)

    comparison_rows = []

    for name, user_value in user_values.items():
        comparison_rows.append({
            "건강 지표": name,
            "입력값": round(user_value, 1),
            "실제 나이 기준 가상 평균": round(
                actual_profile[name], 1
            ),
            "추정 나이 기준 가상 평균": round(
                predicted_profile[name], 1
            ),
            "단위": METRICS[name]["unit"]
        })

    comparison_df = pd.DataFrame(comparison_rows)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    st.caption(
        "표의 평균값은 모두 프로그램 내부의 가상 수식으로 계산했습니다. "
        "실제 인구의 연령별 평균값이 아닙니다."
    )

    # ----------------------------------------------
    # 9. 입력값과 연령별 프로필 시각화
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">🔎 건강 지표 프로필 비교</div>',
        unsafe_allow_html=True
    )

    selected_metric = st.selectbox(
        "비교할 지표 선택",
        list(user_values.keys())
    )

    profile_ages = np.arange(18, 81)
    profile_values = [
        expected_profile(int(a), sex)[selected_metric]
        for a in profile_ages
    ]

    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=profile_ages,
        y=profile_values,
        mode="lines",
        name="가상 연령별 평균",
        line=dict(color="#159ed1", width=3)
    ))

    fig2.add_trace(go.Scatter(
        x=[int(actual_age)],
        y=[user_values[selected_metric]],
        mode="markers",
        name="입력값 위치(실제 나이)",
        marker=dict(color="#f29b38", size=13, symbol="circle")
    ))

    fig2.add_trace(go.Scatter(
        x=[predicted_age],
        y=[user_values[selected_metric]],
        mode="markers",
        name="입력값을 표시한 추정 나이",
        marker=dict(color="#16a67a", size=13, symbol="diamond")
    ))

    fig2.update_layout(
        xaxis_title="나이",
        yaxis_title=f"{selected_metric} ({METRICS[selected_metric]['unit']})",
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=30, b=15),
        height=370,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0
        )
    )

    fig2.update_xaxes(
        dtick=5,
        gridcolor="#eaf1f5"
    )
    fig2.update_yaxes(gridcolor="#eaf1f5")

    st.plotly_chart(fig2, use_container_width=True)

    # ----------------------------------------------
    # 10. 해석 안내
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">💡 결과를 이해하는 방법</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
    <b>1. 추정 신체 나이</b><br>
    입력한 여러 건강 지표의 조합과 가장 가까운 가상 연령별 프로필의 나이입니다.
    실제 생물학적 노화 속도를 직접 측정한 값은 아닙니다.
    <br><br>
    <b>2. 실제 나이와의 차이</b><br>
    추정 나이에서 실제 나이를 뺀 값입니다.
    이 차이는 시연 모델의 추정 결과를 설명하기 위한 것이며,
    건강 상태를 종합적으로 판정하는 점수는 아닙니다.
    <br><br>
    <b>3. 지표별 비교</b><br>
    각 지표가 실제 나이와 추정 나이의 가상 프로필에서
    어떤 값으로 설정되어 있는지 비교할 수 있습니다.
    <br><br>
    <b>4. 모델의 한계</b><br>
    이 모델에는 운동 능력, 근력, 폐 기능, 수면, 질환 이력 등
    다양한 요소가 포함되어 있지 않습니다. 또한 지표별 나이 변화는
    실제 사람에게서 측정한 결과가 아니라 시연용 가정입니다.
    따라서 이 프로그램을 의료적 판단이나 질병 진단에 사용하면 안 됩니다.
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("---")
    st.markdown(
        '<div class="section-title">🌱 이 프로그램은 어떻게 작동할까요?</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">📝</div>
            <b>STEP 1. 건강 지표 입력</b>
            <p class="info-description">
            실제 나이와 혈압, 혈당, 콜레스테롤,
            허리둘레 등의 측정값을 입력합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">🧮</div>
            <b>STEP 2. 연령별 프로필 비교</b>
            <p class="info-description">
            입력값과 18~80세의 가상 평균 프로필 사이의
            차이를 계산합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">🎯</div>
            <b>STEP 3. 신체 나이 추정</b>
            <p class="info-description">
            입력한 지표의 조합과 가장 가까운
            가상 연령 프로필을 표시합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "먼저 건강 정보를 입력하고 '신체 나이 추정하기'를 눌러 보세요."
    )

# --------------------------------------------------
# 11. 사이드바
# --------------------------------------------------
with st.sidebar:
    st.markdown("## 🏥 건강나이 연구소")
    st.write("건강 지표와 연령별 프로필의 유사성을 탐색합니다.")

    st.markdown("---")
    st.markdown("### 📌 이용 안내")
    st.write("1. 실제 나이와 비교 프로필을 선택합니다.")
    st.write("2. 측정한 건강 지표를 입력합니다.")
    st.write("3. 추정 나이와 비교 그래프를 확인합니다.")

    st.markdown("---")
    st.markdown("### 🔬 데이터 안내")
    st.write(
        "현재 버전은 별도의 파일 다운로드나 API 연결 없이 "
        "작동하도록 만든 가상 데이터 기반 시연 프로그램입니다."
    )

    st.warning(
        "실제 건강검진 데이터에 기반한 예측이 아니며, "
        "의학적으로 검증된 신체 나이 측정 도구가 아닙니다."
    )
