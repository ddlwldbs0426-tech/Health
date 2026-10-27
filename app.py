
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================================================
# 건강나이 연구소
# 연령대별 건강 지표 비교 프로그램
# =========================================================

st.set_page_config(
    page_title="건강나이 연구소",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 1. 전체 디자인 설정
# ---------------------------------------------------------

st.markdown("""
<style>
/* 전체 배경과 글꼴 */
.stApp {
    background-color: #F5F7F3;
    color: #34483D;
    font-family: "Pretendard", "Malgun Gothic", sans-serif;
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* 제목 */
h1, h2, h3 {
    color: #285C4D !important;
    letter-spacing: -0.7px;
}

h1 {
    font-weight: 750 !important;
}

h2, h3 {
    font-weight: 700 !important;
}

/* 기본 글자 */
p, label, .stMarkdown {
    color: #465B50;
}

/* 건강 지표 카드 */
div[data-testid="stMetric"] {
    background-color: #FFFFFF;
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

/* 입력창 */
.stTextInput input,
.stNumberInput input {
    border-radius: 10px;
    background-color: #FFFFFF;
}

.stSelectbox div[data-baseweb="select"] {
    border-radius: 10px;
}

/* 버튼 */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #397765;
    color: white;
    border: 1px solid #397765;
    border-radius: 10px;
    padding: 0.55rem 1.2rem;
    font-weight: 650;
    transition: 0.2s;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #2D6253;
    color: white;
    border-color: #2D6253;
}

/* 사이드바 */
section[data-testid="stSidebar"] {
    background-color: #EAF1EB;
    border-right: 1px solid #DCE6DC;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #285C4D !important;
}

/* 첫 화면 소개 영역 */
.hero {
    background: linear-gradient(
        120deg,
        #E4EFE7 0%,
        #F9F8F2 100%
    );
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
    letter-spacing: -1px;
    margin-bottom: 10px;
}

.hero-description {
    color: #536B5E;
    font-size: 15px;
    line-height: 1.8;
}

/* 안내 상자 */
.info-note {
    background-color: #EDF4EE;
    border-left: 4px solid #79A88E;
    border-radius: 8px;
    padding: 14px 16px;
    margin: 12px 0 22px 0;
    color: #405D4D;
    line-height: 1.7;
}

/* 구분선 */
hr {
    border-color: #DCE6DC;
}

/* 표 */
div[data-testid="stDataFrame"],
div[data-testid="stTable"] {
    border: 1px solid #E1E9E1;
    border-radius: 12px;
    overflow: hidden;
}

/* 모바일 화면 */
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


# ---------------------------------------------------------
# 2. 건강 지표 설정
# ---------------------------------------------------------

DATA_PATH = Path(__file__).parent / "knhanes_processed.csv"

VARIABLES = {
    "수축기 혈압": {
        "column": "systolic_bp",
        "unit": "mmHg",
        "description": "심장이 수축할 때 혈관에 가해지는 압력입니다."
    },
    "이완기 혈압": {
        "column": "diastolic_bp",
        "unit": "mmHg",
        "description": "심장이 이완할 때 혈관에 가해지는 압력입니다."
    },
    "공복 혈당": {
        "column": "fasting_glucose",
        "unit": "mg/dL",
        "description": "공복 상태에서 측정한 혈액 속 포도당 농도입니다."
    },
    "HDL 콜레스테롤": {
        "column": "hdl",
        "unit": "mg/dL",
        "description": "혈중 지질 상태를 평가할 때 활용하는 지표입니다."
    },
    "중성지방": {
        "column": "triglycerides",
        "unit": "mg/dL",
        "description": "혈액 속 지방의 한 종류입니다."
    },
    "허리둘레": {
        "column": "waist_cm",
        "unit": "cm",
        "description": "복부 비만 관련 지표 중 하나입니다."
    }
}

REQUIRED_COLUMNS = [
    "age",
    "sex",
    "systolic_bp",
    "diastolic_bp",
    "fasting_glucose",
    "hdl",
    "triglycerides",
    "waist_cm",
    "weight"
]


# ---------------------------------------------------------
# 3. 참고 데이터 불러오기
# ---------------------------------------------------------

@st.cache_data
def load_data(file_path, modified_time):
    df = pd.read_csv(file_path)

    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "CSV 파일에 필요한 열이 없습니다: "
            + ", ".join(missing_columns)
        )

    df = df.copy()

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    df["sex"] = (
        df["sex"]
        .astype(str)
        .str.strip()
        .replace({
            "1": "남",
            "2": "여",
            "M": "남",
            "F": "여",
            "Male": "남",
            "Female": "여",
            "남자": "남",
            "여자": "여"
        })
    )

    numeric_columns = [
        value["column"]
        for value in VARIABLES.values()
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    df = df.dropna(
        subset=["age", "sex", "weight"]
    )

    df = df[df["weight"] > 0]
    df = df[df["sex"].isin(["남", "여"])]

    return df


def weighted_percentile(values, weights, user_value):
    """
    가중치를 이용해 계산한 참고용 누적 백분위입니다.
    복합표본설계를 완전히 반영한 공식 통계량은 아닙니다.
    """
    values = pd.to_numeric(values, errors="coerce")
    weights = pd.to_numeric(weights, errors="coerce")

    valid = (
        values.notna()
        & weights.notna()
        & (weights > 0)
    )

    values = values[valid]
    weights = weights[valid]

    if len(values) == 0 or weights.sum() == 0:
        return None

    percentile = (
        weights[values <= user_value].sum()
        / weights.sum()
        * 100
    )

    return float(percentile)


# ---------------------------------------------------------
# 4. 사이드바
# ---------------------------------------------------------

with st.sidebar:
    st.markdown("# 🌿 건강나이 연구소")
    st.caption("나의 건강 상태를 이해하는 공간")

    st.divider()

    st.markdown("### 이용 방법")
    st.write("**01** 기본 정보를 입력합니다.")
    st.write("**02** 건강검진 수치를 입력합니다.")
    st.write("**03** 비슷한 연령대의 통계와 비교합니다.")

    st.divider()

    st.markdown("### 서비스 안내")
    st.write(
        "건강 지표의 상대적 위치를 확인하기 위한 "
        "교육·정보 제공용 프로그램입니다."
    )

    st.caption(
        "질병 진단이나 치료를 대신할 수 없습니다."
    )


# ---------------------------------------------------------
# 5. 첫 화면
# ---------------------------------------------------------

st.markdown("""
<div class="hero">
    <div class="hero-kicker">
        PERSONAL HEALTH INFORMATION
    </div>

    <div class="hero-title">
        나의 건강을 이해하는 첫걸음
    </div>

    <div class="hero-description">
        건강 지표를 입력하고 비슷한 연령대의 통계와 비교해 보세요.<br>
        현재의 건강 상태를 살펴보는 데 도움이 되는 참고 정보를 제공합니다.
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-note">
    <b>먼저 확인해 주세요.</b><br>
    이 서비스는 건강 지표를 참고 집단과 비교하는 도구입니다.
    결과만으로 질병 여부나 생물학적 나이를 판정할 수는 없습니다.
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# 6. 데이터 파일 확인
# ---------------------------------------------------------

if not DATA_PATH.exists():
    st.error(
        "참고 데이터 파일을 찾을 수 없습니다. "
        "`knhanes_processed.csv` 파일을 `main.py`와 "
        "같은 폴더에 추가해 주세요."
    )

    with st.expander("필요한 CSV 열 확인하기"):
        st.code(
            "age, sex, systolic_bp, diastolic_bp, "
            "fasting_glucose, hdl, triglycerides, "
            "waist_cm, weight",
            language="text"
        )

        st.markdown("""
        `sex`는 `남` 또는 `여`로 표기합니다. `weight`에는
        해당 조사 연도와 분석 대상에 맞는 조사 가중치가 필요합니다.

        국민건강영양조사 원자료의 변수명과 가중치 종류는
        조사 연도에 따라 확인해야 합니다.
        """)

    st.stop()

try:
    data = load_data(
        str(DATA_PATH),
        DATA_PATH.stat().st_mtime
    )
except Exception as error:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {error}")
    st.stop()


# ---------------------------------------------------------
# 7. 사용자 입력
# ---------------------------------------------------------

st.markdown("## 1. 기본 정보 입력")
st.caption(
    "최근 건강검진 결과가 있다면 해당 수치를 입력하세요. "
    "모르는 항목은 비워 두어도 됩니다."
)

with st.form("health_form"):
    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input(
            "만 나이",
            min_value=1,
            max_value=110,
            value=30,
            step=1
        )

    with col2:
        sex = st.selectbox(
            "성별",
            options=["여", "남"]
        )

    age_range = st.radio(
        "비교할 연령 범위",
        options=["같은 10세 연령대", "±5세"],
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


# ---------------------------------------------------------
# 8. 비교 결과 계산
# ---------------------------------------------------------

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
        st.warning("비교할 건강 지표를 한 가지 이상 입력해 주세요.")
        st.stop()

    if age_range == "같은 10세 연령대":
        age_min = (int(age) // 10) * 10
        age_max = age_min + 9
    else:
        age_min = max(0, int(age) - 5)
        age_max = int(age) + 5

    reference = data[
        (data["age"] >= age_min)
        & (data["age"] <= age_max)
        & (data["sex"] == sex)
    ]

    st.markdown("## 2. 나의 건강 지표 비교")

    col1, col2, col3 = st.columns(3)

    col1.metric("입력한 나이", f"{int(age)}세")
    col2.metric(
        "참고 연령 범위",
        f"{age_min}~{age_max}세"
    )
    col3.metric(
        "참고 데이터 수",
        f"{len(reference):,}명"
    )

    if len(reference) < 20:
        st.warning(
            "참고 데이터 수가 적어 비교 결과가 불안정할 수 있습니다. "
            "연령 범위를 넓혀 확인해 보세요."
        )

    result_rows = []
    chart_rows = []

    for name, user_value in entered_values.items():
        info = VARIABLES[name]
        column = info["column"]
        unit = info["unit"]

        subset = reference[
            [column, "weight"]
        ].dropna()

        if subset.empty:
            result_rows.append({
                "건강 지표": name,
                "입력값": f"{user_value:g} {unit}",
                "참고 집단 중앙값": "자료 없음",
                "백분위 위치": "계산 불가"
            })
            continue

        median = subset[column].median()

        percentile = weighted_percentile(
            subset[column],
            subset["weight"],
            user_value
        )

        if percentile is None:
            percentile_text = "계산 불가"
        else:
            percentile_text = f"{percentile:.1f}%"

            chart_rows.append({
                "건강 지표": name,
                "백분위 위치": percentile
            })

        result_rows.append({
            "건강 지표": name,
            "입력값": f"{user_value:g} {unit}",
            "참고 집단 중앙값": f"{median:.1f} {unit}",
            "백분위 위치": percentile_text
        })

    result_df = pd.DataFrame(result_rows)

    st.dataframe(
        result_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # 9. 백분위 그래프
    # -----------------------------------------------------

    if chart_rows:
        st.markdown("### 참고 집단 안에서의 상대적 위치")

        chart_df = pd.DataFrame(chart_rows)

        fig = px.bar(
            chart_df,
            x="건강 지표",
            y="백분위 위치",
            range_y=[0, 100],
            text=chart_df["백분위 위치"].map(
                lambda value: f"{value:.0f}%"
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
                family="Pretendard, Malgun Gothic, sans-serif",
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

    # -----------------------------------------------------
    # 10. 해석 안내
    # -----------------------------------------------------

    st.markdown("### 결과를 해석할 때 주의할 점")

    st.markdown("""
    백분위는 선택한 참고 집단에서 입력값 이하인 관측값의
    가중 비율을 나타내는 참고용 근사치입니다.

    백분위가 높거나 낮다는 사실만으로 건강 상태가 좋거나
    나쁘다고 단정할 수는 없습니다. 혈압, 혈당, HDL,
    중성지방, 허리둘레는 각각 해석 방법이 다르며 개인의
    건강 상태와 측정 조건도 함께 고려해야 합니다.

    또한 이 프로그램의 계산은 국민건강영양조사의 층화·집락 등
    복합표본설계를 모두 반영한 공식 통계 분석이 아닙니다.
    """)


# ---------------------------------------------------------
# 11. 하단 안내
# ---------------------------------------------------------

st.divider()

st.markdown("### 건강나이 연구소 안내")

st.caption("""
본 서비스는 교육 및 건강정보 이해를 위한 참고용 프로그램입니다.
의료적 진단이나 치료 권고를 제공하지 않으며,
검증된 생물학적 나이를 산출하지 않습니다.
건강 상태에 대한 판단은 의료진과 상담하세요.
""")

st.caption(
    "참고 데이터로 국민건강영양조사 자료를 사용할 경우 "
    "해당 조사 연도의 원시자료 이용지침과 가중치 설명을 확인하세요."
)
