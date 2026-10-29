
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ======================================================
# 건강나이 연구소
# 밝고 생동감 있는 병원·건강검진센터 스타일
# 외부 데이터 파일 없이 실행 가능
# ======================================================

st.set_page_config(
    page_title="건강나이 연구소",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------
# 1. 화면 디자인
# ------------------------------------------------------

st.markdown("""
<style>
/* 전체 배경 */
.stApp {
    background:
        radial-gradient(ellipse at 5% 5%,
            rgba(87, 194, 211, 0.17), transparent 28%),
        radial-gradient(ellipse at 95% 20%,
            rgba(106, 170, 239, 0.15), transparent 27%),
        linear-gradient(180deg, #F1F8FF 0%, #F8FBFF 48%, #F2F8FC 100%);
    color: #243B53;
    font-family: "Malgun Gothic", "Apple SD Gothic Neo", sans-serif;
}

.block-container {
    max-width: 1200px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

/* 제목 */
h1, h2, h3 {
    color: #174C78 !important;
    letter-spacing: -0.7px;
}

h1 {
    font-weight: 800 !important;
}

h2, h3 {
    font-weight: 750 !important;
}

/* 본문 */
p, label, .stMarkdown {
    color: #40566D;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #E3F3FF, #F1F8FF);
    border-right: 1px solid #D2E6F5;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #174C78 !important;
}

/* 첫 화면 메인 배너 */
.hero {
    background: linear-gradient(115deg, #1769AA 0%, #248DC5 58%, #54BCD0 100%);
    border-radius: 24px;
    padding: 34px;
    margin-bottom: 24px;
    box-shadow: 0 10px 28px rgba(33, 111, 167, 0.17);
    position: relative;
}

.hero-kicker {
    color: #DDF6FF;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 12px;
}

.hero-title {
    color: #FFFFFF;
    font-size: 32px;
    font-weight: 800;
    line-height: 1.45;
    letter-spacing: -1px;
    margin-bottom: 10px;
}

.hero-description {
    color: #F1FBFF;
    font-size: 15px;
    line-height: 1.9;
}

.hero-tag {
    display: inline-block;
    margin-top: 18px;
    padding: 7px 12px;
    background: rgba(255, 255, 255, 0.18);
    color: #FFFFFF;
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 30px;
    font-size: 12px;
    font-weight: 700;
}

/* 안내 배너 */
.info-note {
    background: #FFF8E8;
    border: 1px solid #F5DDA0;
    border-left: 5px solid #F0B743;
    border-radius: 12px;
    padding: 15px 18px;
    margin: 12px 0 24px 0;
    color: #75561B;
    line-height: 1.75;
}

/* 섹션 카드 */
.section-box {
    background: #FFFFFF;
    border: 1px solid #DCEAF5;
    border-radius: 18px;
    padding: 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 16px rgba(48, 99, 143, 0.045);
}

/* 지표 카드 */
div[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #DCEAF5;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 15px rgba(48, 99, 143, 0.06);
}

div[data-testid="stMetricLabel"] {
    color: #607D98 !important;
    font-size: 0.92rem;
}

div[data-testid="stMetricValue"] {
    color: #1769AA !important;
    font-weight: 800;
}

/* 입력 영역 */
div[data-testid="stForm"] {
    background: #FFFFFF;
    border: 1px solid #DCEAF5;
    border-radius: 18px;
    padding: 22px;
    box-shadow: 0 4px 16px rgba(48, 99, 143, 0.045);
}

.stTextInput input,
.stNumberInput input {
    border-radius: 10px;
    background: #FFFFFF;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}

/* 버튼 */
.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(100deg, #1769AA, #238FC2);
    color: #FFFFFF;
    border: none;
    border-radius: 11px;
    padding: 0.65rem 1.1rem;
    font-weight: 750;
    transition: 0.2s;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #12588F;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(23, 105, 170, 0.2);
}

/* 표 */
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    background: #FFFFFF;
    border: 1px solid #DCEAF5;
    border-radius: 12px;
    overflow: hidden;
}

/* 구분선 */
hr {
    border-color: #D6E6F2;
}

/* 반응형 */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    .hero {
        padding: 23px;
    }

    .hero-title {
        font-size: 25px;
    }
}
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# 2. 지표 설정
# ------------------------------------------------------

VARIABLES = {
    "수축기 혈압": {
        "unit": "mmHg",
        "description": "심장이 수축할 때 혈관에 가해지는 압력입니다.",
        "direction": "높은 수치만으로 건강 상태를 판정할 수 없습니다."
    },
    "이완기 혈압": {
        "unit": "mmHg",
        "description": "심장이 이완할 때 혈관에 가해지는 압력입니다.",
        "direction": "높은 수치만으로 건강 상태를 판정할 수 없습니다."
    },
    "공복 혈당": {
        "unit": "mg/dL",
        "description": "공복 상태에서 측정한 혈액 속 포도당 농도입니다.",
        "direction": "높은 수치는 추가적인 건강 평가가 필요할 수 있습니다."
    },
    "HDL 콜레스테롤": {
        "unit": "mg/dL",
        "description": "혈중 지질 상태를 평가할 때 활용하는 지표입니다.",
        "direction": "다른 지표와 달리 높은 HDL은 일반적으로 유리한 방향일 수 있습니다."
    },
    "중성지방": {
        "unit": "mg/dL",
        "description": "혈액 속 지방의 한 종류입니다.",
        "direction": "높은 수치는 추가적인 건강 평가가 필요할 수 있습니다."
    },
    "허리둘레": {
        "unit": "cm",
        "description": "복부 비만 관련 지표 중 하나입니다.",
        "direction": "해석에는 성별, 연령 등 여러 요인을 고려해야 합니다."
    }
}


# ------------------------------------------------------
# 3. 가상 참고 데이터 만들기
# ------------------------------------------------------

@st.cache_data
def create_demo_data():
    """
    앱 기능을 시연하기 위한 가상 데이터입니다.
    실제 조사 자료나 실제 인구의 통계가 아닙니다.
    """

    rng = np.random.default_rng(42)
    n = 6000

    age = rng.integers(18, 81, size=n)
    sex = rng.choice(["여", "남"], size=n)

    systolic = (
        105 + age * 0.35
        + np.where(sex == "남", 3, 0)
        + rng.normal(0, 12, n)
    )

    diastolic = (
        66 + age * 0.10
        + np.where(sex == "남", 2, 0)
        + rng.normal(0, 8, n)
    )

    glucose = (
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

    waist = (
        68 + age * 0.12
        + np.where(sex == "남", 12, 0)
        + rng.normal(0, 9, n)
    )

    return pd.DataFrame({
        "age": age,
        "sex": sex,
        "수축기 혈압": np.clip(systolic, 75, 240),
        "이완기 혈압": np.clip(diastolic, 40, 150),
        "공복 혈당": np.clip(glucose, 55, 250),
        "HDL 콜레스테롤": np.clip(hdl, 15, 130),
        "중성지방": np.clip(triglycerides, 25, 900),
        "허리둘레": np.clip(waist, 45, 160)
    })


reference_data = create_demo_data()


# ------------------------------------------------------
# 4. 백분위와 분류 계산
# ------------------------------------------------------

def calculate_percentile(values, user_value):
    """
    입력값 이하인 참고 데이터의 비율을 계산합니다.
    """

    values = pd.Series(values).dropna()

    if values.empty:
        return None

    return float((values <= user_value).mean() * 100)


def classify_percentile(percentile):
    """
    수치의 상대적 위치를 세 구간으로 분류합니다.
    이 분류는 건강 상태의 순위가 아닙니다.
    """

    if percentile is None:
        return "계산 불가"

    if percentile < 25:
        return "하위권"

    if percentile < 75:
        return "중위권"

    return "상위권"


def percentile_explanation(percentile):
    if percentile is None:
        return "비교할 데이터가 부족합니다."

    if percentile < 25:
        return (
            "참고 집단의 하위 25% 범위에 해당하는 수치입니다."
        )

    if percentile < 75:
        return (
            "참고 집단의 가운데 50% 범위에 해당하는 수치입니다."
        )

    return (
        "참고 집단의 상위 25% 범위에 해당하는 수치입니다."
)


# ------------------------------------------------------
# 5. 사이드바
# ------------------------------------------------------

with st.sidebar:
    st.markdown("# 🏥 건강나이 연구소")
    st.caption("HEALTH CHECK · WELLNESS")

    st.divider()

    st.markdown("### 이용 순서")
    st.write("🔹 **01** 기본 정보 입력")
    st.write("🔹 **02** 건강검진 수치 입력")
    st.write("🔹 **03** 상대적 위치 확인")

    st.divider()

    st.markdown("### 현재 데이터")
    st.info(
        "현재 체험 화면은 가상 데이터를 사용합니다. "
        "실제 인구 집단의 건강 통계가 아닙니다."
    )

    st.caption(
        "의료 진단이나 치료 결정을 위한 서비스가 아닙니다."
    )


# ------------------------------------------------------
# 6. 첫 화면 배너
# ------------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-kicker">
        HEALTH CHECK · PERSONAL WELLNESS
    </div>

    <div class="hero-title">
        내 건강 상태를 한눈에 확인하세요
    </div>

    <div class="hero-description">
        건강검진 수치를 입력하고, 비슷한 연령대의 가상 참고 집단과 비교해 보세요.<br>
        각 지표의 상대적 위치와 의미를 알아볼 수 있습니다.
    </div>

    <div class="hero-tag">
        ✦ 나의 건강 지표 살펴보기
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-note">
    <b>📌 체험용 데이터 안내</b><br>
    현재 비교에는 프로그램이 생성한 가상 데이터가 사용됩니다.
    결과는 실제 또래 집단의 통계가 아니며, 건강 상태의 순위나
    생물학적 나이를 판정하는 데 사용할 수 없습니다.
</div>
""", unsafe_allow_html=True)


# ------------------------------------------------------
# 7. 사용자 입력
# ------------------------------------------------------

st.markdown("## 🩺 1. 기본 정보와 건강검진 수치")
st.caption(
    "최근 건강검진 결과가 있다면 해당 수치를 입력하세요. "
    "모르는 항목은 비워 둘 수 있습니다."
)

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

    st.markdown("### 건강검진 결과 입력")

    c1, c2, c3 = st.columns(3)

    with c1:
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

    with c2:
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

    with c3:
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
        "🔎 건강 지표 비교하기",
        use_container_width=True
    )


# ------------------------------------------------------
# 8. 결과 계산 및 표시
# ------------------------------------------------------

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
        st.warning(
            "비교할 건강 지표를 하나 이상 입력해 주세요."
        )
        st.stop()

    # 비교 연령대 계산
    if age_range == "같은 10세 연령대":
        age_min = (int(age) // 10) * 10
        age_max = age_min + 9
    else:
        age_min = max(18, int(age) - 5)
        age_max = min(80, int(age) + 5)

    comparison = reference_data[
        (reference_data["age"] >= age_min)
        & (reference_data["age"] <= age_max)
        & (reference_data["sex"] == sex)
    ]

    st.markdown("## 📊 2. 나의 비교 결과")

    col1, col2, col3 = st.columns(3)

    col1.metric("입력 나이", f"{int(age)}세")
    col2.metric("비교 연령대", f"{age_min}~{age_max}세")
    col3.metric("가상 참고 데이터", f"{len(comparison):,}명")

    st.caption(
        "참고 데이터 수는 가상 데이터의 행 수이며, "
        "실제 조사 참여자 수가 아닙니다."
    )

    result_rows = []
    chart_rows = []

    for name, user_value in entered_values.items():

        unit = VARIABLES[name]["unit"]
        values = comparison[name].dropna()

        if values.empty:
            continue

        median = values.median()

        percentile = calculate_percentile(
            values,
            user_value
        )

        category = classify_percentile(percentile)

        result_rows.append({
            "건강 지표": name,
            "내 입력값": f"{user_value:g} {unit}",
            "가상 집단 중앙값": f"{median:.1f} {unit}",
            "수치 백분위": f"{percentile:.1f}%",
            "수치 상대 위치": category
        })

        chart_rows.append({
            "건강 지표": name,
            "백분위": percentile,
            "분류": category
        })

    # 결과 요약 표
    result_df = pd.DataFrame(result_rows)

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 9. 상위권 / 중위권 / 하위권 기준 안내
    # --------------------------------------------------

    st.markdown("### 🧭 상대적 위치는 어떻게 나뉠까요?")

    rank1, rank2, rank3 = st.columns(3)

    with rank1:
        st.markdown("""
        <div style="
            background:#E9F3FF;
            border:1px solid #B9D8FA;
            border-radius:15px;
            padding:18px;
            min-height:145px;
        ">
            <div style="font-size:13px;color:#3A6FA5;font-weight:700;">
                LOWER 25%
            </div>
            <div style="font-size:23px;color:#205E9C;font-weight:800;margin:8px 0;">
                하위권
            </div>
            <div style="font-size:14px;color:#42627F;line-height:1.7;">
                백분위 25% 미만<br>
                참고 집단에서 비교적 낮은 수치
            </div>
        </div>
        """, unsafe_allow_html=True)

    with rank2:
        st.markdown("""
        <div style="
            background:#E9F8F1;
            border:1px solid #B8E6D0;
            border-radius:15px;
            padding:18px;
            min-height:145px;
        ">
            <div style="font-size:13px;color:#398267;font-weight:700;">
                MIDDLE 50%
            </div>
            <div style="font-size:23px;color:#267458;font-weight:800;margin:8px 0;">
                중위권
            </div>
            <div style="font-size:14px;color:#426B5C;line-height:1.7;">
                백분위 25~75% 미만<br>
                참고 집단의 가운데 범위
            </div>
        </div>
        """, unsafe_allow_html=True)

    with rank3:
        st.markdown("""
        <div style="
            background:#FFF2E5;
            border:1px solid #F7D0A9;
            border-radius:15px;
            padding:18px;
            min-height:145px;
        ">
            <div style="font-size:13px;color:#B96B2B;font-weight:700;">
                TOP 25%
            </div>
            <div style="font-size:23px;color:#A85C22;font-weight:800;margin:8px 0;">
                상위권
            </div>
            <div style="font-size:14px;color:#8A633F;line-height:1.7;">
                백분위 75% 이상<br>
                참고 집단에서 비교적 높은 수치
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="info-note">
        <b>중요:</b> 여기서 상위권·중위권·하위권은 건강 상태의 등급이 아니라
        <b>입력한 수치가 참고 집단에서 차지하는 상대적 위치</b>입니다.
        예를 들어 혈압이 상위권이라는 것은 혈압 수치가 높은 편이라는 의미이지,
        건강 상태가 좋다는 뜻이 아닙니다. HDL처럼 다른 지표와 해석 방향이 다른 항목도 있습니다.
    </div>
    """, unsafe_allow_html=True)

    # --------------------------------------------------
    # 10. 백분위 그래프
    # --------------------------------------------------

    if chart_rows:

        st.markdown("### 📈 지표별 상대적 위치")

        chart_df = pd.DataFrame(chart_rows)

        fig = px.bar(
            chart_df,
            x="건강 지표",
            y="백분위",
            range_y=[0, 100],
            color="분류",
            color_discrete_map={
                "하위권": "#438BD0",
                "중위권": "#43A783",
                "상위권": "#E9A04B"
            },
            text=chart_df["백분위"].map(
                lambda x: f"{x:.1f}%"
            ),
            labels={
                "건강 지표": "건강 지표",
                "백분위": "백분위(%)",
                "분류": "수치 상대 위치"
            }
        )

        fig.update_traces(
            textposition="outside",
            cliponaxis=False
        )

        fig.update_layout(
            paper_bgcolor="#F8FBFF",
            plot_bgcolor="#FFFFFF",
            font=dict(
                family="Malgun Gothic, sans-serif",
                color="#304B63"
            ),
            margin=dict(l=15, r=15, t=30, b=15),
            yaxis=dict(
                title="백분위(%)",
                gridcolor="#E3EDF5",
                dtick=25
            ),
            xaxis=dict(title=None),
            legend_title_text="수치 상대 위치"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # --------------------------------------------------
    # 11. 각 지표별 설명
    # --------------------------------------------------

    st.markdown("### 💡 결과 이해하기")

    for row in chart_rows:
        name = row["건강 지표"]
        percentile = row["백분위"]
        category = row["분류"]

        with st.expander(
            f"{name} · {category} ({percentile:.1f}백분위)"
        ):
            st.write(VARIABLES[name]["description"])
            st.write(
                f"현재 입력값은 가상 참고 집단의 "
                f"{percentile:.1f}백분위에 해당합니다."
            )
            st.write(VARIABLES[name]["direction"])
            st.caption(
                "이 설명은 수치의 상대적 위치에 대한 안내이며 "
                "개인의 건강 상태를 진단하는 결과가 아닙니다."
            )


# ------------------------------------------------------
# 12. 하단 안내
# ------------------------------------------------------

st.divider()

st.markdown("### 🏥 건강나이 연구소")

st.caption("""
이 프로그램은 화면과 기능을 시험하기 위한 교육용 시뮬레이션입니다.
가상 데이터를 사용하므로 실제 인구의 건강 통계를 나타내지 않습니다.
건강 상태에 대한 판단이나 진단은 의료진과 상담하세요.
""")

