
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# =========================================================
# 1. 기본 화면 설정
# =========================================================
st.set_page_config(
    page_title="건강 나이 분석",
    page_icon="🧬",
    layout="wide"
)

st.title("🧬 건강 나이 분석 프로그램")
st.write(
    "실제 나이와 생활 습관을 바탕으로 건강 관련 정보를 살펴보고, "
    "연령대별 비교 자료와 결과를 확인하는 교육용 프로그램입니다."
)

st.warning(
    "이 프로그램은 의학적으로 검증된 생물학적 나이 측정기가 아닙니다. "
    "표시되는 나이는 생활 습관 점수를 이용한 교육용 참고값이며, "
    "질병을 진단하거나 실제 노화 정도를 판정하지 않습니다."
)

# =========================================================
# 2. 연령대 구분 및 점수 계산 함수
# =========================================================
def get_age_group(age):
    """나이를 연령대 그룹으로 변환합니다."""
    if age <= 19:
        return "13~19세"
    elif age <= 39:
        return "20~39세"
    elif age <= 59:
        return "40~59세"
    return "60~100세"


def calculate_score(age, sleep, exercise, vegetables,
                    processed_days, stress, self_health):
    """
    생활 습관 응답을 바탕으로 100점 만점의
    교육용 건강 습관 점수를 계산합니다.
    이 점수는 실제 생물학적 나이 측정값이 아닙니다.
    """
    score = 0

    # 수면: 청소년과 성인의 참고 수면 시간을 다르게 적용합니다.
    if age < 18:
        if 8 <= sleep <= 10:
            score += 20
        elif 7 <= sleep < 8 or 10 < sleep <= 11:
            score += 15
        elif 6 <= sleep < 7 or 11 < sleep <= 12:
            score += 10
        else:
            score += 5
    else:
        if 7 <= sleep <= 9:
            score += 20
        elif 6 <= sleep < 7 or 9 < sleep <= 10:
            score += 15
        elif 5 <= sleep < 6 or 10 < sleep <= 11:
            score += 10
        else:
            score += 5

    # 신체 활동: 청소년과 성인의 참고 기준을 구분합니다.
    target = 420 if age < 18 else 150

    if exercise >= target:
        score += 20
    elif exercise >= target * 0.75:
        score += 15
    elif exercise >= target * 0.5:
        score += 10
    elif exercise > 0:
        score += 5

    # 과일과 채소 섭취 빈도
    if vegetables >= 5:
        score += 20
    elif vegetables >= 3:
        score += 15
    elif vegetables >= 1:
        score += 8
    else:
        score += 2

    # 가공식품·당류가 많은 음료 등을 자주 섭취하는 날
    if processed_days <= 1:
        score += 15
    elif processed_days <= 3:
        score += 12
    elif processed_days <= 5:
        score += 8
    else:
        score += 4

    # 스트레스 체감 정도: 1은 낮음, 5는 높음
    stress_points = {1: 15, 2: 13, 3: 10, 4: 6, 5: 3}
    score += stress_points[stress]

    # 주관적으로 느끼는 전반적인 건강 상태
    health_points = {1: 2, 2: 4, 3: 6, 4: 8, 5: 10}
    score += health_points[self_health]

    return min(100, max(0, score))


def get_reference_label(percentile):
    """연령대 비교 점수의 상대적 위치를 표시합니다."""
    if percentile >= 75:
        return "상위권"
    elif percentile <= 25:
        return "하위권"
    return "중위권"


# =========================================================
# 3. 비교 데이터 안내
# =========================================================
st.subheader("📊 연령대별 비교 데이터")

st.write(
    "동일한 설문 항목으로 수집한 비교 대상자의 CSV 파일을 업로드하면 "
    "해당 자료에서 같은 연령대의 점수 분포를 계산합니다."
)

st.info(
    "비교 파일이 없으면 프로그램 점검용 예시 자료를 사용합니다. "
    "예시 자료는 실제 국민건강 통계가 아니며, 실제 인구의 평균이나 "
    "백분위를 나타내지 않습니다."
)

# CSV에 필요한 열 이름
required_columns = [
    "age",
    "sleep_hours",
    "exercise_min_week",
    "fruit_veg_servings",
    "processed_days_week",
    "stress_level",
    "self_rated_health"
]

uploaded_file = st.file_uploader(
    "비교 대상자 데이터 CSV 업로드 (선택 사항)",
    type=["csv"],
    help="아래 코드 설명에 제시된 열 이름을 사용해야 합니다."
)

# =========================================================
# 4. 사용자의 건강 관련 질문
# =========================================================
st.subheader("📝 건강 관련 질문")

with st.form("health_form"):
    age = st.number_input(
        "실제 나이(만 나이)",
        min_value=13,
        max_value=100,
        value=17,
        step=1
    )

    st.caption(
        "다음 항목은 최근 생활 습관을 기준으로 답해주세요. "
        "건강 관련 질문에 대한 응답은 진단 결과가 아닙니다."
    )

    sleep = st.slider(
        "하루 평균 수면 시간",
        min_value=0.0,
        max_value=14.0,
        value=8.0,
        step=0.5,
        help="평일과 주말을 포함한 대략적인 평균입니다."
    )

    exercise = st.number_input(
        "일주일 동안의 신체 활동 시간(분)",
        min_value=0,
        max_value=3000,
        value=150,
        step=10,
        help="걷기, 자전거 타기, 스포츠 등 신체 활동을 합산합니다."
    )

    vegetables = st.slider(
        "하루 과일·채소 섭취 횟수",
        min_value=0,
        max_value=10,
        value=3,
        help="정밀한 영양 분석이 아닌 간단한 설문 항목입니다."
    )

    processed_days = st.slider(
        "일주일 중 가공식품 또는 당류가 많은 음료를 자주 섭취하는 날",
        min_value=0,
        max_value=7,
        value=3
    )

    stress = st.select_slider(
        "최근 스트레스 체감 정도",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: {
            1: "1 - 매우 낮음",
            2: "2 - 낮음",
            3: "3 - 보통",
            4: "4 - 높음",
            5: "5 - 매우 높음"
        }[x]
    )

    self_health = st.select_slider(
        "스스로 느끼는 전반적인 건강 상태",
        options=[1, 2, 3, 4, 5],
        value=3,
        format_func=lambda x: {
            1: "1 - 좋지 않음",
            2: "2 - 다소 좋지 않음",
            3: "3 - 보통",
            4: "4 - 좋은 편",
            5: "5 - 매우 좋음"
        }[x]
    )

    st.markdown("#### 추가 건강 정보")

    known_conditions = st.multiselect(
        "의료진에게 진단받은 건강 문제가 있다면 선택하세요. (선택 사항)",
        [
            "고혈압",
            "당뇨병",
            "이상지질혈증",
            "천식 등 호흡기 질환",
            "심혈관 질환",
            "기타 만성질환",
            "해당 없음",
            "응답하지 않음"
        ]
    )

    family_history = st.radio(
        "가족 중 만성질환 병력이 있나요?",
        ["있음", "없음", "잘 모르겠음", "응답하지 않음"],
        horizontal=True
    )

    submitted = st.form_submit_button(
        "건강 습관 분석하기",
        type="primary",
        use_container_width=True
    )

# =========================================================
# 5. 비교 데이터 불러오기 및 오류 안내
# =========================================================
def make_demo_data():
    """
    실제 통계가 아닌 프로그램 테스트용 자료입니다.
    연령대별 값은 실제 인구의 건강 수준을 나타내지 않습니다.
    """
    rows = []

    # 동일한 설문으로 수집된 데이터가 있을 때의 계산 과정을
    # 시험하기 위한 예시 응답입니다.
    demo_records = [
        (15, 8.5, 450, 5, 1, 2, 4),
        (16, 7.5, 300, 3, 3, 3, 3),
        (17, 8.0, 500, 5, 2, 2, 4),
        (18, 6.5, 120, 2, 5, 4, 2),
        (19, 8.5, 420, 4, 1, 2, 5),
        (22, 7.5, 180, 4, 2, 2, 4),
        (27, 6.5, 100, 2, 5, 4, 3),
        (31, 8.0, 220, 5, 1, 3, 4),
        (35, 7.0, 150, 3, 3, 3, 3),
        (38, 9.0, 300, 4, 2, 2, 4),
        (42, 6.0, 90, 2, 5, 5, 2),
        (47, 7.5, 180, 4, 2, 3, 4),
        (52, 7.0, 120, 3, 3, 3, 3),
        (56, 8.0, 200, 5, 1, 2, 4),
        (59, 6.5, 100, 2, 4, 4, 2),
        (62, 7.5, 160, 4, 2, 2, 4),
        (68, 7.0, 120, 3, 3, 3, 3),
        (74, 8.0, 180, 5, 1, 2, 4),
        (81, 6.5, 90, 2, 5, 4, 2),
        (88, 7.5, 150, 4, 2, 3, 4)
    ]

    for record in demo_records:
        a, sl, ex, fv, pdays, st_level, sh = record
        rows.append({
            "age": a,
            "sleep_hours": sl,
            "exercise_min_week": ex,
            "fruit_veg_servings": fv,
            "processed_days_week": pdays,
            "stress_level": st_level,
            "self_rated_health": sh
        })

    return pd.DataFrame(rows)


def prepare_reference_data(upload):
    """
    CSV 파일의 열 이름과 값이 올바른지 확인합니다.
    파일이 없거나 잘못된 경우에는 한국어 안내를 표시합니다.
    """
    if upload is None:
        st.info("현재는 시연용 예시 데이터를 사용하고 있습니다.")
        return make_demo_data(), False

    try:
        data = pd.read_csv(upload)

        if data.empty:
            st.error(
                "업로드한 CSV에 데이터 행이 없습니다. "
                "헤더 아래에 실제 응답 데이터가 있는지 확인하세요."
            )
            return make_demo_data(), False

        missing = [col for col in required_columns if col not in data.columns]

        if missing:
            st.error(
                "CSV의 열 이름이 올바르지 않습니다. "
                f"누락된 열: {', '.join(missing)}"
            )
            st.info(
                "필요한 열 이름: " + ", ".join(required_columns)
            )
            return make_demo_data(), False

        for col in required_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        # 핵심 항목이 비어 있거나 숫자로 변환되지 않은 행을 제외합니다.
        data = data.dropna(subset=required_columns).copy()

        if data.empty:
            st.error(
                "유효한 건강 설문 데이터가 없습니다. "
                "나이와 각 응답이 숫자로 입력되었는지 확인하세요."
            )
            return make_demo_data(), False

        # 응답 범위가 잘못된 행을 제거합니다.
        valid = (
            data["age"].between(13, 100)
            & data["sleep_hours"].between(0, 14)
            & data["exercise_min_week"].between(0, 3000)
            & data["fruit_veg_servings"].between(0, 10)
            & data["processed_days_week"].between(0, 7)
            & data["stress_level"].between(1, 5)
            & data["self_rated_health"].between(1, 5)
        )

        data = data.loc[valid].copy()

        if data.empty:
            st.error(
                "응답 범위가 올바른 데이터가 없습니다. "
                "각 열의 값이 안내된 범위에 있는지 확인하세요."
            )
            return make_demo_data(), False

        return data, True

    except Exception as error:
        st.error(
            "CSV 파일을 읽는 중 오류가 발생했습니다. "
            "UTF-8 형식의 CSV인지, 파일이 손상되지 않았는지 확인하세요."
        )
        st.caption(f"오류 유형: {type(error).__name__}")
        return make_demo_data(), False


def add_scores(data):
    """각 응답자의 건강 습관 점수를 계산합니다."""
    result = data.copy()

    result["health_score"] = result.apply(
        lambda row: calculate_score(
            int(row["age"]),
            float(row["sleep_hours"]),
            float(row["exercise_min_week"]),
            float(row["fruit_veg_servings"]),
            int(row["processed_days_week"]),
            int(row["stress_level"]),
            int(row["self_rated_health"])
        ),
        axis=1
    )

    result["age_group"] = result["age"].apply(
        lambda value: get_age_group(int(value))
    )

    return result


# =========================================================
# 6. 결과 분석 및 시각화
# =========================================================
if submitted:
    user_score = calculate_score(
        int(age),
        sleep,
        exercise,
        vegetables,
        processed_days,
        stress,
        self_health
    )

    # 교육용 참고 나이 계산식입니다.
    # 의학적으로 검증된 생물학적 나이 공식이 아닙니다.
    adjustment = round((70 - user_score) / 6)
    adjustment = max(-8, min(8, adjustment))
    estimated_age = max(13, min(100, int(age) + adjustment))

    user_group = get_age_group(int(age))

    reference_raw, is_uploaded_data = prepare_reference_data(uploaded_file)
    reference = add_scores(reference_raw)

    # 입력한 사용자와 같은 연령대의 자료를 선택합니다.
    same_group = reference[reference["age_group"] == user_group].copy()

    # 연령대 표본이 너무 적으면 상대적 순위를 제시하지 않습니다.
    if len(same_group) >= 5:
        percentile = (
            same_group["health_score"] <= user_score
        ).mean() * 100

        rank_label = get_reference_label(percentile)
        comparison_available = True
    else:
        percentile = None
        rank_label = "비교 자료 부족"
        comparison_available = False

    st.divider()
    st.header("📌 분석 결과")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("실제 나이", f"{int(age)}세")

    with col2:
        st.metric(
            "건강 습관 참고 나이",
            f"{estimated_age}세",
            delta=f"{estimated_age - int(age):+d}세"
        )

    with col3:
        st.metric("건강 습관 점수", f"{user_score}/100")

    st.caption(
        "참고 나이는 이 프로그램의 임의적인 교육용 계산식으로 산출됩니다. "
        "실제 생물학적 나이를 의미하지 않습니다."
    )

    st.subheader("🏅 같은 연령대에서의 상대적 위치")

    if comparison_available:
        st.write(
            f"입력 연령대: **{user_group}** · "
            f"비교 자료: **{len(same_group)}명**"
        )

        st.markdown(f"### 결과: {rank_label}")

        st.write(
            f"비교 자료에서 점수가 사용자 점수 이하인 응답자의 비율은 "
            f"약 {percentile:.0f}%입니다. 이는 해당 자료 안에서의 "
            "상대적 위치일 뿐, 실제 건강 수준이나 질병 위험의 순위가 아닙니다."
        )

        if not is_uploaded_data:
            st.warning(
                "현재 비교 결과는 시연용 예시 응답을 바탕으로 합니다. "
                "실제 인구의 상위권·중위권·하위권을 나타내지 않습니다."
            )

        # 점수 분포와 사용자 점수를 같은 그래프에 표시합니다.
        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=same_group["health_score"],
            nbinsx=10,
            name="연령대 비교 자료",
            opacity=0.75
        ))

        fig.add_vline(
            x=user_score,
            line_dash="dash",
            line_width=3,
            annotation_text=f"내 점수: {user_score}",
            annotation_position="top"
        )

        fig.update_layout(
            title=f"{user_group} 건강 습관 점수 분포",
            xaxis_title="건강 습관 점수",
            yaxis_title="응답자 수",
            bargap=0.12,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning(
            f"{user_group} 비교 자료가 5명 미만이어서 "
            "상위권·중위권·하위권을 표시하지 않았습니다. "
            "같은 연령대의 응답 자료를 더 확보하세요."
        )

    # -----------------------------------------------------
    # 사용자와 같은 연령대의 건강 설문 지표 비교
    # -----------------------------------------------------
    st.subheader("📈 내 응답과 같은 연령대의 평균 비교")

    if len(same_group) > 0:
        comparison_rows = [
            ("수면 시간", "sleep_hours", sleep, "시간"),
            ("주간 신체 활동", "exercise_min_week", exercise, "분/주"),
            ("과일·채소 섭취", "fruit_veg_servings", vegetables, "회/일"),
            ("가공식품·당류 음료 섭취 빈도", "processed_days_week",
             processed_days, "일/주"),
            ("스트레스 체감", "stress_level", stress, "점 (1~5)"),
            ("주관적 건강 상태", "self_rated_health",
             self_health, "점 (1~5)")
        ]

        comparison_table = []

        for label, column, user_value, unit in comparison_rows:
            average = same_group[column].mean()

            comparison_table.append({
                "항목": label,
                "내 응답": user_value,
                "비교 자료 평균": round(float(average), 1),
                "단위": unit
            })

        st.dataframe(
            pd.DataFrame(comparison_table),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            "비교 자료 평균은 사용자가 업로드한 설문 데이터 또는 "
            "시연용 예시 데이터의 평균입니다. 공식 건강 통계의 평균이 아닙니다."
        )
    else:
        st.warning(
            "해당 연령대의 비교 자료가 없어 평균 비교를 표시할 수 없습니다."
        )

    # -----------------------------------------------------
    # 점수 구성 설명
    # -----------------------------------------------------
    st.subheader("🔎 점수에 반영된 항목")

    components = {
        "수면": 20,
        "신체 활동": 20,
        "과일·채소 섭취": 20,
        "가공식품·당류 음료 빈도": 15,
        "스트레스 체감": 15,
        "주관적 건강 상태": 10
    }

    score_table = pd.DataFrame({
        "항목": list(components.keys()),
        "배점": list(components.values())
    })

    st.bar_chart(
        score_table.set_index("항목"),
        y="배점"
    )

    st.info(
        "진단받은 질환과 가족력은 참고를 위해 질문했지만 점수 계산에는 "
        "포함하지 않았습니다. 가족력이나 질환 유무만으로 개인의 노화 정도를 "
        "판단할 수 없기 때문입니다."
    )

    if known_conditions and "해당 없음" not in known_conditions:
        st.write(
            "추가 건강 정보가 입력되었습니다. 이 프로그램은 해당 정보를 "
            "진단이나 위험도 계산에 사용하지 않습니다."
        )

    st.subheader("💡 결과를 해석할 때 주의할 점")
    st.write(
        "이 결과는 제한된 설문 항목을 점수화한 교육용 분석입니다. "
        "유전적 요인, 혈액검사 결과, 장기 기능, 실제 신체 기능 등 "
        "다양한 요소를 반영하지 않습니다. 따라서 점수가 높다고 생물학적 "
        "나이가 젊다는 뜻도 아니고, 점수가 낮다고 노화가 빠르다는 뜻도 아닙니다. "
        "건강 문제나 검사 결과가 걱정된다면 의료 전문가의 설명을 참고하세요."
    )

else:
    st.info(
        "위 질문에 답한 뒤 '건강 습관 분석하기'를 누르면 결과가 표시됩니다."
    )

# =========================================================
# 7. 비교 CSV 예시 형식 안내
# =========================================================
with st.expander("📄 비교용 CSV 파일 형식 확인하기"):
    st.write(
        "비교 자료는 프로그램의 설문과 같은 항목으로 수집되어야 합니다. "
        "첫 번째 행에는 아래 열 이름을 정확하게 입력하세요."
    )

    example = pd.DataFrame([
        {
            "age": 17,
            "sleep_hours": 8,
            "exercise_min_week": 420,
            "fruit_veg_servings": 5,
            "processed_days_week": 2,
            "stress_level": 2,
            "self_rated_health": 4
        },
        {
            "age": 18,
            "sleep_hours": 7,
            "exercise_min_week": 180,
            "fruit_veg_servings": 3,
            "processed_days_week": 3,
            "stress_level": 3,
            "self_rated_health": 3
        }
    ])

    st.dataframe(example, use_container_width=True, hide_index=True)

    st.caption(
        "위 두 행은 CSV 구조를 보여주기 위한 예시일 뿐입니다. "
        "실제 연령대별 순위를 분석하려면 동일한 설문을 충분한 인원에게 "
        "실시한 비교 자료가 필요합니다. 개인정보가 포함된 파일은 업로드하지 마세요."
    )
