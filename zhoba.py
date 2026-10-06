import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Қарағанды өңірінің ластану нысандары",
    layout="wide",
)

MAP_CENTER = [49.90, 73.00]
START_ZOOM = 9

eeas_source = {
    "t": "EEAS/ESA (2023): Air pollution in Karaganda Region as seen from space",
    "u": "https://www.eeas.europa.eu/sites/default/files/documents/2023/KZ-Air-Pollution-from-Space-EN_WEB.pdf"
}

burt_source = {
    "t": "Буртовая Е.В., Баранова Е.И. (2024): Анализ экологического состояния г. Караганды",
    "u": "https://geosib.sgugit.ru/upload/geosibir/sborniki/2024/tom-4-2/158-163.pdf"
}

eco_data = [
    {
        "name": "Qarmet (ArcelorMittal Temirtau)",
        "area": "Теміртау",
        "lat": 50.031766,
        "lon": 72.994863,
        "risk_type": "Ауа",
        "risk_level": "Жоғары",
        "evidence": "A",
        "description": "2020 ж. Теміртаудағы шығарындының 242 мың тоннасының 89%-ы осы кәсіпорынға тиесілі. ESA спутник деректері бойынша NO2 деңгейі жоғары.",
        "coord_note": "GEM Global Iron and Steel Tracker",
        "sources": [
            {"t": "Қазақстан Үкіметі ресми есебі (2020)", "u": "https://primeminister.kz/en/news/2021-zhylgy-mausym-ayynda-utilizaciyalyk-alymga-noldik-molsherleme-engizildi-m-myrzagaliev-155917"},
            eeas_source,
            {"t": "Arnika: Polluted air in Temirtau", "u": "https://arnika.org/en/hotspots/kazakhstan/polluted-air-in-temirtau"},
            {"t": "GEM: Qarmet steel plant", "u": "https://www.gem.wiki/Qarmet_steel_plant"}
        ]
    },
    {
        "name": "Қарағанды ЖЭО-3 (ТЭЦ-3)",
        "area": "Қарағанды қаласы",
        "lat": 49.916732,
        "lon": 73.237172,
        "risk_type": "Ауа",
        "risk_level": "Жоғары",
        "evidence": "A",
        "description": "Қаладағы ең ірі көмір станциясы. Станция маңындағы топырақта қорғасын деңгейі ШРК-дан асқан.",
        "coord_note": "GEM Global Coal Plant Tracker",
        "sources": [
            {"t": "GEM: Karaganda-3 power station", "u": "https://www.gem.wiki/Karaganda-3_power_station"},
            {"t": "Adil'bayeva T.E. et al. (2016)", "u": "https://earchive.tpu.ru/handle/11683/35148?locale=en"},
            burt_source
        ]
    },
    {
        "name": "Қарағанды ЖЭО-2 (Qarmet ТЭЦ-2)",
        "area": "Теміртау",
        "lat": 50.04667,
        "lon": 73.053235,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "B",
        "description": "Qarmet комбинатының ішкі қажеттіліктеріне арналған көмір ЖЭО.",
        "coord_note": "GEM Global Coal Plant Tracker",
        "sources": [{"t": "GEM: Karaganda-2 power station", "u": "https://www.gem.wiki/Karaganda-2_power_station"}]
    },
    {
        "name": "Қарағанды ГРЭС-1",
        "area": "Теміртау",
        "lat": 50.089267,
        "lon": 72.918005,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "B",
        "description": "1942 жылдан бері жұмыс істейтін көмір станциясы.",
        "coord_note": "GEM Global Coal Plant Tracker",
        "sources": [{"t": "GEM: Karaganda-1 power station", "u": "https://www.gem.wiki/Karaganda-1_power_station"}]
    },
    {
        "name": "Топар ГРЭС-2",
        "area": "Қарағанды облысы",
        "lat": 49.51333,
        "lon": 72.79861,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "B",
        "description": "Көмірмен жұмыс істейтін ірі электр станциясы.",
        "coord_note": "GEM Global Coal Plant Tracker",
        "sources": [{"t": "GEM: Topar power station", "u": "https://www.gem.wiki/Topar_power_station"}]
    },
    {
        "name": "Костенко шахтасы",
        "area": "Қарағанды қаласы",
        "lat": 49.859567,
        "lon": 73.113928,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "C",
        "description": "Жерасты көмір өндіру кешені, метан бөліну көзі.",
        "coord_note": "GEM Global Coal Mine Tracker",
        "sources": [{"t": "GEM: Kostenko Coal Mine", "u": "https://www.gem.wiki/Kostenko_Coal_Mine"}, eeas_source]
    },
    {
        "name": "Күзембаев шахтасы",
        "area": "Қарағанды облысы",
        "lat": 49.805879,
        "lon": 72.966106,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "C",
        "description": "Жерасты көмір шахтасы.",
        "coord_note": "GEM Global Coal Mine Tracker",
        "sources": [{"t": "GEM: Kuzembaev Coal Mine", "u": "https://www.gem.wiki/Kuzembaev_Coal_Mine"}, eeas_source]
    },
    {
        "name": "Саран шахтасы",
        "area": "Қарағанды облысы",
        "lat": 49.773061,
        "lon": 72.895188,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "C",
        "description": "Саран аймағындағы жерасты шахтасы.",
        "coord_note": "GEM Global Coal Mine Tracker",
        "sources": [{"t": "GEM: Saranskaya Coal Mine", "u": "https://www.gem.wiki/Saranskaya_Coal_Mine"}, eeas_source]
    },
    {
        "name": "Абай шахтасы",
        "area": "Қарағанды облысы",
        "lat": 49.68629,
        "lon": 72.75919,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "C",
        "description": "Абай қаласы маңындағы жерасты шахтасы.",
        "coord_note": "GEM Global Coal Mine Tracker",
        "sources": [{"t": "GEM: Abayskaya Coal Mine", "u": "https://www.gem.wiki/Abayskaya_coal_mine"}, eeas_source]
    },
    {
        "name": "Ленин атындағы шахта",
        "area": "Қарағанды облысы",
        "lat": 49.725506,
        "lon": 72.521954,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "C",
        "description": "Шахтинск аймағындағы көмір өндіру нысаны.",
        "coord_note": "GEM Global Coal Mine Tracker",
        "sources": [{"t": "GEM: Lenin Coal Mine", "u": "https://www.gem.wiki/V._I._Lenin_(Kazakhstan)_Coal_Mine"}, eeas_source]
    },
    {
        "name": "Шахтинская шахтасы",
        "area": "Қарағанды облысы",
        "lat": 49.764274, "lon": 72.617826,
        "risk_type": "Ауа",
        "risk_level": "Орташа",
        "evidence": "C",
        "description": "Қарағанды көмір бассейнінің активті шахтасы.",
        "coord_note": "GEM Global Coal Mine Tracker",
        "sources": [{"t": "GEM: Shakhtinskaya Coal Mine", "u": "https://www.gem.wiki/Shakhtinskaya_Coal_Mine"}, eeas_source]
    },
    {
        "name": "Нұра өзені (Теміртау учаскесі)",
        "area": "Теміртау",
        "lat": 50.10472,
        "lon": 72.91889,
        "risk_type": "Су",
        "risk_level": "Жоғары",
        "evidence": "A",
        "description": "Бұрынғы 'Карбид' зауытынан қалған сынаппен ластану аймағы.",
        "coord_note": "Самарқан бөгені бөгеті координатасы",
        "sources": [
            {"t": "Heaven S. et al. (2000)", "u": "https://eprints.soton.ac.uk/74706"},
            {"t": "World Bank (2012) Nura Clean-up Project", "u": "https://www.worldbank.org/en/results/2012/04/30/eliminating-mercurys-invisible-threat-in-kazakhstan"},
            {"t": "Arnika Study", "u": "https://arnika.org/en/hotspots/kazakhstan/mercury-contamination-of-nura-river"}
        ]
    },
    {
        "name": "Соқыр өзені",
        "area": "Қарағанды облысы",
        "lat": 49.88167,
        "lon": 72.56778,
        "risk_type": "Су",
        "risk_level": "Жоғары",
        "evidence": "A",
        "description": "Қазгидромет деректері бойынша су сапасы 5-класқа жатқызылған.",
        "coord_note": "Өзен сағасы",
        "sources": [burt_source, {"t": "Wikipedia: Sokyr", "u": "https://en.wikipedia.org/wiki/Sokyr"}]
    },
    {
        "name": "Фёдоров су қоймасы және Кіші Бұқпа өзені",
        "area": "Қарағанды қаласы",
        "lat": 49.7583,
        "lon": 73.0908,
        "risk_type": "Су",
        "risk_level": "Орташа",
        "evidence": "A",
        "description": "Коммуналдық кәріз желілеріндегі апаттар салдарынан болған ластану.",
        "coord_note": "Фёдоров су қоймасы координатасы",
        "sources": [burt_source]
    },
    {
        "name": "Ертіс–Қарағанды каналы",
        "area": "Қарағанды облысы",
        "lat": 50.09056,
        "lon": 73.37778,
        "risk_type": "Су",
        "risk_level": "Төмен",
        "evidence": "A",
        "description": "Ауыз су көзі. Негізгі көрсеткіштер бойынша су сапасы 3-класқа сәйкес келеді.",
        "coord_note": "Нұра өзенімен қиылысу нүктесі",
        "sources": [
            {"t": "Adilbekov Zh. et al. (2025)", "u": "https://ojs.ksu.edu.kz/index.php/3i/article/view/1278"},
            burt_source
        ]
    }
]

df = pd.DataFrame(eco_data)

RISK_COLORS = {"Жоғары": "red", "Орташа": "orange", "Төмен": "green"}
RISK_TYPE_ICONS = {"Ауа": "info-sign", "Су": "info-sign"}

st.sidebar.header("Параметрлер")

selected_risk_types = st.sidebar.multiselect(
    "Ластану түрі:",
    options=list(df["risk_type"].unique()),
    default=list(df["risk_type"].unique())
)

selected_risk_levels = st.sidebar.multiselect(
    "Қауіп деңгейі:",
    options=["Жоғары", "Орташа", "Төмен"],
    default=["Жоғары", "Орташа", "Төмен"]
)

selected_areas = st.sidebar.multiselect(
    "Аймақ:",
    options=list(df["area"].unique()),
    default=list(df["area"].unique())
)

show_heatmap = st.sidebar.checkbox("Жылу картасы (Heatmap)", value=False)

filtered_df = df[
    df["risk_type"].isin(selected_risk_types) &
    df["risk_level"].isin(selected_risk_levels) &
    df["area"].isin(selected_areas)
]

st.title("Қарағанды өңірінің экологиялық мониторинг картасы")

col1, col2, col3 = st.columns(3)
col1.metric("Барлық нысандар", len(df))
col2.metric("Тандалған нысандар", len(filtered_df))
col3.metric("Жоғары қауіпті", len(filtered_df[filtered_df["risk_level"] == "Жоғары"]))

st.subheader("Геокарта")

m = folium.Map(location=MAP_CENTER, zoom_start=START_ZOOM)

for _, row in filtered_df.iterrows():
    popup_text = f"<b>{row['name']}</b><br>Аймақ: {row['area']}<br>Қауіп: {row['risk_level']}"
    
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=popup_text,
        tooltip=row["name"],
        icon=folium.Icon(color=RISK_COLORS[row["risk_level"]])
    ).add_to(m)

if show_heatmap and not filtered_df.empty:
    weight_map = {"Жоғары": 1.0, "Орташа": 0.6, "Төмен": 0.3}
    heat_points = [[r["lat"], r["lon"], weight_map[r["risk_level"]]] for _, r in filtered_df.iterrows()]
    HeatMap(heat_points, radius=20, blur=15).add_to(m)

st_folium(m, width=1100, height=550, returned_objects=[])

st.subheader("Деректер кестесі")
if not filtered_df.empty:
    st.dataframe(
        filtered_df[["name", "area", "risk_type", "risk_level", "evidence", "description"]],
        use_container_width=True
    )

st.subheader("Статистика")
if not filtered_df.empty:
    c1, c2 = st.columns(2)
    with c1:
        fig1 = px.histogram(filtered_df, x="risk_type", color="risk_level", title="Ластану түрі бойынша")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        fig2 = px.pie(filtered_df, names="area", title="Аймақтар бойынша үлесі")
        st.plotly_chart(fig2, use_container_width=True)