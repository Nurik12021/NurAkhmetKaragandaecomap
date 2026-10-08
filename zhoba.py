import streamlit as st
import folium
from folium.plugins import HeatMap
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------------------
# 1. БЕТТІ БАПТАУ
# ---------------------------------------------------------------------
st.set_page_config(
    page_title="Қарағанды | Дәлелденген ластану нысандары",
    layout="wide",
)

MAP_CENTER = [49.90, 73.00]
START_ZOOM = 9

# ---------------------------------------------------------------------
# 2. ДЕРЕКТЕР БАЗАСЫ — 15 нысан, әрқайсысының дереккөзімен
# ---------------------------------------------------------------------
EEAS = {"t": "EEAS/ESA (2023): Air pollution in Karaganda Region as seen from space",
        "u": "https://www.eeas.europa.eu/sites/default/files/documents/2023/KZ-Air-Pollution-from-Space-EN_WEB.pdf"}
BURT = {"t": "Буртовая Е.В., Баранова Е.И. (2024): Анализ экологического состояния г. Караганды (Гео-Сибирь)",
        "u": "https://geosib.sgugit.ru/upload/geosibir/sborniki/2024/tom-4-2/158-163.pdf"}

eco_data = [
    # ------------------------- АУА -------------------------
    {"name": "Qarmet (бұр. ArcelorMittal Temirtau) металлургия комбинатi", "area": "Теміртау",
     "lat": 50.031766, "lon": 72.994863, "risk_type": "Ауа", "risk_level": "Жоғары",
     "description": "2020 ж. Теміртаудағы шығарындының 242 мың тоннасының 89%-ы осы кәсіпорынға тиесілі. 2018 ж. қаңтарда қала үстіне қара қар жауды. ESA спутник деректері бойынша Теміртауда NO₂ деңгейі ұқсас қалалардан 2–3 есе жоғары.",
     "coord_note": "GEM Global Iron and Steel Tracker (нақты координата)",
     "sources": [
         {"t": "Қазақстан Үкіметі (ресми): 2020 ж. шығарындылар, Теміртау — АМТ үлесі 89%",
          "u": "https://primeminister.kz/en/news/2021-zhylgy-mausym-ayynda-utilizaciyalyk-alymga-noldik-molsherleme-engizildi-m-myrzagaliev-155917"},
         EEAS,
         {"t": "Arnika: Polluted air in Temirtau", "u": "https://arnika.org/en/hotspots/kazakhstan/polluted-air-in-temirtau"},
         {"t": "Wikipedia: Qarmet", "u": "https://en.wikipedia.org/wiki/Qarmet"},
         {"t": "GEM: Qarmet steel plant (координата)", "u": "https://www.gem.wiki/Qarmet_steel_plant"},
     ]},
    {"name": "Қарағанды ЖЭО-3 (ТЭЦ-3) және күл үйіндісі", "area": "Қарағанды қаласы",
     "lat": 49.916732, "lon": 73.237172, "risk_type": "Ауа", "risk_level": "Жоғары",
     "description": "Қаланың ең ірі көмірмен жұмыс істейтін электр станциясы. 2021 ж. көмір шаңының рұқсат етілген деңгейінен асқаны үшін 1,7 млн теңге айыппұл салынған. Қар түсірілімі зерттеуі стансадан таралған жанбаған көмір мен күл бөлшектерін анықтады; станса маңы топырағында қорғасын 1,1 ШРК.",
     "coord_note": "GEM Global Coal Plant Tracker (нақты координата)",
     "sources": [
         {"t": "GEM: Karaganda-3 power station", "u": "https://www.gem.wiki/Karaganda-3_power_station"},
         {"t": "Adil'bayeva T.E. et al. (2016), IOP Conf. Ser.: Earth Environ. Sci. — қар түсірілімі, Қарағанды ЖЭО",
          "u": "https://earchive.tpu.ru/handle/11683/35148?locale=en"},
         BURT,
     ]},
    {"name": "Қарағанды ЖЭО-2 (Qarmet ТЭЦ-2)", "area": "Теміртау",
     "lat": 50.04667, "lon": 73.053235, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "Qarmet-тің өз қажетіне арналған көмірмен жұмыс істейтін жылу электр орталығы (≥435 МВт), Global Coal Plant Tracker тізімінде.",
     "coord_note": "GEM Global Coal Plant Tracker (нақты координата)",
     "sources": [{"t": "GEM: Karaganda-2 power station", "u": "https://www.gem.wiki/Karaganda-2_power_station"}]},
    {"name": "Қарағанды ГРЭС-1 (Теміртау)", "area": "Теміртау",
     "lat": 50.089267, "lon": 72.918005, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "1942 жылдан жұмыс істейтін көмір станциясы (84 МВт). 2023 ж. мамырда тұрғындар күл үйіндісінен күл бұлттары таралатынына шағымданды, мәселе бойынша тексеру жарияланды.",
     "coord_note": "GEM Global Coal Plant Tracker (нақты координата)",
     "sources": [{"t": "GEM: Karaganda-1 power station", "u": "https://www.gem.wiki/Karaganda-1_power_station"}]},
    {"name": "Топар ГРЭС-2 (Қарағанды ГРЭС-2)", "area": "Қарағанды облысы",
     "lat": 49.51333, "lon": 72.79861, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "Көмірмен жұмыс істейтін ірі станса (мың МВт-қа жуық). GEM күл үйіндісінен шаң көтерілуі туралы хабарламалар мен бейнематериалдар бар екенін көрсетеді.",
     "coord_note": "GEM Global Coal Plant Tracker (нақты координата)",
     "sources": [{"t": "GEM: Topar power station", "u": "https://www.gem.wiki/Topar_power_station"}]},
    {"name": "Костенко шахтасы", "area": "Қарағанды қаласы",
     "lat": 49.859567, "lon": 73.113928, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "Қарағанды қаласы шегіндегі жерасты көмір шахтасы. EEAS/ESA есебі: жерасты көмір өндіру ашық тәсілден гөрі көбірек метан (CH₄) бөледі; Қарағанды — шахталық ластану басым өңірлердің бірі.",
     "coord_note": "GEM Global Coal Mine Tracker (нақты координата)",
     "sources": [{"t": "GEM: Kostenko Coal Mine", "u": "https://www.gem.wiki/Kostenko_Coal_Mine"}, EEAS]},
    {"name": "Кузембаев шахтасы", "area": "Қарағанды облысы",
     "lat": 49.805879, "lon": 72.966106, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "Жерасты көмір шахтасы, шығыс бөлігі Қарағанды қаласымен шектеседі. Метан шығарындысының секторлық көзі (EEAS/ESA).",
     "coord_note": "GEM Global Coal Mine Tracker (нақты координата)",
     "sources": [{"t": "GEM: Kuzembaev Coal Mine", "u": "https://www.gem.wiki/Kuzembaev_Coal_Mine"}, EEAS]},
    {"name": "Саран шахтасы", "area": "Қарағанды облысы",
     "lat": 49.773061, "lon": 72.895188, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "Қарағанды қаласынан шамамен 12 км қашықтықтағы жерасты шахтасы. Метан шығарындысының секторлық көзі (EEAS/ESA).",
     "coord_note": "GEM Global Coal Mine Tracker (нақты координата)",
     "sources": [{"t": "GEM: Saranskaya Coal Mine", "u": "https://www.gem.wiki/Saranskaya_Coal_Mine"}, EEAS]},
    {"name": "Абай шахтасы", "area": "Қарағанды облысы",
     "lat": 49.68629, "lon": 72.75919, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "2021 ж. қарашада метан жарылысы болған жерасты шахтасы. Метан шығарындысының секторлық көзі (EEAS/ESA).",
     "coord_note": "GEM Global Coal Mine Tracker (нақты координата)",
     "sources": [{"t": "GEM: Abayskaya Coal Mine", "u": "https://www.gem.wiki/Abayskaya_coal_mine"}, EEAS]},
    {"name": "Ленин атындағы шахта (Шахтинск)", "area": "Қарағанды облысы",
     "lat": 49.725506, "lon": 72.521954, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "2006 және 2022 жж. метан жарылыстары болған жерасты шахтасы. Метан шығарындысының секторлық көзі (EEAS/ESA).",
     "coord_note": "GEM Global Coal Mine Tracker (нақты координата)",
     "sources": [{"t": "GEM: Lenin (Kazakhstan) Coal Mine", "u": "https://www.gem.wiki/V._I._Lenin_(Kazakhstan)_Coal_Mine"}, EEAS]},
    {"name": "Шахтинская шахтасы (Шахтинск)", "area": "Қарағанды облысы",
     "lat": 49.764274, "lon": 72.617826, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "Қарағанды көмір бассейнінің жерасты шахтасы. Метан шығарындысының секторлық көзі (EEAS/ESA).",
     "coord_note": "GEM Global Coal Mine Tracker (нақты координата)",
     "sources": [{"t": "GEM: Shakhtinskaya Coal Mine", "u": "https://www.gem.wiki/Shakhtinskaya_Coal_Mine"}, EEAS]},

    # ------------------------- СУ -------------------------
    {"name": "Нұра өзені — Теміртау учаскесі (сынап, «Карбид» зауыты)", "area": "Теміртау",
     "lat": 50.10472, "lon": 72.91889, "risk_type": "Су", "risk_level": "Жоғары",
     "description": "1972 жылдан «Карбид» ацетальдегид зауыты өзенге сынап төкті (1997 ж. жабылды). Зерттеулерде өзен суындағы еритін сынап ШРК-дан 20 есе, Теміртау топырағында 30 есе асқан. Теміртау–Интумак аралығындағы шөгінділерде ~9,4 т сынап бағаланған; жоғарғы 25 км-де орташа 150–240 мг/кг. Дүниежүзілік банк жобасы (2011 ж. аяқталды) ластанған топырақты жойды; Arnika 2013–2014 жж. қалдық ластануды зерттеген.",
     "coord_note": "Анықтамалық нүкте: Самарқан бөгені бөгеті, Нұра өзенінің Теміртау тұсы (Wikipedia). Ластанған учаске осы жерден төменге қарай ~25 км.",
     "sources": [
         {"t": "Wikipedia: Nura (river)", "u": "https://en.wikipedia.org/wiki/Nura_(river)"},
         {"t": "Heaven S. et al. (2000), Univ. of Southampton: Mercury in the river Nura and its floodplain I",
          "u": "https://eprints.soton.ac.uk/74706"},
         {"t": "CORDIS (Еуропалық Комиссия): Mercury contamination, Karaganda region", "u": "https://cordis.europa.eu/project/id/IC15960110"},
         {"t": "Bretton Woods Project: Mercury rising — World Bank and the Nura clean-up",
          "u": "https://www.brettonwoodsproject.org/2007/04/mercury-rising-the-world-bank-and-the-nura-river-clean-up/"},
         {"t": "World Bank (2012): Eliminating Mercury's Invisible Threat in Kazakhstan",
          "u": "https://www.worldbank.org/en/results/2012/04/30/eliminating-mercurys-invisible-threat-in-kazakhstan"},
         {"t": "Arnika: Mercury contamination of Nura river", "u": "https://arnika.org/en/hotspots/kazakhstan/mercury-contamination-of-nura-river"},
     ]},
    {"name": "Сокыр өзені", "area": "Қарағанды облысы",
     "lat": 49.88167, "lon": 72.56778, "risk_type": "Су", "risk_level": "Жоғары",
     "description": "Қазгидромет деректері бойынша 2021–2022 жж. су сапасы «нормаланбайды (>5 класс)»: 2022 ж. жалпы темір 0,358 және марганец 0,187 мг/дм³. Өзен Қарағанды қаласының оңтүстік шетінен өтеді, суы ішуге жарамсыз.",
     "coord_note": "Өзен сағасы (Шерубайнұрамен құятын жер), Wikipedia координатасы.",
     "sources": [BURT, {"t": "Wikipedia: Sokyr", "u": "https://en.wikipedia.org/wiki/Sokyr"}]},
    {"name": "Фёдоров су қоймасы және Кіші Бұқпа өзені (кәріз ағыны)", "area": "Қарағанды қаласы",
     "lat": 49.7583, "lon": 73.0908, "risk_type": "Су", "risk_level": "Орташа",
     "description": "Қаладағы кәріздің 70%-ын өткізетін коллекторда болған апат салдарынан тазартылмаған ағын сулар Кіші Бұқпаға құйылды, ал өзен Фёдоров су қоймасына барады. Санэпидемиологтар өзен суында кәріздің бар екенін зертханалық түрде растады; су қоймасына жетуі туралы нәтижелер бөлек тексерілуде.",
     "coord_note": "Wikipedia (RuWiki): 49°45′30″ с.е., 73°05′27″ ш.б.",
     "sources": [
         BURT,
         {"t": "NewTimes.kz: Қарағандыда кәріздің ағуы бір айдан бері табылмай жатыр (СЭС сынамалары)",
          "u": "https://newtimes.kz/obshchestvo/165178-v-karagande-uzhe-mesyac-ne-mogut-najti-utechku-iz-kanalizacii"},
         {"t": "Zakon.kz: №10 коллектордағы апат, Бұқпа және Фёдоров су қоймасына қауіп",
          "u": "https://www.zakon.kz/obshestvo/6394114-udivitelnoe-yavlenie-v-karagande-na-vodokhranilishche-obosnovalas-staya-lebedey.html"},
         {"t": "Wikipedia: Sokyr (су қоймасының сипаты)", "u": "https://en.wikipedia.org/wiki/Sokyr"},
     ]},
    {"name": "Ертіс–Қарағанды каналы (Нұра өзенімен қиылысу)", "area": "Қарағанды облысы",
     "lat": 50.09056, "lon": 73.37778, "risk_type": "Су", "risk_level": "Төмен",
     "description": "Қарағанды қаласының негізгі ауыз су көзі. Балық сынамаларында қорғасын (0,081 мг/кг дейін) барлық сынамада анықталған; шектен асу көрсетілмеген. Қазгидромет бойынша канал суы 2022 ж. 4-сыныптан 3-класқа жақсарды.",
     "coord_note": "Wikipedia: канал мен Нұраның қиылысу нүктесі.",
     "sources": [
         {"t": "Adilbekov Zh. et al. (2025): Sanitary and environmental safety assessment of fish from reservoirs of Northern and Central Kazakhstan",
          "u": "https://ojs.ksu.edu.kz/index.php/3i/article/view/1278"},
         BURT,
         {"t": "Wikipedia: Nura (river) — канал координатасы", "u": "https://en.wikipedia.org/wiki/Nura_(river)"},
     ]},
]

df = pd.DataFrame(eco_data)
assert len(df) == 15

RISK_COLORS = {"Жоғары": "red", "Орташа": "orange", "Төмен": "green"}
RISK_TYPE_ICONS = {"Ауа": "cloud", "Су": "tint"}
RISK_LEVEL_BADGE = {"Жоғары": "#e74c3c", "Орташа": "#f39c12", "Төмен": "#27ae60"}
RISK_COLOR_PLOTLY = {"Жоғары": "#e74c3c", "Орташа": "#f1c40f", "Төмен": "#27ae60"}

# ---------------------------------------------------------------------
# 3. SIDEBAR
# ---------------------------------------------------------------------
st.sidebar.title("Бақылау панелі")
st.sidebar.markdown("---")

selected_risk_types = st.sidebar.multiselect(
    "Ластану түрі:", options=list(df["risk_type"].unique()), default=list(df["risk_type"].unique())
)
selected_risk_levels = st.sidebar.multiselect(
    "Қауіп деңгейі:", options=["Жоғары", "Орташа", "Төмен"], default=["Жоғары", "Орташа", "Төмен"]
)
selected_areas = st.sidebar.multiselect(
    "Аймақ:", options=list(df["area"].unique()), default=list(df["area"].unique())
)

st.sidebar.markdown("---")
show_heatmap = st.sidebar.checkbox("Жылу картасын қосу", value=False)

filtered_df = df[
    df["risk_type"].isin(selected_risk_types)
    & df["risk_level"].isin(selected_risk_levels)
    & df["area"].isin(selected_areas)
]

# ---------------------------------------------------------------------
# 4. НЕГІЗГІ БЕТ
# ---------------------------------------------------------------------
st.title("Қарағанды қаласы мен өңірінің дәлелденген ластану нысандары")
st.markdown(
    "Әр нысан үшін **дереккөз** (ғылыми мақала, ресми құжат, халықаралық есеп немесе энциклопедия) көрсетілген. "
    "Нысандар Қарағанды қаласында және оның индустриялық өңірінде (Теміртау, Саран, Шахтинск, Топар) орналасқан."
)

c1, c2, c3 = st.columns(3)
c1.metric("Жалпы нысандар", len(df))
c2.metric("Сүзгідегі нысандар", len(filtered_df))
c3.metric("Жоғары қауіп", len(filtered_df[filtered_df["risk_level"] == "Жоғары"]))

with st.expander("Қауіп деңгейі қалай анықталды?"):
    st.markdown(
        "**Қауіп деңгейі**\n"
        "- **Жоғары** — өлшенген шектен асу немесе ресми құжатта басым үлес көрсетілген\n"
        "- **Орташа** — ластау көзі расталған, бірақ сандық асу көрсетілмеген\n"
        "- **Төмен** — іздері анықталған, шектен асу көрсетілмеген\n\n"
        "Қауіп деңгейі — осы өлшемдер бойынша авторлық жіктеу, ресми рейтинг емес."
    )

st.markdown("---")

# ---------------------------------------------------------------------
# 5. КАРТА
# ---------------------------------------------------------------------
st.subheader("1. Ластану нысандарының картасы")

m = folium.Map(location=MAP_CENTER, zoom_start=START_ZOOM, tiles="OpenStreetMap")
markers_layer = folium.FeatureGroup(name="Ластану нысандары")

for _, row in filtered_df.iterrows():
    color = RISK_COLORS[row["risk_level"]]
    icon_name = RISK_TYPE_ICONS[row["risk_type"]]
    badge_color = RISK_LEVEL_BADGE[row["risk_level"]]
    src_html = "".join(
        f'<li><a href="{s["u"]}" target="_blank" rel="noopener">{s["t"]}</a></li>' for s in row["sources"]
    )

    popup_html = f"""
    <div style="font-family: Arial, sans-serif; width: 300px; max-height: 340px; overflow-y:auto;">
        <h4 style="margin-bottom:4px; color:#2c3e50;">{row['name']}</h4>
        <p style="margin:2px 0; color:#7f8c8d;"><b>Аймақ:</b> {row['area']}</p>
        <p style="margin:2px 0;"><b>Түрі:</b> {row['risk_type']}</p>
        <p style="margin:6px 0;">
            <span style="background-color:{badge_color}; color:white; padding:3px 10px; border-radius:12px; font-size:12px; font-weight:bold;">
                Қауіп деңгейі: {row['risk_level']}
            </span>
        </p>
        <hr style="margin:6px 0;">
        <p style="margin:2px 0; font-size:12px; color:#34495e;">{row['description']}</p>
        <p style="margin:6px 0 2px 0; font-size:11px; color:#7f8c8d;"><i>Координата: {row['coord_note']}</i></p>
        <p style="margin:6px 0 2px 0; font-size:12px;"><b>Дереккөздер:</b></p>
        <ul style="margin:0; padding-left:16px; font-size:11px;">{src_html}</ul>
    </div>
    """

    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=340),
        tooltip=row["name"],
        icon=folium.Icon(color=color, icon=icon_name, prefix="fa"),
    ).add_to(markers_layer)

markers_layer.add_to(m)

if show_heatmap and not filtered_df.empty:
    weight_map = {"Жоғары": 1.0, "Орташа": 0.6, "Төмен": 0.3}
    heat_points = [[r["lat"], r["lon"], weight_map[r["risk_level"]]] for _, r in filtered_df.iterrows()]
    HeatMap(heat_points, radius=25, blur=20, min_opacity=0.4).add_to(m)

st_folium(m, width=1200, height=600, returned_objects=[])

# ---------------------------------------------------------------------
# 6. КЕСТЕ ЖӘНЕ ДЕРЕККӨЗДЕР
# ---------------------------------------------------------------------
st.subheader("2. Нысандар және дереккөздер")

if filtered_df.empty:
    st.warning("Сүзгіге сәйкес деректер табылмады.")
else:
    table_df = filtered_df[["name", "area", "risk_type", "risk_level"]].rename(
        columns={"name": "Атауы", "area": "Аймақ", "risk_type": "Түрі",
                 "risk_level": "Қауіп деңгейі"}
    )
    st.dataframe(table_df, use_container_width=True, hide_index=True)

    for _, row in filtered_df.iterrows():
        with st.expander(f"{row['name']} — дереккөздер"):
            st.markdown(f"**Сипаттама:** {row['description']}")
            st.caption(f"Координата: {row['lat']}, {row['lon']} — {row['coord_note']}")
            for s in row["sources"]:
                st.markdown(f"- [{s['t']}]({s['u']})")

st.markdown("---")

# ---------------------------------------------------------------------
# 7. ДИАГРАММАЛАР
# ---------------------------------------------------------------------
st.subheader("3. Статистика")

if not filtered_df.empty:
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("**Ластану түрі бойынша қауіп деңгейлері**")
        fig_bar = px.histogram(
            filtered_df, x="risk_type", color="risk_level", barmode="group",
            category_orders={"risk_type": ["Ауа", "Су"], "risk_level": ["Жоғары", "Орташа", "Төмен"]},
            color_discrete_map=RISK_COLOR_PLOTLY,
            labels={"risk_type": "Ластану түрі", "risk_level": "Қауіп деңгейі"},
        )
        fig_bar.update_layout(template="plotly_white", yaxis_title="Саны", margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown("**Аймақтар бойынша нысандар үлесі**")
        area_counts = filtered_df["area"].value_counts().reset_index()
        area_counts.columns = ["area", "count"]
        fig_pie = px.pie(area_counts, names="area", values="count", hole=0.3,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(template="plotly_white", margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.caption("© Республикалық ғылыми жобалар конкурсы.")