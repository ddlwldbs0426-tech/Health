
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from pathlib import Path

# --------------------------------------------------
# 1. 기본 설정
# --------------------------------------------------
st.set_page_config(
    page_title="건강나이 연구소",
    page_icon="🧬",
    layout="wide"
)

BASE_DIR = Path(__file__).parent

YOUNG_IMAGE = BASE_DIR / "character_young.png"
MATURE_IMAGE = BASE_DIR / "character_mature.png"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Pretendard', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #f7fbff 0%, #fffaf4 100%);
}

.main-title {
    font-size: 36px;
    font-weight: 800;
    color: #263b59;
    margin-bottom: 4px;
}

.sub-title {
    color: #718096;
    font-size: 15px;
    margin-bottom: 25px;
}

.section-title {
    font-size: 21px;
    font-weight: 750;
    color: #30435f;
    margin-top: 20px;
    margin-bottom: 12px;
}

.result-card {
    background: white;
    border: 1px solid #e7edf5;
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 5px 18px rgba(40, 65, 100, 0.06);
}

.age-number {
    font-size: 48px;
    font-weight: 800;
    color: #486da8;
    line-height: 1.2;
}

.small-caption {
    color: #7b8798;
    font-size: 13px;
}

div[data-testid="stForm"] {
    background: white;
    border: 1px solid #e7edf5;
    border-radius: 18px;
    padding: 22px;
}

div[data-testid="stMetric"] {
    background: white;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #e7edf5;
}

.stButton button[kind="primaryFormSubmit"] {
    background: #547db8;
    border-radius: 12px;
    border: none;
    font-weight: 700;
    min-height: 45px;
}

hr {
    border-color: #e8edf4;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# 2. 제목
# --------------------------------------------------
st.markdown(
    '<div class="main-title">🧬 건강나이 연구소</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '건강지표를 바탕으로 나의 건강 프로필을 분석해 보세요.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# 3. 건강지표 기준 프로필
# --------------------------------------------------
def expected_profile(age):
    """
    연령별 비교를 위한 예시 기준 프로필.
    실제 공공데이터 API를 연결하기 전 사용하는
    시연용 가상 기준값이다.
    """

    return {
        "수축기 혈압": 112 + (age - 18) * 0.20,
        "이완기 혈압": 72 + (age - 18) * 0.08,
        "공복혈당": 88 + (age - 18) * 0.12,
        "HDL 콜레스테롤": 58 - (age - 18) * 0.10,
        "중성지방": 90 + (age - 18) * 0.45,
        "허리둘레": 70 + (age - 18) * 0.22
    }


# --------------------------------------------------
# 4. 건강나이 추정
# --------------------------------------------------
def predict_body_age(actual_age, values):
    """
    건강지표와 예시 기준값의 차이를 이용한
    교육용 시연 계산식이다.
    의학적으로 검증된 건강나이 공식은 아니다.
    """

    weights = {
        "수축기 혈압": 0.20,
        "이완기 혈압": 0.10,
        "공복혈당": 0.25,
        "HDL 콜레스테롤": 0.15,
        "중성지방": 0.15,
        "허리둘레": 0.15
    }

    deviations = []

    for age in [actual_age]:
        reference = expected_profile(age)

        # 각 지표의 차이를 표준화하기 위한 예시 척도
        scales = {
            "수축기 혈압": 15,
            "이완기 혈압": 10,
            "공복혈당": 12,
            "HDL 콜레스테롤": 12,
            "중성지방": 50,
            "허리둘레": 12
        }

        for key, weight in weights.items():
            difference = values[key] - reference[key]

            # HDL은 수치가 높을수록 일반적으로 유리한 방향이므로 부호 반전
            if key == "HDL 콜레스테롤":
                difference *= -1

            deviations.append(
                weight * difference / scales[key]
            )

    total_deviation = sum(deviations)

    # 과도한 추정값 방지
    estimated_age = actual_age + total_deviation * 12

    return int(round(np.clip(estimated_age, 18, 80)))


# --------------------------------------------------
# 5. 연령대별 건강 프로필 유사도 계산
# --------------------------------------------------
def calculate_similarity(values):
    ages = np.arange(18, 81)

    scales = {
        "수축기 혈압": 15,
        "이완기 혈압": 10,
        "공복혈당": 12,
        "HDL 콜레스테롤": 12,
        "중성지방": 50,
        "허리둘레": 12
    }

    weights = {
        "수축기 혈압": 0.20,
        "이완기 혈압": 0.10,
        "공복혈당": 0.25,
        "HDL 콜레스테롤": 0.15,
        "중성지방": 0.15,
        "허리둘레": 0.15
    }

    distances = []

    for age in ages:
        reference = expected_profile(age)
        distance = 0

        for key, weight in weights.items():
            diff = values[key] - reference[key]

            if key == "HDL 콜레스테롤":
                diff *= -1

            distance += weight * (diff / scales[key]) ** 2

        distances.append(np.sqrt(distance))

    distances = np.array(distances)

    # 거리가 가까울수록 유사도가 높도록 변환
    similarities = 100 * np.exp(-distances * 1.5)

    return ages, similarities


# --------------------------------------------------
# 6. 캐릭터 선택
# --------------------------------------------------
def show_character(body_age):
    """
    추정 건강나이에 따라 캐릭터 이미지 선택.
    """

    if body_age < 40:
        image_path = YOUNG_IMAGE
        character_name = "분홍 안경 캐릭터"
        message = "건강 프로필이 비교적 젊은 연령대와 가까워요!"
    else:
        image_path = MATURE_IMAGE
        character_name = "빨간 안경 캐릭터"
        message = "건강 프로필을 꾸준히 살펴보면 좋겠어요!"

    if image_path.exists():
        st.image(str(image_path), use_container_width=True)
    else:
        st.warning(
            f"캐릭터 이미지를 찾을 수 없습니다: {image_path.name}"
        )

    st.markdown(
        f"<div style='text-align:center; font-weight:700; color:#526782;'>"
        f"{character_name}</div>",
        unsafe_allow_html=True
    )

    st.caption(message)


# --------------------------------------------------
# 7. 유사도 그래프
# --------------------------------------------------
def similarity_chart(values, estimated_age):
    ages, similarities = calculate_similarity(values)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=ages,
        y=similarities,
        mode="lines",
        name="건강 프로필 유사도",
        line=dict(color="#7098cc", width=3),
        fill="tozeroy",
        fillcolor="rgba(112,152,204,0.13)"
    ))

    fig.add_vline(
        x=estimated_age,
        line_dash="dash",
        line_color="#ef9b70",
        annotation_text=f"추정 건강나이 {estimated_age}세",
        annotation_position="top"
    )

    fig.update_layout(
        title="연령대별 건강 프로필 유사도",
        xaxis_title="연령",
        yaxis_title="유사도 (%)",
        xaxis=dict(range=[18, 80], dtick=10),
        yaxis=dict(range=[0, 100]),
        height=370,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=65, b=35),
        legend=dict(orientation="h", y=1.12)
    )

    return fig


# --------------------------------------------------
# 8. 건강지표 비교 그래프
# --------------------------------------------------
def metric_chart(values, actual_age):
    reference = expected_profile(actual_age)

    labels = list(values.keys())
    user_values = list(values.values())
    reference_values = [reference[key] for key in labels]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        name="입력한 건강 수치",
        x=labels,
        y=user_values,
        marker_color="#7199cc"
    ))

    fig.add_trace(go.Bar(
        name="비교 기준값",
        x=labels,
        y=reference_values,
        marker_color="#f2b88f"
    ))

    fig.update_layout(
        title="건강지표별 입력값과 비교 기준값",
        barmode="group",
        height=390,
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=20, r=20, t=60, b=75),
        legend=dict(orientation="h", y=1.12),
        xaxis=dict(tickangle=-15)
    )

    return fig


# --------------------------------------------------
# 9. 건강지표 비교표
# --------------------------------------------------
def make_comparison_table(values, actual_age):
    reference = expected_profile(actual_age)

    rows = []

    for key, value in values.items():
        standard = reference[key]

        difference = value - standard

        rows.append({
            "건강지표": key,
            "입력값": round(value, 1),
            "비교 기준값": round(standard, 1),
            "차이": round(difference, 1)
        })

    return pd.DataFrame(rows)


# --------------------------------------------------
# 10. 사용자 입력
# --------------------------------------------------
st.markdown(
    '<div class="section-title">01. 건강정보 입력</div>',
    unsafe_allow_html=True
)

with st.form("health_form"):

    col1, col2 = st.columns(2)

    with col1:
        actual_age = st.number_input(
            "실제 나이",
            min_value=18,
            max_value=80,
            value=25,
            step=1
        )

        sex = st.selectbox(
            "성별",
            ["남성", "여성"]
        )

        systolic = st.number_input(
            "수축기 혈압 (mmHg)",
            min_value=70,
            max_value=250,
            value=120
        )

        diastolic = st.number_input(
            "이완기 혈압 (mmHg)",
            min_value=40,
            max_value=150,
            value=80
        )

    with col2:
        glucose = st.number_input(
            "공복혈당 (mg/dL)",
            min_value=40,
            max_value=400,
            value=95
        )

        hdl = st.number_input(
            "HDL 콜레스테롤 (mg/dL)",
            min_value=10,
            max_value=150,
            value=55
        )

        triglyceride = st.number_input(
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
        "건강나이 분석하기",
        type="primary",
        use_container_width=True
    )


# --------------------------------------------------
# 11. 분석 실행 및 결과 저장
# --------------------------------------------------
if submitted:

    if systolic <= diastolic:
        st.error("수축기 혈압은 이완기 혈압보다 높게 입력해 주세요.")

    else:
        values = {
            "수축기 혈압": float(systolic),
            "이완기 혈압": float(diastolic),
            "공복혈당": float(glucose),
            "HDL 콜레스테롤": float(hdl),
            "중성지방": float(triglyceride),
            "허리둘레": float(waist)
        }

        body_age = predict_body_age(actual_age, values)

        st.session_state.health_result = {
            "actual_age": actual_age,
            "body_age": body_age,
            "sex": sex,
            "values": values
        }


# --------------------------------------------------
# 12. 결과 출력
# --------------------------------------------------
if "health_result" in st.session_state:

    result = st.session_state.health_result

    actual_age = result["actual_age"]
    body_age = result["body_age"]
    values = result["values"]

    st.markdown("---")

    st.markdown(
        '<div class="section-title">02. 건강나이 분석 결과</div>',
        unsafe_allow_html=True
    )

    result_col1, result_col2 = st.columns([1.5, 1])

    with result_col1:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)

        st.markdown(
            '<div class="small-caption">예측된 건강나이</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            f'<div class="age-number">{body_age}세</div>',
            unsafe_allow_html=True
        )

        difference = body_age - actual_age

        if difference < 0:
            st.success(
                f"실제 나이보다 {abs(difference)}세 낮은 추정 결과입니다."
            )
        elif difference > 0:
            st.warning(
                f"실제 나이보다 {difference}세 높은 추정 결과입니다."
            )
        else:
            st.info("실제 나이와 동일한 추정 결과입니다.")

        st.markdown(
            f"실제 나이: **{actual_age}세**",
            unsafe_allow_html=True
        )

        st.markdown('</div>', unsafe_allow_html=True)

    with result_col2:
        show_character(body_age)

    # --------------------------------------------------
    # 13. 연령대별 유사도
    # --------------------------------------------------
    st.markdown(
        '<div class="section-title">03. 연령대별 건강 프로필 유사도</div>',
        unsafe_allow_html=True
    )

    st.caption(
        "입력한 건강지표와 각 연령대의 예시 기준 프로필 사이의 "
        "수치적 유사도를 나타냅니다."
    )

    st.plotly_chart(
        similarity_chart(values, body_age),
        use_container_width=True
    )

    # --------------------------------------------------
    # 14. 지표별 비교
    # --------------------------------------------------
    st.markdown(
        '<div class="section-title">04. 건강지표별 비교</div>',
        unsafe_allow_html=True
    )

    st.plotly_chart(
        metric_chart(values, actual_age),
        use_container_width=True
    )

    # --------------------------------------------------
    # 15. 비교표
    # --------------------------------------------------
    st.markdown(
        '<div class="section-title">05. 건강 수치 비교표</div>',
        unsafe_allow_html=True
    )

    comparison = make_comparison_table(values, actual_age)

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # 16. 결과 해석 및 안내
    # --------------------------------------------------
    st.markdown("---")

    st.markdown("### 분석 결과 해석")

    st.write(
        f"입력한 건강지표를 예시 기준 프로필과 비교한 결과, "
        f"추정 건강나이는 {body_age}세로 계산되었습니다. "
        f"이는 실제 나이 {actual_age}세를 기준으로 한 "
        f"교육용 시뮬레이션 결과입니다."
    )

    st.info(
        "현재 프로그램은 실제 공공 건강검진 API와 연결되어 있지 않으며, "
        "연령별 비교 기준과 건강나이 계산식은 시연을 위해 설정한 값입니다. "
        "의학적으로 검증된 건강나이나 질병 위험도 진단이 아닙니다. "
        "실제 건강 상태는 의료 전문가와 상담해 확인해야 합니다."
    )

    if st.button("새로운 건강정보 입력하기"):
        del st.session_state.health_result
        st.rerun()

else:
    st.markdown("---")

    st.markdown(
        """
        <div style="
            background:white;
            padding:22px;
            border-radius:18px;
            border:1px solid #e7edf5;
            text-align:center;
        ">
            <div style="font-size:18px;font-weight:750;color:#425873;">
                나의 건강 프로필을 확인해 보세요!
            </div>
            <div style="font-size:14px;color:#8995a5;margin-top:8px;">
                건강정보를 입력하고 분석하기 버튼을 누르면
                건강나이와 연령대별 비교 결과를 확인할 수 있습니다.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
