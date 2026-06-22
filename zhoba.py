import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import numpy as np
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------------------
# 1. БЕТТІ БАПТАУ
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Қарағанды | Экологиялық қауіп-қатерлер картасы",
    page_icon="🌍",
    layout="wide",
)

KARAGANDY_CENTER = [49.802, 73.085]
START_ZOOM = 12

# ---------------------------------------------------------------------
# 2. ДЕРЕКТЕР БАЗАСЫ (Толық 25 экологиялық нысан)
# ---------------------------------------------------------------------
eco_data = [
    # --- Майқұдық ауданы (6 нысан) ---
    {"name": "Қарағанды металлургия комбинаты ауданы", "area": "Майқұдық", "lat": 49.751, "lon": 73.045, "risk_type": "Ауа", "risk_level": "Жоғары", "description": "Металлургия кәсіпорнынан шығатын күкірт қышқылы мен шаң бөлшектерінің жоғары шоғырлануы байқалады."},
    {"name": "Рұқсат етілмеген қоқыс орны", "area": "Майқұдық", "lat": 49.742, "lon": 73.021, "risk_type": "Су/Топырақ", "risk_level": "Орташа", "description": "Тұрмыстық және құрылыс қалдықтары ресми емес түрде тасталады, топырақтың ластануы мен жерасты суларына қаупі бар."},
    {"name": "Теміржол желісі бойы", "area": "Майқұдық", "lat": 49.758, "lon": 73.038, "risk_type": "Шу", "risk_level": "Орташа", "description": "Жүк пойыздарының түнгі қозғалысы тұрғындардың тыныш ұйқысына теріс әсер етеді."},
    {"name": "Майқұдық зауыттар аймағы", "area": "Майқұдық", "lat": 49.832, "lon": 73.155, "risk_type": "Ауа", "risk_level": "Жоғары", "description": "Машина жасау және құю өндірістерінен бөлінетін қатты бөлшектер мен өндірістік шаң деңгейі жоғары."},
    {"name": "Үлкен Бұқпа өзені", "area": "Майқұдық", "lat": 49.845, "lon": 73.185, "risk_type": "Су/Топырақ", "risk_level": "Орташа", "description": "Тұрмыстық қалдықтармен қоқыстану деңгейі жоғары, өзін-өзі тазарту қабілеті төмендеген."},
    {"name": "Майқұдық ішкі теміржол тармағы", "area": "Майқұдық", "lat": 49.851, "lon": 73.140, "risk_type": "Шу", "risk_level": "Орташа", "description": "Зауыттарға шикізат таситын жүк пойыздарының қозғалысынан болатын діріл мен шу."},

    # --- Пришахтинск ауданы (6 нысан) ---
    {"name": "Шахта №5 өндірістік аймағы", "area": "Пришахтинск", "lat": 49.912, "lon": 73.132, "risk_type": "Ауа", "risk_level": "Жоғары", "description": "Көмір өндіру және байыту фабрикасының жұмысы салдарынан ауаға көмір шаңы мен метан газы түседі."},
    {"name": "Өзен жағасындағы лас алқап", "area": "Пришахтинск", "lat": 49.901, "lon": 73.108, "risk_type": "Су/Топырақ", "risk_level": "Жоғары", "description": "Өнеркәсіп қалдықтары өзен арнасына тікелей ағызылады деген болжам бар, су құрамында ауыр металдар анықталған."},
    {"name": "Теміржол торабы", "area": "Пришахтинск", "lat": 49.897, "lon": 73.121, "risk_type": "Шу", "risk_level": "Орташа", "description": "Вагон ауыстыру және маневр жұмыстары үнемі қайталанатын механикалық шу көзі болып табылады."},
    {"name": "Пришахтинск көмір байыту фабрикасы маңы", "area": "Пришахтинск", "lat": 49.905, "lon": 73.148, "risk_type": "Ауа", "risk_level": "Орташа", "description": "Ауадағы көмір шаңының (PM2.5 және PM10) шоғырлануы нормадан жиі асады."},
    {"name": "Сұрыптау (Сортировка) өндірістік станциясы", "area": "Пришахтинск", "lat": 49.931, "lon": 73.235, "risk_type": "Су/Топырақ", "risk_level": "Орташа", "description": "Мұнай өнімдерінің қалдықтары мен техникалық сулардың топыраққа сіңу қаупі бар."},
    {"name": "Сұрыптау теміржол торабы", "area": "Пришахтинск", "lat": 49.925, "lon": 73.220, "risk_type": "Шу", "risk_level": "Жоғары", "description": "Жүк вагондарын іріктеу және түнгі уақыттағы пойыз дыбыстары тұрғын үйлерге әсер етеді."},

    # --- Қала орталығы (5 нысан) ---
    {"name": "Гоголь–Ермекова көше қиылысы", "area": "Қала орталығы", "lat": 49.806, "lon": 73.087, "risk_type": "Ауа", "risk_level": "Орташа", "description": "Көлік қозғалысы тығыз қиылыс. Автокөлік пайдаланылған газдарының шоғырлануы (CO, NOx) күн сайын жоғарылайды."},
    {"name": "Қарағанды теміржол вокзалы маңы", "area": "Қала орталығы", "lat": 49.813, "lon": 73.099, "risk_type": "Шу", "risk_level": "Жоғары", "description": "Жүк және жолаушылар пойыздарының жиі қозғалысы күн бойы 60-75 дБ аралығында шу деңгейін тудырады."},
    {"name": "Бұқар Жырау даңғылы (Орталық)", "area": "Қала орталығы", "lat": 49.803, "lon": 73.092, "risk_type": "Ауа", "risk_level": "Орташа", "description": "Автокөліктердің ең тығыз ағыны. Азот диоксиді (NO₂) мен көміртегі оксиді (CO) жиналады."},
    {"name": "Кіші Бұқпа өзенінің арнасы", "area": "Қала орталығы", "lat": 49.795, "lon": 73.075, "risk_type": "Су/Топырақ", "risk_level": "Жоғары", "description": "Өндірістік және тұрмыстық ағынды сулардың бақылаусыз құйылуы, су құрамында сульфаттар мен ауыр металдар бар."},
    {"name": "Қарағанды-Пассажирская теміржол вокзалы", "area": "Қала орталығы", "lat": 49.795, "lon": 73.094, "risk_type": "Шу", "risk_level": "Жоғары", "description": "Пойыздар қозғалысы мен маневрлік жұмыстардан шығатын тұрақты механикалық шу (75 дБ дейін)."},

    # --- Оңтүстік-Шығыс (5 нысан) ---
    {"name": "Өнеркәсіптік аймақ", "area": "Оңтүстік-Шығыс", "lat": 49.781, "lon": 73.151, "risk_type": "Ауа", "risk_level": "Орташа", "description": "Шағын және орта өндіріс кәсіпорындарының түтін шығарғыштары тұрғын үй аймағына жақын орналасқан."},
    {"name": "Қарағанды өзенінің жағалауы", "area": "Оңтүстік-Шығыс", "lat": 49.772, "lon": 73.168, "risk_type": "Су/Топырақ", "risk_level": "Төмен", "description": "Жалпы су сапасы қалыпты, бірақ жекелеген учаскелерде тұрмыстық қалдықтардың кездесуі байқалады."},
    {"name": "Оңтүстік-Шығыс (Республика даңғылы)", "area": "Оңтүстік-Шығыс", "lat": 49.775, "lon": 73.155, "risk_type": "Ауа", "risk_level": "Төмен", "description": "Қаланың басқа аудандарымен салыстырғанда ауа сапасы салыстырмалы түрде таза, жасыл желектер көп."},
    {"name": "Федоровка су қоймасы (жағалауы)", "area": "Оңтүстік-Шығыс", "lat": 49.762, "lon": 73.180, "risk_type": "Су/Топырақ", "risk_level": "Төмен", "description": "Судың санитарлық жағдайы қалыпты, бірақ жазғы шомылу маусымында тұрмыстық қоқыстар көбейеді."},
    {"name": "Ескі аэропорт маңындағы күл-қож үйіндісі", "area": "Оңтүстік-Шығыс", "lat": 49.768, "lon": 73.170, "risk_type": "Су/Топырақ", "risk_level": "Жоғары", "description": "Топырақтың мышьяк, қорғасын сияқты ауыр металдармен ластану қаупі анықталған."},
    {"name": "Шахтерлер даңғылы мен Гоголь көшесінің қиылысы", "area": "Оңтүстік-Шығыс", "lat": 49.790, "lon": 73.115, "risk_type": "Шу", "risk_level": "Орташа", "description": "Күндізгі уақыттағы көлік кептелісі мен дыбыстық сигналдардан туындайтын акустикалық ластану."},

    # --- Өндірістік аймақтар (ТЭЦ) (2 нысан) ---
    {"name": "ЖЭО-3 (ТЭЦ-3) ауданы", "area": "Өндірістік аймақ", "lat": 49.878, "lon": 73.212, "risk_type": "Ауа", "risk_level": "Жоғары", "description": "Көмір жағу арқылы атмосфераға күл, күкірт ангидриді (SO₂) және азот оксидтерін ең көп шығаратын ірі нысан."},
    {"name": "ЖЭО-2 (ТЭЦ-2) маңы", "area": "Өндірістік аймақ", "lat": 49.815, "lon": 72.930, "risk_type": "Ауа", "risk_level": "Жоғары", "description": "Қаланың батыс бөлігіндегі ауа бассейнін ластаушы негізгі көздердин бірі."}
]

df = pd.DataFrame(eco_data)

# Түстер мен белгішелер палитрасы
RISK_COLORS = {"Жоғары": "red", "Орташа": "orange", "Төмен": "green"}
RISK_TYPE_ICONS = {"Ауа": "cloud", "Су/Топырақ": "tint", "Шу": "volume-up"}
RISK_LEVEL_BADGE = {"Жоғары": "#e74c3c", "Орташа": "#f39c12", "Төмен": "#27ae60"}
RISK_COLOR_PLOTLY = {"Жоғары": "#e74c3c", "Орташа": "#f1c40f", "Төмен": "#27ae60"}

# ---------------------------------------------------------------------
# 3. SIDEBAR — БАҚЫЛАУ ПАНЕЛІ
# ---------------------------------------------------------------------
st.sidebar.title("🗺️ Бақылау панелі")
st.sidebar.markdown("---")

selected_risk_types = st.sidebar.multiselect(
    "⚙️ Қауіп түрі:", options=list(df["risk_type"].unique()), default=list(df["risk_type"].unique())
)
selected_risk_levels = st.sidebar.multiselect(
    "🚦 Қауіп деңгейі:", options=["Жоғары", "Орташа", "Төмен"], default=["Жоғары", "Орташа", "Төмен"]
)
selected_areas = st.sidebar.multiselect(
    "📍 Қала ауданы:", options=list(df["area"].unique()), default=list(df["area"].unique())
)

st.sidebar.markdown("---")
show_heatmap = st.sidebar.checkbox("🔥 Жылу картасын қосу", value=True)

# Деректерді сүзгілеу
filtered_df = df[
    df["risk_type"].isin(selected_risk_types)
    & df["risk_level"].isin(selected_risk_levels)
    & df["area"].isin(selected_areas)
]

# ---------------------------------------------------------------------
# 4. НЕГІЗГІ БЕТ — БАСЫ МЕН МЕТРИКАЛАР
# ---------------------------------------------------------------------
st.title("🌍 Қарағанды қаласының экологиялық қауіп-қатерлерінің цифрлық картасы")
st.markdown("Жоба аясында қала бойынша ең маңызды **25 экологиялық нысан** толық зерттеліп, бірыңғай жүйеге біріктірілді.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Жалпы нысандар саны", len(df))
col2.metric("Сүзгідегі нысандар", len(filtered_df))
col3.metric("Жоғары қауіп деңгейі", len(filtered_df[filtered_df["risk_level"] == "Жоғары"]))
col4.metric("Қамтылған аудандар", filtered_df["area"].nunique())

st.markdown("---")

# ---------------------------------------------------------------------
# 5. БІРІНШІ КЕЗЕКТЕ: ИНТЕРАКТИВТІ КАРТА
# ---------------------------------------------------------------------
st.subheader("🗺️ 1. Экологиялық қауіп-қатерлердің цифрлық картасы")

m = folium.Map(location=KARAGANDY_CENTER, zoom_start=START_ZOOM, tiles="CartoDB positron")
markers_layer = folium.FeatureGroup(name="Экологиялық нысандар")

for _, row in filtered_df.iterrows():
    color = RISK_COLORS[row["risk_level"]]
    icon_name = RISK_TYPE_ICONS[row["risk_type"]]
    badge_color = RISK_LEVEL_BADGE[row["risk_level"]]

    popup_html = f"""
    <div style="font-family: Arial, sans-serif; width: 260px;">
        <h4 style="margin-bottom:4px; color:#2c3e50;">{row['name']}</h4>
        <p style="margin:2px 0; color:#7f8c8d;"><b>Аудан:</b> {row['area']}</p>
        <p style="margin:2px 0;"><b>Қауіп түрі:</b> {row['risk_type']}</p>
        <p style="margin:6px 0;">
            <span style="background-color:{badge_color}; color:white; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold;">
                Қауіп деңгейі: {row['risk_level']}
            </span>
        </p>
        <hr style="margin:6px 0;">
        <p style="margin:2px 0; font-size:12px; color:#34495e;">{row['description']}</p>
    </div>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row["name"],
        icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
    ).add_to(markers_layer)

markers_layer.add_to(m)

# Жылу эффектісін қосу
if show_heatmap and not filtered_df.empty:
    weight_map = {"Жоғары": 1.0, "Орташа": 0.6, "Төмен": 0.3}
    heat_points = [[r["lat"], r["lon"], weight_map[r["risk_level"]]] for _, r in filtered_df.iterrows()]
    HeatMap(heat_points, radius=25, blur=20, min_opacity=0.4).add_to(m)

st_folium(m, width=1200, height=600, returned_objects=[])

# Ашылмалы кесте
with st.expander("📋 Сүзілген нысандардың толық деректер кестесі"):
    st.dataframe(
        filtered_df[["name", "area", "risk_type", "risk_level"]].rename(
            columns={"name": "Атауы", "area": "Аудан", "risk_type": "Қауіп түрі", "risk_level": "Қауіп деңгейі"}
        ),
        width="stretch", hide_index=True
    )

st.markdown("---")

# ---------------------------------------------------------------------
# 6. ЕКІНШІ КЕЗЕКТЕ: АНАЛИТИКАЛЫҚ ДИЗЕЙН ЖӘНЕ ДИАГРАММАЛАР
# ---------------------------------------------------------------------
st.subheader("📊 2. Экологиялық статистика және аналитикалық диаграммалар")

if filtered_df.empty:
    st.warning("Сүзгіге сәйкес деректер табылмады.")
else:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Қауіп түрлері бойынша деңгейлердің үлестірілуі**")
        fig_bar = px.histogram(
            filtered_df, x="risk_type", color="risk_level", barmode="group",
            category_orders={"risk_type": ["Ауа", "Су/Топырақ", "Шу"], "risk_level": ["Жоғары", "Орташа", "Төмен"]},
            color_discrete_map=RISK_COLOR_PLOTLY,
            labels={"risk_type": "Қауіп түрі", "risk_level": "Қауіп деңгейі"}
        )
        fig_bar.update_layout(template="plotly_white", yaxis_title="Саны", margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_bar, width="stretch")

    with col_right:
        st.markdown("**Аудандар бойынша қауіпті нысандар үлесі (пайызбен)**")
        area_counts = filtered_df["area"].value_counts().reset_index()
        area_counts.columns = ["area", "count"]
        fig_pie = px.pie(area_counts, names="area", values="count", hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(template="plotly_white", margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_pie, width="stretch")

st.markdown("---")
st.caption("© Республикалық ғылыми жобалар конкурсы. Жоба авторы: Nur Akhmet.")
