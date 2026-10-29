
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# =====================================================
# 건강나이 연구소
# 외부 데이터 파일 없이 실행되는 버전
# =====================================================

st.set_page_config(
    page_title="건강나이 연구소",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------
# 1. 디자인
# -----------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #F5F7F3;
    color: #34483D;
    font-family: "Malgun Gothic", sans-serif;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

h1, h2, h3 {
    color: #285C4D !important;
    letter-spacing: -0.6px;
}

h1 {
    font-weight: 750 !important;
}

p, label, .stMarkdown {
    color: #465B50;
}

div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E1E9E1;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 3px 12px rgba(42, 75, 57, 0.05);
}

div[data-testid="stMetricLabel"] {
    color: #63796C !important;
}

div[data-testid="stMetricValue"] {
    color: #285C4D !important;
    font-weight: 750;
}

section[data-testid="stSidebar"] {
    background-color: #EAF1EB;
    border-right: 1px solid #DCE6DC;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #285C4D !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background-color: #397765;
    color: white;
    border: 1px solid #397765;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    font-weight: 650;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #2D6253;
    color: white;
    border-color: #2D6253;
}

.stTextInput input,
.stNumberInput input {
    border-radius: 10px;
    background-color: white;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}

.hero {
    background: linear-gradient(120deg, #E4EFE7, #F9F8F2);
    border: 1px solid #DCE7DC;
    border-radius: 20px;
    padding: 30px;
    margin-bottom: 24px;
}

.hero-kicker {
    color: #53816D;
    font-size: 12px;
    font-weight: 750;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.hero-title {
    color: #285C4D;
    font-size: 30px;
    font-weight: 750;
    line-height: 1.5;
    margin-bottom: 10px;
}

.hero-description {
    color: #536B5E;
    font-size: 15px;
    line-height: 1.8;
}

.info-note {
    background: #EDF4EE;
    border-left: 4px solid #79A88E;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 12px 0 22px 0;
    color: #405D4D;
    line-height: 1.7;
}

.section-card {
    background: white;
    border: 1px solid #E1E9E1;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 15px;
}

hr {
    border-color: #DCE6DC;
}

@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    .hero {
        padding: 22px;
    }

    .hero-title {
        font-size: 24px;
    }
}
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# 2. 건강 지표 설정
# -----------------------------------------------------

VARIABLES = {
    "수축기 혈압": {
        "unit": "mmHg",
        "description": "심장이 수축할 때 혈관에 가해지는 압력입니다."
    },
    "이완기 혈압": {
        "unit": "mmHg",
        "description": "심장이 이완할 때 혈관에 가해지는 압력입니다."
    },
    "공복 혈당": {
        "unit": "mg/dL",
        "description": "공복 상태에서 측정한 혈액 속 포도당 농도입니다."
    },
    "HDL 콜레스테롤": {
        "unit": "mg/dL",
        "description": "혈중 지질 상태를 평가할 때 활용하는 지표입니다."
    },
    "중성지방": {
        "unit": "mg/dL",
        "description": "혈액 속 지방의 한 종류입니다."
    },
    "허리둘레": {
        "unit": "cm",
        "description": "복부 비만 관련 지표 중 하나입니다."
    }
}


# -----------------------------------------------------
# 3. 시뮬레이션 참고 데이터 생성
# -----------------------------------------------------

@st.cache_data
def create_demo_data():
    """
    화면 실행과 기능 시험을 위한 가상 데이터입니다.
    실제 국민건강영양조사 자료가 아닙니다.
    """

    rng = np.random.default_rng(42)
    n = 5000

    age = rng.integers(18, 81, size=n)
    sex = rng.choice(["여", "남"], size=n)

    # 나이와 개인별 차이를 단순하게 반영한 예시값
    systolic_bp = (
        105 + age * 0.35
        + np.where(sex == "남", 3, 0)
        + rng.normal(0, 12, n)
    )

    diastolic_bp = (
        66 + age * 0.10
        + np.where(sex == "남", 2, 0)
        + rng.normal(0, 8, n)
    )

    fasting_glucose = (
        82 + age * 0.16
        + rng.normal(0, 12, n)
    )

    hdl = (
        57
        + np.where(sex == "여", 5, 0)
        - age * 0.04
        + rng.normal(0, 12, n)
    )

    triglycerides = rng.lognormal(
        mean=np.log(115 + age * 0.35),
        sigma=0.45,
        size=n
    )

    waist_cm = (
        68 + age * 0.12
        + np.where(sex == "남", 12, 0)
        + rng.normal(0, 9, n)
    )

    df = pd.DataFrame({
        "age": age,
        "sex": sex,
        "수축기 혈압": np.clip(systolic_bp, 75, 240),
        "이완기 혈압": np.clip(diastolic_bp, 40, 150),
        "공복 혈당": np.clip(fasting_glucose, 55, 250),
        "HDL 콜레스테롤": np.clip(hdl, 15, 130),
        "중성지방": np.clip(triglycerides, 25, 900),
        "허리둘레": np.clip(waist_cm, 45, 160)
    })

    return df


reference_data = create_demo_data()


# -----------------------------------------------------
# 4. 백분위 계산 함수
# -----------------------------------------------------

def calculate_percentile(values, user_value):
    """
    참고 데이터에서 입력값 이하에 해당하는 비율을 계산합니다.
    시뮬레이션 데이터용 단순 백분위입니다.
    """

    values = pd.Series(values).dropna()

    if len(values) == 0:
        return None

    return float((values <= user_value).mean() * 100)


def get_percentile_text(percentile):
    if percentile is None:
        return "계산할 수 없습니다."

    if percentile < 25:
        return "참고 집단의 하위 25% 범위"
    elif percentile < 50:
        return "참고 집단의 25~50% 범위"
    elif percentile < 75:
        return "참고 집단의 50~75% 범위"
    else:
        return "참고 집단의 상위 25% 범위"


# -----------------------------------------------------
# 5. 사이드바
# -----------------------------------------------------

with st.sidebar:
    st.markdown("# 🌿 건강나이 연구소")
    st.caption("나의 건강을 이해하는 공간")

    st.divider()

    st.markdown("### 이용 방법")
    st.write("**01** 기본 정보를 입력합니다.")
    st.write("**02** 건강검진 수치를 입력합니다.")
    st.write("**03** 비슷한 연령대와 비교합니다.")

    st.divider()

    st.markdown("### 데이터 안내")
    st.write(
        "현재는 프로그램 작동을 확인하기 위한 "
        "가상 데이터를 사용합니다."
    )

    st.caption(
        "비교 결과는 실제 인구 통계나 의학적 진단이 아닙니다."
    )


# -----------------------------------------------------
# 6. 첫 화면
# -----------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-kicker">
        PERSONAL HEALTH INFORMATION
    </div>

    <div class="hero-title">
        나의 건강을 이해하는 첫걸음
    </div>

    <div class="hero-description">
        건강 지표를 입력하고 비슷한 연령대의 가상 참고 데이터와 비교해 보세요.<br>
        나의 건강 상태를 이해하는 데 도움이 되는 정보를 확인할 수 있습니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-note">
    <b>현재 체험 모드입니다.</b><br>
    실제 건강 조사 자료가 아닌 가상 데이터로 결과를 계산합니다.
    따라서 실제 또래 집단의 건강 상태를 나타내지 않으며,
    질병이나 생물학적 나이를 판정하는 데 사용할 수 없습니다.
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------
# 7. 기본 정보 입력
# -----------------------------------------------------

st.markdown("## 1. 기본 정보 입력")
st.caption("나이와 성별을 선택한 뒤 비교할 건강검진 수치를 입력하세요.")

with st.form("health_form"):

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "만 나이",
            min_value=18,
            max_value=80,
            value=30,
            step=1
        )

    with col2:
        sex = st.selectbox(
            "성별",
            ["여", "남"]
        )

    age_range = st.radio(
        "비교 연령 범위",
        ["같은 10세 연령대", "±5세"],
        horizontal=True
    )

    st.markdown("### 건강검진 수치")

    col1, col2, col3 = st.columns(3)

    with col1:
        systolic_bp = st.number_input(
            "수축기 혈압 (mmHg)",
            min_value=0.0,
            max_value=300.0,
            value=None,
            placeholder="예: 115"
        )

        diastolic_bp = st.number_input(
            "이완기 혈압 (mmHg)",
            min_value=0.0,
            max_value=200.0,
            value=None,
            placeholder="예: 75"
        )

    with col2:
        fasting_glucose = st.number_input(
            "공복 혈당 (mg/dL)",
            min_value=0.0,
            max_value=800.0,
            value=None,
            placeholder="예: 90"
        )

        hdl = st.number_input(
            "HDL 콜레스테롤 (mg/dL)",
            min_value=0.0,
            max_value=300.0,
            value=None,
            placeholder="예: 55"
        )

    with col3:
        triglycerides = st.number_input(
            "중성지방 (mg/dL)",
            min_value=0.0,
            max_value=2000.0,
            value=None,
            placeholder="예: 100"
        )

        waist_cm = st.number_input(
            "허리둘레 (cm)",
            min_value=0.0,
            max_value=250.0,
            value=None,
            placeholder="예: 75"
        )

    submitted = st.form_submit_button(
        "건강 지표 비교하기",
        use_container_width=True
    )


# -----------------------------------------------------
# 8. 결과 계산
# -----------------------------------------------------

if submitted:

    user_values = {
        "수축기 혈압": systolic_bp,
        "이완기 혈압": diastolic_bp,
        "공복 혈당": fasting_glucose,
        "HDL 콜레스테롤": hdl,
        "중성지방": triglycerides,
        "허리둘레": waist_cm
    }

    entered_values = {
        name: value
        for name, value in user_values.items()
        if value is not None
    }

    if not entered_values:
        st.warning("비교할 건강 지표를 하나 이상 입력해 주세요.")
        st.stop()

    # 연령대 설정
    if age_range == "같은 10세 연령대":
        age_min = (int(age) // 10) * 10
        age_max = age_min + 9
    else:
        age_min = max(18, int(age) - 5)
        age_max = min(80, int(age) + 5)

    # 같은 성별 및 연령대의 참고 데이터 선택
    comparison = reference_data[
        (reference_data["age"] >= age_min)
        & (reference_data["age"] <= age_max)
        & (reference_data["sex"] == sex)
    ]

    st.markdown("## 2. 건강 지표 비교 결과")

    col1, col2, col3 = st.columns(3)

    col1.metric("입력한 나이", f"{age}세")
    col2.metric(
        "비교 연령대",
        f"{age_min}~{age_max}세"
    )
    col3.metric(
        "가상 참고 데이터",
        f"{len(comparison):,}명"
    )

    st.caption(
        "참고 데이터 수는 실제 조사 참여자 수가 아니라 "
        "프로그램에서 생성한 가상 데이터의 수입니다."
    )

    result_rows = []
    chart_rows = []

    for name, user_value in entered_values.items():

        unit = VARIABLES[name]["unit"]
        values = comparison[name]

        if values.dropna().empty:
            continue

        median = values.median()

        percentile = calculate_percentile(
            values,
            user_value
        )

        result_rows.append({
            "건강 지표": name,
            "입력값": f"{user_value:g} {unit}",
            "가상 참고 집단 중앙값": f"{median:.1f} {unit}",
            "백분위 위치": f"{percentile:.1f}%",
            "참고 위치": get_percentile_text(percentile)
        })

        chart_rows.append({
            "건강 지표": name,
            "백분위 위치": percentile
        })

    # 결과 표
    result_df = pd.DataFrame(result_rows)

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    # -------------------------------------------------
    # 9. 그래프
    # -------------------------------------------------

    if chart_rows:

        st.markdown("### 참고 집단 안에서의 상대적 위치")

        chart_df = pd.DataFrame(chart_rows)

        fig = px.bar(
            chart_df,
            x="건강 지표",
            y="백분위 위치",
            range_y=[0, 100],
            text=chart_df["백분위 위치"].map(
                lambda x: f"{x:.0f}%"
            ),
            labels={
                "건강 지표": "건강 지표",
                "백분위 위치": "백분위 위치(%)"
            }
        )

        fig.update_traces(
            marker_color="#6FA38D",
            textposition="outside"
        )

        fig.update_layout(
            paper_bgcolor="#F5F7F3",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="Malgun Gothic, sans-serif",
                color="#40584B"
            ),
            margin=dict(l=15, r=15, t=25, b=15),
            yaxis=dict(
                gridcolor="#E5ECE5",
                title="백분위 위치(%)"
            ),
            xaxis=dict(title=None)
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # -------------------------------------------------
    # 10. 지표 설명
    # -------------------------------------------------

    st.markdown("### 입력한 지표 알아보기")

    for name in entered_values:
        with st.expander(name):
            st.write(VARIABLES[name]["description"])

    st.markdown("### 결과 해석 시 주의할 점")

    st.markdown("""
    백분위는 입력한 수치가 가상 참고 데이터에서 어느 위치에 있는지 보여줍니다.
    백분위가 높거나 낮다는 사실만으로 건강 상태가 좋거나 나쁘다고 단정할 수 없습니다.

    특히 HDL 콜레스테롤은 다른 지표와 해석 방향이 다를 수 있습니다.
    개인의 건강 상태, 측정 조건, 나이 및 다른 검사 결과를 함께 고려해야 합니다.
    이 결과는 실제 건강검진 통계가 아니며 의료진의 판단을 대신하지 않습니다.
    """)


# -----------------------------------------------------
# 11. 하단 안내
# -----------------------------------------------------

st.divider()

st.markdown("### 건강나이 연구소 안내")

st.caption("""
이 프로그램은 교육 및 화면 기능 확인을 위한 시뮬레이션입니다.
실제 건강 조사 자료나 검증된 생물학적 나이 계산 모델을 사용하지 않습니다.
건강 상태에 대한 진단과 판단은 의료진과 상담하세요.
""")
