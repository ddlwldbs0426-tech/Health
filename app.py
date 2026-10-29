
import base64

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# =========================================================
# 1. 페이지 설정과 디자인
# =========================================================
st.set_page_config(
    page_title="건강나이 연구소",
    page_icon="🥟",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Jua&family=Noto+Sans+KR:wght@400;500;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}
.stApp {
    background: linear-gradient(180deg, #f2f8ff, #fff8f0);
}
.main .block-container {
    max-width: 1120px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
.hero {
    padding: 1.5rem;
    border-radius: 24px;
    background: linear-gradient(120deg, #dff3ff, #f2eaff);
    margin-bottom: 1rem;
    border: 1px solid #e2e8f5;
}
.hero-title {
    font-family: 'Jua', sans-serif;
    font-size: 2.5rem;
    color: #20314f;
}
.hero-subtitle {
    color: #52617c;
    margin-top: .4rem;
}
.panel, .result-panel {
    background: white;
    border: 1px solid #e3eaf5;
    border-radius: 20px;
    padding: 1.2rem;
}
.result-panel {
    background: linear-gradient(135deg, #ffffff, #f3f8ff);
    margin-bottom: 1rem;
}
.character-title {
    font-family: 'Jua', sans-serif;
    font-size: 1.5rem;
    color: #2b426c;
}
.character-subtitle {
    font-size: .9rem;
    line-height: 1.6;
    color: #63718a;
}
.result-label {
    font-size: .95rem;
    font-weight: 700;
    color: #5b6b84;
}
.result-age {
    font-family: 'Jua', sans-serif;
    font-size: 3rem;
    color: #3158a5;
}
.notice {
    background: #fff7df;
    border: 1px solid #f3df9d;
    color: #72591c;
    border-radius: 14px;
    padding: 1rem;
    font-size: .88rem;
    line-height: 1.65;
}
div[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e8edf5;
    border-radius: 14px;
    padding: .8rem;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# 2. 안경만두 픽셀 캐릭터 생성
# SVG의 사각형 픽셀을 조합해 만두를 직접 그립니다.
# =========================================================
def make_pixel_dumpling(age):
    # 나이에 따라 옷과 소품이 바뀝니다.
    if age < 30:
        outfit = "#72B9F5"
        accessory = "#FFD45C"
        title = "반짝반짝 청춘 만두"
        caption = "호기심과 에너지가 넘치는 만두!"
        symbol = "star"

    elif age < 40:
        outfit = "#F19BB9"
        accessory = "#F3A6C4"
        title = "활기찬 만두"
        caption = "새로운 도전을 즐기는 만두!"
        symbol = "flower"

    elif age < 50:
        outfit = "#67B99A"
        accessory = "#65B58B"
        title = "든든한 만두"
        caption = "경험과 여유가 쌓이는 만두!"
        symbol = "leaf"

    elif age < 60:
        outfit = "#F09A7D"
        accessory = "#F3A6C4"
        title = "여유로운 만두"
        caption = "나만의 리듬을 찾아가는 만두!"
        symbol = "flower"

    elif age < 70:
        outfit = "#72A9D8"
        accessory = "#FFD45C"
        title = "지혜로운 안경만두"
        caption = "경험과 지혜가 빛나는 만두!"
        symbol = "star"

    else:
        outfit = "#B5A0E8"
        accessory = "#E9A1C3"
        title = "인생 선배 만두"
        caption = "나만의 이야기가 가득한 만두!"
        symbol = "heart"

    # 1칸 = 8픽셀. H=만두 윤곽, D=만두 몸통
    # C=옷, L=다리, S=신발
    sprite = [
        ".......HHHH.......",
        ".....HHDDDDHH.....",
        "....HDDDDDDDDH....",
        "...HDDDDDDDDDDH...",
        "..HDDDDDDDDDDDDH..",
        "..HDDDDDDDDDDDDH..",
        ".HDDDDDDDDDDDDDDH.",
        ".HDDDDDDDDDDDDDDH.",
        ".HDDDDDDDDDDDDDDH.",
        ".HDDDDDDDDDDDDDDH.",
        "..HDDDDDDDDDDDDH..",
        "..HDDDDDDDDDDDDH..",
        "...HDDDDDDDDDDH...",
        "....HDDDDDDDDH....",
        ".....HHHHHHHH......",
        "......CCCCCC.......",
        ".....CCCCCCCC......",
        "......LL..LL........",
        "......SS..SS........",
    ]

    # 줄 길이를 맞춰 모든 픽셀이 정확히 정렬되도록 합니다.
    width = max(len(row) for row in sprite)
    sprite = [row.ljust(width, ".") for row in sprite]

    colors = {
        "H": "#B9AFA7",  # 만두 테두리
        "D": "#FFFDF5",  # 만두피
        "C": outfit,     # 옷
        "L": "#59647B",  # 다리
        "S": "#34415B",  # 신발
    }

    pixel = 8
    rects = []

    for y, row in enumerate(sprite):
        for x, char in enumerate(row):
            if char in colors:
                rects.append(
                    f'<rect x="{x * pixel}" y="{y * pixel}" '
                    f'width="{pixel}" height="{pixel}" '
                    f'fill="{colors[char]}"/>'
                )

    # 볼터치
    rects.extend([
        '<rect x="40" y="72" width="16" height="8" fill="#F6B6B6"/>',
        '<rect x="88" y="72" width="16" height="8" fill="#F6B6B6"/>',
    ])

    # 안경테와 안경다리도 픽셀 사각형으로 그립니다.
    glasses = """
      <rect x="40" y="48" width="24" height="8" fill="#39465B"/>
      <rect x="40" y="56" width="8" height="16" fill="#39465B"/>
      <rect x="48" y="64" width="16" height="8" fill="#39465B"/>
      <rect x="64" y="56" width="8" height="8" fill="#39465B"/>

      <rect x="72" y="48" width="24" height="8" fill="#39465B"/>
      <rect x="88" y="56" width="8" height="16" fill="#39465B"/>
      <rect x="72" y="64" width="16" height="8" fill="#39465B"/>
      <rect x="64" y="48" width="8" height="8" fill="#39465B"/>
    """

    # 안경 안의 작은 눈
    eyes = """
      <rect x="48" y="56" width="8" height="8" fill="#34415B"/>
      <rect x="80" y="56" width="8" height="8" fill="#34415B"/>
    """

    # 작은 입
    mouth = """
      <rect x="64" y="80" width="8" height="8" fill="#B66F72"/>
      <rect x="56" y="72" width="8" height="8" fill="#B66F72"/>
      <rect x="72" y="72" width="8" height="8" fill="#B66F72"/>
    """

    # 나이대별 장식도 모두 픽셀로 그립니다.
    decorations = {
        "star": """
          <rect x="128" y="32" width="8" height="24" fill="#FFD45C"/>
          <rect x="120" y="40" width="24" height="8" fill="#FFD45C"/>
        """,
        "flower": """
          <rect x="128" y="32" width="8" height="8" fill="#F3A6C4"/>
          <rect x="120" y="40" width="8" height="8" fill="#F3A6C4"/>
          <rect x="136" y="40" width="8" height="8" fill="#F3A6C4"/>
          <rect x="128" y="48" width="8" height="8" fill="#F3A6C4"/>
          <rect x="128" y="40" width="8" height="8" fill="#F4D46A"/>
        """,
        "leaf": """
          <rect x="120" y="40" width="8" height="8" fill="#65B58B"/>
          <rect x="128" y="32" width="8" height="8" fill="#65B58B"/>
          <rect x="136" y="32" width="8" height="8" fill="#65B58B"/>
          <rect x="128" y="40" width="8" height="8" fill="#65B58B"/>
          <rect x="136" y="48" width="8" height="8" fill="#65B58B"/>
        """,
        "heart": """
          <rect x="120" y="36" width="8" height="8" fill="#E9A1C3"/>
          <rect x="136" y="36" width="8" height="8" fill="#E9A1C3"/>
          <rect x="120" y="44" width="24" height="8" fill="#E9A1C3"/>
          <rect x="128" y="52" width="8" height="8" fill="#E9A1C3"/>
        """,
    }

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="176" height="184" viewBox="0 0 176 184"
         shape-rendering="crispEdges">
      <rect x="4" y="4" width="168" height="176" rx="12" fill="#EFF6FF"/>
      <rect x="12" y="12" width="152" height="160" fill="#F9FBFF"/>
      {''.join(rects)}
      {glasses}
      {eyes}
      {mouth}
      {decorations[symbol]}
    </svg>
    """

    return svg, title, caption


# =========================================================
# 3. 가상 건강 기준 프로필
# 실제 의료 자료가 아닌 시연용 수식입니다.
# =========================================================
METRICS = {
    "수축기 혈압": ("mmHg", 1.0, 12),
    "이완기 혈압": ("mmHg", 0.8, 8),
    "공복 혈당": ("mg/dL", 1.2, 15),
    "HDL 콜레스테롤": ("mg/dL", 1.0, 12),
    "중성지방": ("mg/dL", 0.9, 35),
    "허리둘레": ("cm", 0.8, 10),
}


def expected_profile(age, sex):
    female = sex == "여"

    return {
        "수축기 혈압": 108 + 0.42 * (age - 18),
        "이완기 혈압": 68 + 0.16 * (age - 18),
        "공복 혈당": 83 + 0.30 * (age - 18),
        "HDL 콜레스테롤": (61 if female else 54) - 0.10 * (age - 18),
        "중성지방": 82 + 0.55 * (age - 18),
        "허리둘레": (66 if female else 72) + 0.24 * (age - 18),
    }


def predict_body_age(values, sex):
    candidates = []

    for age in range(18, 81):
        profile = expected_profile(age, sex)
        distance = 0

        for metric, value in values.items():
            unit, weight, scale = METRICS[metric]
            distance += weight * ((value - profile[metric]) / scale) ** 2

        candidates.append({
            "age": age,
            "distance": distance,
        })

    body_age = min(candidates, key=lambda x: x["distance"])["age"]
    return body_age, candidates


# =========================================================
# 4. 그래프
# =========================================================
def similarity_chart(candidates, body_age):
    ages = [x["age"] for x in candidates]
    distances = np.array([x["distance"] for x in candidates])
    similarity = 100 / (1 + distances)

    fig = go.Figure(go.Scatter(
        x=ages,
        y=similarity,
        mode="lines",
        fill="tozeroy",
        line={"width": 3},
        hovertemplate="비교 나이 %{x}세<br>시각화용 값 %{y:.1f}<extra></extra>",
    ))

    fig.add_vline(
        x=body_age,
        line_dash="dash",
        annotation_text=f"추정 {body_age}세",
    )

    fig.update_layout(
        height=300,
        margin=dict(l=10, r=10, t=25, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,.8)",
        xaxis=dict(title="비교 나이(세)", range=[18, 80], dtick=10),
        yaxis=dict(title="시각화용 유사도", range=[0, 100]),
        showlegend=False,
        uirevision="fixed-similarity",
    )

    return fig


def metric_chart(values, sex):
    ages = list(range(18, 81))
    fig = go.Figure()

    for metric, value in values.items():
        fig.add_trace(go.Scatter(
            x=ages,
            y=[expected_profile(age, sex)[metric] for age in ages],
            mode="lines",
            name=metric,
        ))

        fig.add_trace(go.Scatter(
            x=[st.session_state.health_result["body_age"]],
            y=[value],
            mode="markers",
            showlegend=False,
            marker={"size": 9},
            hovertemplate=f"{metric}<br>입력값 {value}<extra></extra>",
        ))

    fig.update_layout(
        height=370,
        margin=dict(l=10, r=10, t=20, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,.8)",
        xaxis=dict(title="비교 나이(세)", range=[18, 80], dtick=10),
        yaxis=dict(title="지표 값", rangemode="tozero"),
        legend=dict(orientation="h", y=1.02, x=0),
        uirevision="fixed-metrics",
    )

    return fig


# =========================================================
# 5. 메인 화면
# =========================================================
st.markdown("""
<div class="hero">
  <div class="hero-title">건강나이 연구소</div>
  <div class="hero-subtitle">
    건강 지표를 입력하고 귀여운 안경만두와 함께 결과를 확인해 보세요!
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
<b>꼭 확인해 주세요.</b> 이 앱은 코딩 시연용 가상 모델입니다.
의학적으로 검증된 건강나이 측정기가 아니며 진단이나 치료 판단에 사용할 수 없습니다.
기준값과 계산 결과는 설명을 위해 만든 예시입니다.
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1.15, 0.85], gap="large")

with left:
    st.subheader("건강 지표 입력")
    st.caption("건강검진 결과가 있다면 참고하세요. 기본값으로도 체험할 수 있어요.")

    with st.form("health_form"):
        col1, col2 = st.columns(2)

        with col1:
            actual_age = st.number_input("실제 나이", 18, 80, 35, 1)
            sex = st.selectbox("프로필 기준", ["여", "남"])
            systolic = st.number_input("수축기 혈압 (mmHg)", 70, 250, 120, 1)
            diastolic = st.number_input("이완기 혈압 (mmHg)", 40, 150, 80, 1)

        with col2:
            glucose = st.number_input("공복 혈당 (mg/dL)", 40, 400, 95, 1)
            hdl = st.number_input("HDL 콜레스테롤 (mg/dL)", 10, 150, 55, 1)
            triglycerides = st.number_input("중성지방 (mg/dL)", 20, 1000, 120, 1)
            waist = st.number_input("허리둘레 (cm)", 40, 180, 80, 1)

        submitted = st.form_submit_button(
            "안경만두와 결과 보기",
            type="primary",
            use_container_width=True,
        )

with right:
    st.subheader("이용 방법")
    st.write(
        "건강 지표를 입력하고 결과 버튼을 누르면 가상 기준 프로필과 비교한 결과가 나타납니다."
    )
    st.write(
        "추정 나이 구간에 따라 안경만두의 옷 색과 장식이 달라집니다."
    )
    st.write(
        "안경만두는 실제 외모나 건강 상태를 예측하지 않는 픽셀 캐릭터입니다."
    )


# =========================================================
# 6. 계산 및 결과 저장
# =========================================================
if submitted:
    if diastolic >= systolic:
        st.error("입력값을 확인해 주세요. 이완기 혈압은 수축기 혈압보다 낮게 입력해야 합니다.")
    else:
        values = {
            "수축기 혈압": float(systolic),
            "이완기 혈압": float(diastolic),
            "공복 혈당": float(glucose),
            "HDL 콜레스테롤": float(hdl),
            "중성지방": float(triglycerides),
            "허리둘레": float(waist),
        }

        body_age, candidates = predict_body_age(values, sex)

        st.session_state.health_result = {
            "actual_age": int(actual_age),
            "body_age": int(body_age),
            "sex": sex,
            "values": values,
            "candidates": candidates,
        }


# 결과는 다시 계산하기 전까지 유지
result = st.session_state.get("health_result")

if result:
    actual_age = result["actual_age"]
    body_age = result["body_age"]
    values = result["values"]
    difference = body_age - actual_age

    svg, character_title, character_caption = make_pixel_dumpling(body_age)
    svg64 = base64.b64encode(svg.encode("utf-8")).decode("ascii")

    st.markdown("## 나의 건강나이 결과")

    char_col, info_col = st.columns([0.8, 1.5], gap="large")

    with char_col:
        st.markdown(f"""
        <div class="result-panel" style="text-align:center;">
          <div class="character-title">{character_title}</div>
          <img
            src="data:image/svg+xml;base64,{svg64}"
            width="200"
            alt="안경을 쓴 픽셀 만두 캐릭터"
            style="image-rendering:pixelated;display:block;margin:10px auto;"
          >
          <div class="character-subtitle">{character_caption}</div>
          <div class="character-subtitle" style="margin-top:10px;font-size:.8rem;">
            나이대별로 꾸며지는 나만의 안경만두!
          </div>
        </div>
        """, unsafe_allow_html=True)

    with info_col:
        color = (
            "#D97757" if difference > 0
            else "#3C8D78" if difference < 0
            else "#64748B"
        )

        st.markdown(f"""
        <div class="result-panel">
          <div class="result-label">가상 프로필 기반 추정 건강나이</div>
          <div class="result-age">
            {body_age}<span style="font-size:1.3rem;">세</span>
          </div>
          <div style="color:#65738a;">
            실제 나이 {actual_age}세 · 나이 차이
            <b style="color:{color};">{difference:+d}세</b>
          </div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        c1.metric("실제 나이", f"{actual_age}세")
        c2.metric("추정 나이", f"{body_age}세")
        c3.metric("나이 차이", f"{difference:+d}세")

        if difference < 0:
            st.info("입력값이 더 낮은 나이대의 가상 프로필에 가까웠어요. 실제 건강 상태를 판정한 결과는 아닙니다.")
        elif difference > 0:
            st.info("입력값이 더 높은 나이대의 가상 프로필에 가까웠어요. 특정 질환이나 건강 문제를 뜻하지 않습니다.")
        else:
            st.info("입력값이 실제 나이와 같은 나이대의 가상 프로필에 가장 가까웠어요.")

    st.markdown("### 나이대별 프로필 유사도")
    st.caption("설명용 시각화이며 의료적으로 검증된 점수가 아닙니다.")

    st.plotly_chart(
        similarity_chart(result["candidates"], body_age),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    st.markdown("### 입력값과 가상 기준값 비교")

    reference = expected_profile(body_age, result["sex"])

    table = pd.DataFrame([
        {
            "건강 지표": metric,
            "입력값": round(value, 1),
            "추정 나이대의 가상 기준값": round(reference[metric], 1),
            "단위": METRICS[metric][0],
        }
        for metric, value in values.items()
    ])

    st.dataframe(table, use_container_width=True, hide_index=True)

    st.markdown("### 지표별 가상 기준 변화")
    st.caption("실제 인구 자료가 아닌 예시 수식으로 만든 기준선입니다.")

    st.plotly_chart(
        metric_chart(values, result["sex"]),
        use_container_width=True,
        config={"displayModeBar": False},
    )

    st.markdown("""
    <div class="notice">
    <b>결과 해석에 주의하세요.</b> 건강은 몇 가지 수치만으로 결정되지 않습니다.
    이 결과는 재미와 코딩 시연을 위한 것이며 건강 상태를 진단하지 않습니다.
    건강에 관한 판단은 의료 전문가와 상담하세요.
    </div>
    """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="result-panel" style="text-align:center;padding:2rem;">
      <div class="character-title">안경만두가 기다리고 있어요!</div>
      <div class="character-subtitle">
        건강 지표를 입력하고 결과 버튼을 누르면 안경만두가 나타납니다.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.caption(
    "건강나이 연구소 · 교육 및 프로그래밍 시연용 · 의료기기 또는 진단 서비스가 아닙니다."
)
