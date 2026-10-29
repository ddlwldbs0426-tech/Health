
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# ==================================================
# 1. 기본 설정
# ==================================================
st.set_page_config(
    page_title="건강나이 연구소",
    page_icon="🏥",
    layout="wide"
)

# ==================================================
# 2. 디자인
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background: linear-gradient(
        180deg, #eefaff 0%, #f7fbff 45%, #ffffff 100%
    );
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


# ==================================================
# 3. 건강 지표 설정
# ==================================================
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

# 시연용 표준화 값이며, 실제 의학적 기준은 아님
NOISE = {
    "수축기 혈압": 12.0,
    "이완기 혈압": 8.0,
    "공복 혈당": 10.0,
    "HDL 콜레스테롤": 12.0,
    "중성지방": 35.0,
    "허리둘레": 11.0
}


# ==================================================
# 4. 가상 연령별 건강 프로필
# ==================================================
def expected_profile(age, sex):
    """
    시연을 위해 설정한 가상 연령별 평균 프로필.
    실제 인구 자료나 의학적으로 검증된 예측식이 아니다.
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


# ==================================================
# 5. 신체 나이 추정 함수
# ==================================================
def predict_body_age(user_values, sex):
    """
    입력값과 가상 연령별 프로필 사이의 표준화 거리를 계산하고,
    거리가 가장 작은 나이를 추정 신체 나이로 선택한다.
    """
    ages = np.arange(18, 81)
    records = []

    for age in ages:
        profile = expected_profile(int(age), sex)

        weighted_distance = 0
        total_weight = 0

        for name, user_value in user_values.items():
            weight = METRICS[name]["weight"]
            scale = NOISE[name]

            difference = (user_value - profile[name]) / scale

            weighted_distance += weight * difference ** 2
            total_weight += weight

        distance = np.sqrt(weighted_distance / total_weight)

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
        return "실제 나이보다 10세 이상 낮게 추정되었어요."
    elif difference <= -3:
        return "실제 나이보다 낮게 추정되었어요."
    elif difference < 3:
        return "실제 나이와 비슷하게 추정되었어요."
    elif difference < 10:
        return "실제 나이보다 높게 추정되었어요."
    else:
        return "실제 나이보다 10세 이상 높게 추정되었어요."


# ==================================================
# 6. 세션 상태 초기화
# ==================================================
# Streamlit이 입력 변경 때마다 앱을 다시 실행하더라도
# 마지막으로 계산한 결과를 유지한다.
if "health_result" not in st.session_state:
    st.session_state.health_result = None


# ==================================================
# 7. 상단 소개
# ==================================================
st.markdown("""
<div class="hero">
    <h1>🏥 건강나이 연구소</h1>
    <p>
        실제 나이만으로는 알기 어려운 건강 지표의 연령별 특성을 살펴보세요.<br>
        입력한 건강 지표를 가상의 연령별 프로필과 비교해
        신체 나이를 추정하는 연구 시연 프로그램입니다.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="soft-blue">
<b>🔬 프로그램의 목적</b><br>
건강 지표의 조합이 어느 연령대의 가상 평균 프로필과 가장 비슷한지 계산합니다.
건강 순위를 매기는 것이 아니라, 입력한 수치를 바탕으로 연령을 추정하는
원리를 보여주는 것이 목적입니다.
</div>
""", unsafe_allow_html=True)


# ==================================================
# 8. 입력 폼
# ==================================================
st.markdown(
    '<div class="section-title">🩺 건강 정보 입력</div>',
    unsafe_allow_html=True
)

st.write(
    "건강검진 결과나 측정값을 입력해 주세요. "
    "결과는 추정 버튼을 눌렀을 때 계산됩니다."
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
            ["여", "남"]
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


# ==================================================
# 9. 버튼을 눌렀을 때만 결과 갱신
# ==================================================
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

    st.session_state.health_result = {
        "actual_age": int(actual_age),
        "sex": sex,
        "user_values": user_values,
        "predicted_age": predicted_age,
        "distances": distances.copy()
    }


# ==================================================
# 10. 마지막으로 계산한 결과 표시
# ==================================================
result = st.session_state.health_result

if result is not None:
    actual_age = result["actual_age"]
    sex = result["sex"]
    user_values = result["user_values"]
    predicted_age = result["predicted_age"]
    distances = result["distances"]

    age_difference = predicted_age - actual_age

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
            <div class="info-number">{actual_age}세</div>
            <div class="info-description">사용자가 입력한 나이</div>
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
        if age_difference > 0:
            difference_text = f"+{age_difference}세"
        else:
            difference_text = f"{age_difference}세"

        st.markdown(f"""
        <div class="info-card">
            <div class="info-label">실제 나이와의 차이</div>
            <div class="info-number">{difference_text}</div>
            <div class="info-description">
                추정 신체 나이 - 실제 나이
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(
        f"**결과 해석:** {get_age_difference_text(age_difference)}"
    )

    st.markdown("""
    <div class="notice">
    <b>꼭 확인해 주세요.</b><br>
    이 결과는 실제 건강검진 자료로 검증된 생물학적 나이가 아닙니다.
    가상의 연령별 프로필 중 입력값과 가장 가까운 것을 선택한 시연 결과입니다.
    신체 나이가 실제 나이보다 낮다고 해서 반드시 건강하다는 뜻은 아니며,
    높다고 해서 질병이 있다는 뜻도 아닙니다.
    </div>
    """, unsafe_allow_html=True)

    # ----------------------------------------------
    # 10-1. 나이별 프로필 유사도 그래프
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">📈 나이별 프로필 유사도</div>',
        unsafe_allow_html=True
    )

    st.write(
        "각 나이의 가상 평균 프로필과 입력한 건강 지표 사이의 차이입니다. "
        "거리가 작을수록 입력값과 더 비슷합니다."
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

    # X축과 Y축을 항상 같은 범위로 유지한다.
    # 입력값에 따라 그래프가 자동 확대/축소되지 않는다.
    fig.update_layout(
        xaxis_title="비교 프로필의 나이",
        yaxis_title="표준화된 차이 (작을수록 유사)",
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=45, b=15),
        height=380,
        showlegend=False,
        uirevision="fixed-age-similarity"
    )

    fig.update_xaxes(
        range=[18, 80],
        dtick=5,
        gridcolor="#eaf1f5",
        autorange=False
    )

    fig.update_yaxes(
        range=[0, 6],
        dtick=1,
        gridcolor="#eaf1f5",
        autorange=False
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        key="age_similarity_chart"
    )

    st.caption(
        "그래프의 가로축은 18~80세, 세로축은 0~6으로 고정됩니다. "
        "차이가 6을 넘는 부분은 그래프 영역 밖에 표시될 수 있습니다."
    )

    # ----------------------------------------------
    # 10-2. 지표별 비교 표
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">🧪 지표별 비교</div>',
        unsafe_allow_html=True
    )

    actual_profile = expected_profile(actual_age, sex)
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
        "표의 평균값은 프로그램 내부의 가상 수식으로 계산한 값이며, "
        "실제 인구의 연령별 평균값이 아닙니다."
    )

    # ----------------------------------------------
    # 10-3. 개별 지표 그래프
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">🔎 건강 지표 프로필 비교</div>',
        unsafe_allow_html=True
    )

    selected_metric = st.selectbox(
        "비교할 지표 선택",
        list(user_values.keys()),
        key="selected_metric"
    )

    profile_ages = np.arange(18, 81)

    profile_values = [
        expected_profile(int(age), sex)[selected_metric]
        for age in profile_ages
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
        x=[actual_age],
        y=[user_values[selected_metric]],
        mode="markers",
        name="입력값",
        marker=dict(color="#f29b38", size=13)
    ))

    fig2.add_vline(
        x=predicted_age,
        line_dash="dash",
        line_color="#16a67a",
        annotation_text=f"추정 {predicted_age}세",
        annotation_position="top"
    )

    fig2.update_layout(
        xaxis_title="나이",
        yaxis_title=(
            f"{selected_metric} "
            f"({METRICS[selected_metric]['unit']})"
        ),
        plot_bgcolor="white",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=15, r=15, t=40, b=15),
        height=370,
        uirevision=f"fixed-metric-{selected_metric}"
    )

    fig2.update_xaxes(
        range=[18, 80],
        dtick=5,
        gridcolor="#eaf1f5",
        autorange=False
    )

    # 개별 지표 그래프의 세로축은 해당 지표의
    # 전체 가상 프로필 범위와 입력값을 포함하도록 고정한다.
    y_min = min(min(profile_values), user_values[selected_metric])
    y_max = max(max(profile_values), user_values[selected_metric])
    padding = max((y_max - y_min) * 0.12, 1)

    fig2.update_yaxes(
        range=[y_min - padding, y_max + padding],
        gridcolor="#eaf1f5",
        autorange=False
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
        key="individual_metric_chart"
    )

    # ----------------------------------------------
    # 10-4. 해석 안내
    # ----------------------------------------------
    st.markdown(
        '<div class="section-title">💡 결과를 이해하는 방법</div>',
        unsafe_allow_html=True
    )

    st.markdown("""
    <div class="info-card">
    <b>1. 추정 신체 나이</b><br>
    입력한 건강 지표의 조합과 가장 가까운 가상 연령별 프로필의 나이입니다.
    실제 생물학적 노화 속도를 직접 측정한 값은 아닙니다.
    <br><br>
    <b>2. 실제 나이와의 차이</b><br>
    추정 나이에서 실제 나이를 뺀 값입니다.
    건강 상태를 종합적으로 판정하는 점수는 아닙니다.
    <br><br>
    <b>3. 나이별 프로필 유사도</b><br>
    입력한 지표와 각 나이의 가상 프로필 사이의 차이를 보여줍니다.
    그래프 축을 고정해 서로 다른 결과도 같은 기준으로 비교할 수 있습니다.
    <br><br>
    <b>4. 모델의 한계</b><br>
    운동 능력, 근력, 폐 기능, 수면, 질환 이력 등 다양한 요소가 포함되어 있지 않습니다.
    실제 건강검진 자료를 이용해 학습하거나 검증한 모델도 아닙니다.
    의료적 판단이나 질병 진단에 사용하면 안 됩니다.
    </div>
    """, unsafe_allow_html=True)

else:
    # 결과를 아직 계산하지 않은 경우
    st.markdown("---")

    st.markdown(
        '<div class="section-title">🌱 프로그램 이용 방법</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">📝</div>
            <b>STEP 1. 건강 지표 입력</b>
            <p class="info-description">
            실제 나이와 건강 지표를 입력합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
            <div style="font-size:30px;">🧮</div>
            <b>STEP 2. 프로필 비교</b>
            <p class="info-description">
            입력값과 18~80세의 가상 프로필 사이의
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
            가장 가까운 가상 연령 프로필을 표시합니다.
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.info(
        "건강 정보를 입력한 다음 '신체 나이 추정하기' 버튼을 눌러 주세요."
    )


# ==================================================
# 11. 사이드바
# ==================================================
with st.sidebar:
    st.markdown("## 🏥 건강나이 연구소")
    st.write("건강 지표와 연령별 프로필의 유사성을 탐색합니다.")

    st.markdown("---")
    st.markdown("### 📌 이용 안내")
    st.write("1. 실제 나이와 비교 프로필을 선택합니다.")
    st.write("2. 측정한 건강 지표를 입력합니다.")
    st.write("3. 추정 버튼을 눌러 결과를 계산합니다.")
    st.write("4. 그래프와 지표별 비교를 확인합니다.")

    st.markdown("---")
    st.markdown("### 🔬 데이터 안내")
    st.write(
        "현재 버전은 별도의 데이터 파일이나 API 연결 없이 "
        "작동하도록 만든 가상 데이터 기반 시연 프로그램입니다."
    )

    st.warning(
        "실제 건강검진 자료에 기반한 예측이 아니며, "
        "의학적으로 검증된 신체 나이 측정 도구가 아닙니다."
    )
