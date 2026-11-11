
import io
import zipfile
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

warnings.filterwarnings("ignore")


# =========================================================
# 1. 기본 설정
# =========================================================

st.set_page_config(
    page_title="AI 건강나이 분석",
    page_icon="🧬",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #F6F8FC;
}

.main-title {
    font-size: 34px;
    font-weight: 800;
    color: #203B63;
}

.sub-title {
    color: #687991;
    font-size: 16px;
}

div[data-testid="stMetric"] {
    background-color: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #E5EAF2;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
}

</style>
""", unsafe_allow_html=True)


st.markdown(
    '<div class="main-title">🧬 AI 건강나이 분석</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    '국민건강영양조사 데이터를 활용한 건강지표 기반 연령 추정'
    '</div>',
    unsafe_allow_html=True
)

st.divider()


# =========================================================
# 2. SAS 원시자료 읽기
# =========================================================

@st.cache_data(show_spinner="건강데이터를 불러오는 중입니다...")
def load_sas_data(file_bytes, file_name):

    # ZIP 파일인 경우 내부의 SAS 파일 찾기
    if file_name.lower().endswith(".zip"):

        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:

            sas_files = [
                name for name in z.namelist()
                if name.lower().endswith(".sas7bdat")
            ]

            if not sas_files:
                raise ValueError(
                    "ZIP 파일 내부에서 SAS7BDAT 파일을 찾지 못했습니다."
                )

            # 파일명에 HN24_ALL이 포함된 파일 우선 선택
            sas_files.sort(
                key=lambda x: (
                    "hn24_all" not in x.lower(),
                    x.lower()
                )
            )

            sas_bytes = z.read(sas_files[0])

            # encoding=None으로 읽어 UTF-8 강제 변환 오류 방지
            df = pd.read_sas(
                io.BytesIO(sas_bytes),
                format="sas7bdat",
                encoding=None
            )

    elif file_name.lower().endswith(".sas7bdat"):

        df = pd.read_sas(
            io.BytesIO(file_bytes),
            format="sas7bdat",
            encoding=None
        )

    else:
        raise ValueError(
            "ZIP 또는 SAS7BDAT 파일을 업로드해 주세요."
        )

    # 변수명 디코딩
    decoded_columns = []

    for col in df.columns:

        if isinstance(col, bytes):
            try:
                col = col.decode("cp949")
            except UnicodeDecodeError:
                col = col.decode("utf-8", errors="replace")

        decoded_columns.append(str(col).strip())

    df.columns = decoded_columns

    # 문자형 데이터 디코딩
    for col in df.select_dtypes(include=["object"]).columns:

        def decode_value(value):

            if isinstance(value, bytes):

                try:
                    return value.decode("cp949").strip()

                except UnicodeDecodeError:

                    return value.decode(
                        "utf-8",
                        errors="replace"
                    ).strip()

            return value

        df[col] = df[col].apply(decode_value)

    return df


# =========================================================
# 3. 사이드바 설정 및 기본 데이터 자동 연결
# =========================================================

with st.sidebar:

    st.header("📂 데이터 설정")

    st.success("국민건강영양조사 데이터 내장")

    st.caption(
        "기본 데이터는 앱 실행 시 자동으로 불러옵니다."
    )

    uploaded_file = st.file_uploader(
        "다른 데이터로 변경하기 (선택)",
        type=["zip", "sas7bdat"]
    )

    st.divider()

    st.header("⚙️ 분석 설정")

    test_size = st.slider(
        "테스트 데이터 비율",
        min_value=0.1,
        max_value=0.4,
        value=0.2,
        step=0.05
    )

    n_estimators = st.slider(
        "Random Forest 학습 트리 수",
        min_value=100,
        max_value=600,
        value=300,
        step=50
    )


# GitHub 저장소의 기본 데이터 경로
DATA_PATH = (
    Path(__file__).parent
    / "HN24_ALL(SAS).zip"
)


# 업로드 파일이 있으면 업로드 파일 사용
if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name

# 업로드 파일이 없으면 저장소의 기본 파일 사용
elif DATA_PATH.exists():

    file_bytes = DATA_PATH.read_bytes()
    file_name = DATA_PATH.name

else:

    st.error(
        "기본 건강데이터를 찾을 수 없습니다."
    )

    st.markdown("""
    GitHub 저장소에 다음 경로로 파일을 넣어주세요.

    `data/HN24_ALL(SAS).zip`
    """)

    st.stop()


# =========================================================
# 4. 데이터 불러오기
# =========================================================

try:

    df = load_sas_data(
        file_bytes,
        file_name
    )

except Exception as e:

    st.error(
        f"데이터를 읽지 못했습니다: {e}"
    )

    st.stop()


st.success("국민건강영양조사 원시자료 연결 완료")


# =========================================================
# 5. 원시자료 기본 정보
# =========================================================

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "전체 조사 대상자",
        f"{len(df):,}명"
    )

with col2:

    st.metric(
        "전체 변수 수",
        f"{len(df.columns):,}개"
    )

with col3:

    memory_size = (
        df.memory_usage(deep=True).sum()
        / 1024**2
    )

    st.metric(
        "메모리 사용량",
        f"{memory_size:.1f} MB"
    )


with st.expander("원시자료 미리보기"):

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


with st.expander("전체 변수명 확인"):

    st.write(list(df.columns))


# =========================================================
# 6. 변수 자동 탐색
# =========================================================

column_lookup = {
    str(col).lower(): col
    for col in df.columns
}


variable_candidates = {

    "age": ["age"],

    "sex": ["sex"],

    "수축기 혈압": ["he_sbp"],

    "이완기 혈압": ["he_dbp"],

    "공복혈당": ["he_glu"],

    "당화혈색소": ["he_hba1c"],

    "HDL 콜레스테롤": [
        "he_hdl_st2",
        "he_hdl"
    ],

    "중성지방": ["he_tg"],

    "허리둘레": ["he_wc"],

    "체질량지수": ["he_bmi"],

    "고감도 CRP": ["he_hscrp"],

    "백혈구 수": ["he_wbc"],

    "1초간 노력성 호기량": ["he_fev1"]

}


found_columns = {}

for label, candidates in variable_candidates.items():

    for candidate in candidates:

        if candidate.lower() in column_lookup:

            found_columns[label] = column_lookup[
                candidate.lower()
            ]

            break


if "age" not in found_columns:

    st.error(
        "연령 변수(age)를 찾지 못했습니다. "
        "실제 변수명을 확인해야 합니다."
    )

    st.stop()


if "sex" not in found_columns:

    st.warning(
        "성별 변수(sex)를 찾지 못했습니다. "
        "이번 모델에서는 성별을 제외합니다."
    )


# =========================================================
# 7. 분석 변수 선택
# =========================================================

st.divider()

st.subheader("🔎 분석에 사용할 건강지표")

feature_labels = [

    "수축기 혈압",

    "이완기 혈압",

    "공복혈당",

    "당화혈색소",

    "HDL 콜레스테롤",

    "중성지방",

    "허리둘레",

    "체질량지수",

    "고감도 CRP",

    "백혈구 수",

    "1초간 노력성 호기량"

]


available_features = [

    label
    for label in feature_labels
    if label in found_columns

]


# 성별 변수 추가
if "sex" in found_columns:

    available_features.insert(
        0,
        "sex"
    )


selected_features = st.multiselect(

    "머신러닝 학습에 포함할 변수",

    options=available_features,

    default=available_features

)


if len(selected_features) < 3:

    st.warning(
        "최소 3개 이상의 건강지표를 선택해 주세요."
    )

    st.stop()


# =========================================================
# 8. 데이터 전처리
# =========================================================

age_col = found_columns["age"]

model_df = pd.DataFrame()


# 연령 변수
model_df["age"] = pd.to_numeric(
    df[age_col],
    errors="coerce"
)


# 선택한 건강지표
for label in selected_features:

    if label == "sex":

        source_col = found_columns["sex"]

    else:

        source_col = found_columns[label]

    model_df[label] = pd.to_numeric(
        df[source_col],
        errors="coerce"
    )


# 무한대 값 제거
model_df = model_df.replace(
    [np.inf, -np.inf],
    np.nan
)


# 성인 자료만 분석
model_df = model_df[
    (model_df["age"] >= 19)
    & (model_df["age"] <= 100)
].copy()


# 전체가 결측인 변수 제거
usable_features = [

    col
    for col in selected_features
    if model_df[col].notna().sum() > 0

]


if len(usable_features) < 3:

    st.error(
        "실제 값이 존재하는 건강지표가 3개 미만입니다."
    )

    st.stop()


model_df = model_df[
    ["age"] + usable_features
].copy()


# 모든 건강지표가 결측인 행 제거
model_df = model_df.dropna(
    subset=usable_features,
    how="all"
)


if len(model_df) < 100:

    st.error(
        "전처리 후 분석 가능한 데이터가 너무 적습니다."
    )

    st.stop()


# =========================================================
# 9. 전처리 결과 확인
# =========================================================

st.subheader("🧹 데이터 전처리 결과")

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "분석 대상자",
        f"{len(model_df):,}명"
    )

with c2:

    st.metric(
        "사용 건강지표",
        f"{len(usable_features)}개"
    )

with c3:

    st.metric(
        "평균 연령",
        f"{model_df['age'].mean():.1f}세"
    )


with st.expander("변수별 결측값 확인"):

    missing_table = pd.DataFrame({

        "변수": usable_features,

        "결측값 수": [

            model_df[col].isna().sum()
            for col in usable_features

        ],

        "결측 비율(%)": [

            model_df[col].isna().mean() * 100
            for col in usable_features

        ]

    })

    st.dataframe(
        missing_table.round(2),
        use_container_width=True
    )


# =========================================================
# 10. 학습 데이터 구성
# =========================================================

X = model_df[usable_features]

y = model_df["age"]


X_train, X_test, y_train, y_test = train_test_split(

    X,

    y,

    test_size=test_size,

    random_state=42

)


# =========================================================
# 11. Random Forest 모델 학습
# =========================================================

@st.cache_resource(
    show_spinner="AI 모델을 학습하고 있습니다..."
)

def train_model(
    X_train,
    y_train,
    X_test,
    y_test,
    n_trees
):

    model = Pipeline([

        (
            "imputer",

            SimpleImputer(
                strategy="median"
            )

        ),

        (
            "random_forest",

            RandomForestRegressor(

                n_estimators=n_trees,

                min_samples_leaf=3,

                random_state=42,

                n_jobs=-1

            )

        )

    ])


    model.fit(
        X_train,
        y_train
    )


    predictions = model.predict(
        X_test
    )


    mae = mean_absolute_error(
        y_test,
        predictions
    )


    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )


    r2 = r2_score(
        y_test,
        predictions
    )


    return (
        model,
        predictions,
        mae,
        rmse,
        r2
    )


model, predictions, mae, rmse, r2 = train_model(

    X_train,

    y_train,

    X_test,

    y_test,

    n_estimators

)


# =========================================================
# 12. 모델 성능 평가
# =========================================================

st.divider()

st.subheader("🤖 AI 모델 성능 평가")


m1, m2, m3 = st.columns(3)


with m1:

    st.metric(
        "MAE",
        f"{mae:.2f}세"
    )


with m2:

    st.metric(
        "RMSE",
        f"{rmse:.2f}세"
    )


with m3:

    st.metric(
        "R²",
        f"{r2:.3f}"
    )


st.caption(
    "MAE와 RMSE는 예측 연령과 실제 연령 사이의 오차를 나타냅니다. "
    "R²는 테스트 자료에서 연령 변동을 설명하는 정도입니다."
)


# 실제 연령과 예측 연령 비교
result_df = pd.DataFrame({

    "실제 연령": y_test.values,

    "예측 연령": predictions

})


fig = px.scatter(

    result_df,

    x="실제 연령",

    y="예측 연령",

    opacity=0.55,

    title="실제 연령과 AI 예측 연령 비교"

)


min_age = min(

    result_df["실제 연령"].min(),

    result_df["예측 연령"].min()

)


max_age = max(

    result_df["실제 연령"].max(),

    result_df["예측 연령"].max()

)


fig.add_trace(

    go.Scatter(

        x=[min_age, max_age],

        y=[min_age, max_age],

        mode="lines",

        name="완벽한 예측 기준선",

        line=dict(
            dash="dash"
        )

    )

)


fig.update_layout(

    height=450,

    xaxis_title="실제 연령(세)",

    yaxis_title="예측 연령(세)"

)


st.plotly_chart(
    fig,
    use_container_width=True
)


# =========================================================
# 13. 개인 건강지표 입력
# =========================================================

st.divider()

st.subheader("🧑 개인 건강지표 분석")


st.write(
    "건강검진 결과를 입력하면 학습된 AI 모델이 "
    "건강지표 기반 연령을 추정합니다."
)


medians = X.median(
    numeric_only=True
)


input_values = {}

input_columns = st.columns(2)


for i, feature in enumerate(usable_features):

    default_value = medians[feature]

    if pd.isna(default_value):

        default_value = 0.0


    with input_columns[i % 2]:

        if feature == "sex":

            input_values[feature] = st.selectbox(

                "성별",

                options=[1, 2],

                format_func=lambda x: (
                    "남성" if x == 1 else "여성"
                )

            )

        else:

            input_values[feature] = st.number_input(

                feature,

                value=float(default_value),

                format="%.2f"

            )


if st.button(

    "건강지표 기반 연령 추정하기",

    type="primary",

    use_container_width=True

):

    user_df = pd.DataFrame(

        [input_values],

        columns=usable_features

    )


    predicted_age = float(
        model.predict(user_df)[0]
    )


    # 학습 데이터의 연령 범위 내에서 표시
    predicted_age = float(

        np.clip(

            predicted_age,

            y.min(),

            y.max()

        )

    )


    st.session_state["user_df"] = user_df

    st.session_state["predicted_age"] = predicted_age


    st.success(
        "건강지표 분석이 완료되었습니다."
    )


# =========================================================
# 14. 개인 분석 결과
# =========================================================

if "predicted_age" in st.session_state:

    predicted_age = st.session_state["predicted_age"]


    st.markdown("### 분석 결과")


    result_col1, result_col2 = st.columns(2)


    with result_col1:

        st.metric(

            "건강지표 기반 연령 추정값",

            f"{predicted_age:.1f}세"

        )


    with result_col2:

        st.metric(

            "학습 데이터 평균 연령",

            f"{y.mean():.1f}세"

        )


    st.info(
        "이 결과는 건강지표와 연령 사이의 통계적 관계를 학습한 "
        "모델의 추정값입니다. 의학적으로 검증된 생물학적 나이나 "
        "실제 노화 정도를 직접 측정한 값은 아닙니다."
    )


# =========================================================
# 15. SHAP 분석
# =========================================================

st.divider()

st.subheader("🔬 SHAP 분석")

st.write(
    "개인별 건강지표 중 어떤 변수가 모델의 연령 예측에 "
    "상대적으로 크게 기여했는지 분석합니다."
)


if "user_df" in st.session_state:

    try:

        import shap


        rf_model = model.named_steps[
            "random_forest"
        ]


        imputer = model.named_steps[
            "imputer"
        ]


        user_df = st.session_state[
            "user_df"
        ]


        user_imputed = imputer.transform(
            user_df
        )


        explainer = shap.TreeExplainer(
            rf_model
        )


        shap_values = explainer.shap_values(
            user_imputed
        )


        shap_values = np.array(
            shap_values
        ).reshape(-1)


        shap_df = pd.DataFrame({

            "건강지표": usable_features,

            "SHAP 기여도": shap_values

        })


        shap_df["절대 기여도"] = (
            shap_df["SHAP 기여도"].abs()
        )


        shap_df = shap_df.sort_values(
            "절대 기여도",
            ascending=True
        )


        fig_shap = px.bar(

            shap_df,

            x="SHAP 기여도",

            y="건강지표",

            orientation="h",

            title="개인별 건강지표의 예측 기여도"

        )


        st.plotly_chart(

            fig_shap,

            use_container_width=True

        )


        st.caption(
            "양수는 모델의 기준 예측값보다 높은 연령 방향, "
            "음수는 낮은 연령 방향으로 기여했다는 뜻입니다. "
            "인과관계나 건강상 유불리를 의미하지 않습니다."
        )


    except ImportError:

        st.warning(
            "SHAP 패키지가 설치되지 않았습니다. "
            "requirements.txt를 확인해 주세요."
        )


    except Exception as e:

        st.warning(
            f"SHAP 분석 중 오류가 발생했습니다: {e}"
        )


else:

    st.info(
        "개인 건강지표를 입력하면 SHAP 분석 결과가 표시됩니다."
    )


# =========================================================
# 16. K-means 군집분석
# =========================================================

st.divider()

st.subheader("🧩 K-means 건강지표 패턴 분석")


st.write(
    "비슷한 건강지표 조합을 가진 조사 대상자들을 "
    "3개의 군집으로 분류합니다."
)


@st.cache_resource(
    show_spinner="군집분석을 진행하고 있습니다..."
)

def make_clusters(data):

    imputer = SimpleImputer(
        strategy="median"
    )

    scaler = StandardScaler()


    imputed = imputer.fit_transform(
        data
    )


    scaled = scaler.fit_transform(
        imputed
    )


    kmeans = KMeans(

        n_clusters=3,

        random_state=42,

        n_init=10

    )


    clusters = kmeans.fit_predict(
        scaled
    )


    return (
        clusters,
        imputer,
        scaler,
        kmeans
    )


clusters, cluster_imputer, cluster_scaler, kmeans = (
    make_clusters(X)
)


cluster_df = model_df.copy()

cluster_df["군집"] = clusters.astype(str)


# 군집별 인원 및 평균 연령
cluster_summary = (

    cluster_df

    .groupby("군집")

    .agg(

        인원수=("age", "count"),

        평균연령=("age", "mean")

    )

    .reset_index()

)


st.markdown("#### 군집별 분포")


st.dataframe(

    cluster_summary.round(2),

    use_container_width=True

)


# 군집별 건강지표 평균
cluster_means = (

    cluster_df

    .groupby("군집")[usable_features]

    .mean()

    .reset_index()

)


st.markdown("#### 군집별 건강지표 평균")


st.dataframe(

    cluster_means.round(2),

    use_container_width=True

)


# 군집별 인원수 시각화
fig_cluster = px.bar(

    cluster_summary,

    x="군집",

    y="인원수",

    text="인원수",

    title="군집별 조사 대상자 분포"

)


st.plotly_chart(

    fig_cluster,

    use_container_width=True

)


# =========================================================
# 17. 개인과 유사한 군집 확인
# =========================================================

if "user_df" in st.session_state:

    user_df = st.session_state[
        "user_df"
    ]


    user_imputed = cluster_imputer.transform(
        user_df
    )


    user_scaled = cluster_scaler.transform(
        user_imputed
    )


    user_cluster = int(
        kmeans.predict(user_scaled)[0]
    )


    st.metric(

        "가장 유사한 건강지표 패턴 군집",

        f"군집 {user_cluster + 1}"

    )


    st.caption(
        "군집 번호는 유사한 데이터 패턴을 구분하기 위한 식별자이며, "
        "건강 등급이나 질병 위험 순위를 의미하지 않습니다."
    )


# =========================================================
# 18. 분석 유의사항
# =========================================================

st.divider()

st.markdown("""
### 📌 분석 시 유의사항

이 프로그램은 국민건강영양조사 원시자료를 활용하여
건강지표와 연령 사이의 통계적 관계를 학습하는 연구용 프로그램입니다.

예측된 연령은 생물학적 노화를 직접 측정한 값이 아닙니다.

SHAP 분석은 모델의 예측에 영향을 준 변수의 기여도를 나타내며,
변수가 노화를 일으키거나 억제한다는 인과관계를 증명하지 않습니다.

K-means 군집분석은 비슷한 건강지표 패턴을 가진 자료를 분류하는 방법이며,
건강 상태의 우열을 판정하는 방법이 아닙니다.

또한 현재 모델은 국민건강영양조사의 복합표본 설계와 조사 가중치를
반영한 모집단 추정 모델이 아닙니다.
""")

st.caption(
    "데이터 출처: 질병관리청 국민건강영양조사 제9기 원시자료"
)
