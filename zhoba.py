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
    page_title="Қарағанды | Экологиялық қауіп-қатерлер картасы",
    page_icon="🌍",
    layout="wide",
)

KARAGANDY_CENTER = [49.90, 73.00]
START_ZOOM = 9

# ---------------------------------------------------------------------
# 2. ДЕРЕКТЕР БАЗАСЫ — 15 нысан (5 ауа, 5 су, 5 шу)
# Барлық мәндер: Қазгидромет РМК филиалы (Қарағанды және Ұлытау облыстары),
# "Қоршаған ортаның жай-күйі туралы ақпараттық бюллетень", 2026 жылғы ақпан.
# ---------------------------------------------------------------------
SRC = "Қазгидромет, Қарағанды және Ұлытау обл. бюллетені, 2026 ақпан (kazhydromet.kz)"
APPROX = "Координата шамамен (елді мекен/нысан бойынша). Дәл створ координатасын Қазгидромет паспортынан алыңыз."
NO_NOISE = "Ресми шу өлшемі жарияланбаған. Өз өлшемдеріңізді сол жақ панельге енгізіңіз."

# ---- АУА: деңгей бюллетеньнің өз шкаласы бойынша (СИ, НП) ----
air = [
    {"name": "Қарағанды, ҚБП №8 (Зелинский к-сі, 23, Пришахтинск)", "area": "Қарағанды қ.",
     "lat": 49.8987, "lon": 73.0820, "risk_type": "Ауа", "risk_level": "Жоғары",
     "description": "PM2.5: бір реттік макс. 24,4 ШРК, орташа тәуліктік 11,3 ШРК; "
                    "ақпанда 50 жоғары ластану жағдайы. Қала бойынша СИ=24,4, НП=100% (өте жоғары).",
     "source": SRC, "coord_note": "Пост мекенжайы бойынша (Google Places)."},
    {"name": "Теміртау, ҚБП №2 (Фурманов к-сі, 5)", "area": "Теміртау",
     "lat": 50.0522, "lon": 72.9932, "risk_type": "Ауа", "risk_level": "Орташа",
     "description": "Күкіртті сутек: СИ=4,2 (жоғарылаған деңгей), 36 жағдайда ШРК асты. "
                    "Теміртау бойынша жалпы деңгей жоғары (фенол, НП=32%, №4 пост).",
     "source": SRC, "coord_note": "Пост мекенжайы бойынша (Google Places)."},
    {"name": "Абай қаласы, ҚБП (Абай к-сі, 26)", "area": "Абай",
     "lat": 49.6335, "lon": 72.8547, "risk_type": "Ауа", "risk_level": "Жоғары",
     "description": "Азот диоксиді: орташа тәуліктік 5,61 ШРК, бір реттік 1,48 ШРК; "
                    "1751 жағдайда ШРК асты; НП=87% (өте жоғары).",
     "source": SRC, "coord_note": "Пост мекенжайы бойынша (Google Places)."},
    {"name": "Сарань, ҚБП (Саранская к-сі, 28а, орталық аурухана)", "area": "Сарань",
     "lat": 49.8036, "lon": 72.8247, "risk_type": "Ауа", "risk_level": "Төмен",
     "description": "Көміртек оксиді: СИ=0,6, НП=0% (төмен деңгей). Тек CO өлшенеді. "
                    "Салыстыру үшін таза нүкте ретінде алынған.",
     "source": SRC, "coord_note": "Пост мекенжайы бойынша (Google Places)."},
    {"name": "Сортировка (жылжымалы лаборатория, Бородин/Серов қиылысы)", "area": "Қарағанды қ.",
     "lat": 49.9667, "lon": 73.2212, "risk_type": "Ауа", "risk_level": "Төмен",
     "description": "Эпизодтік өлшем: барлық заттар нормада. Тұрақты пост емес, бір реттік өлшем.",
     "source": SRC, "coord_note": APPROX},
]

# ---- СУ: деңгей Бірыңғай жіктеме класы бойынша (5-6 жоғары, 4 орташа, ≤3 төмен) ----
def water_level(cls):
    return "Жоғары" if cls >= 5 else ("Орташа" if cls == 4 else "Төмен")

water_raw = [
    ("Сокыр өзені, сағасы (Қаражар ауылы маңы)", "Нұра ауданы", 49.8670, 72.5776, 6,
     "6 класс (жоғары ластанған): аммоний-ион 18,1 мг/дм³, нитрит 10,37, фосфат 5,21, хлорид 419. "
     "Ақпанда 2 жоғары ластану жағдайы."),
    ("Шерубайнұра өзені, сағасы (Асыл ауылынан 2 км төмен)", "Абай ауданы", 49.8861, 72.5753, 6,
     "6 класс (жоғары ластанған): аммоний-ион 18,0 мг/дм³, нитрит 9,586, фосфат 5,009. "
     "Ақпанда 4 жоғары ластану жағдайы."),
    ("Нұра өзені, Теміртау (Qarmet пен ТЭМК бірлескен ағынынан 1 км төмен)", "Теміртау", 50.0518, 73.0145, 5,
     "5 класс (өте ластанған): фосфат 1,559 мг/дм³, фондық кластан асады."),
    ("Нұра өзені, Теміртау (бірлескен ағыннан 1 км жоғары)", "Теміртау", 50.0550, 72.9650, 3,
     "3 класс (орташа ластанған): минерализация 1280 мг/дм³, сульфат 315 мг/дм³. "
     "Ағыннан төмен 5 класқа дейін нашарлайды."),
    ("Қ. Сәтбаев атындағы канал (Қарағанды қ., 156-көпір, Петровка ауылына)", "Қарағанды қ.", 50.0991, 73.5082, 4,
     "4 класс (ластанған): қалқыма заттар 13,0 мг/дм³, фондық кластан асады."),
]
water = [
    {"name": n, "area": a, "lat": la, "lon": lo, "risk_type": "Су",
     "risk_level": water_level(c), "description": d, "source": SRC, "coord_note": APPROX}
    for (n, a, la, lo, c, d) in water_raw
]

# ---- ШУ: ресми өлшем жоқ, деңгей пайдаланушы енгізген дБА бойынша есептеледі ----
noise_raw = [
    ("Қарағанды-Пассажирская теміржол вокзалы (Ермеков к-сі, 27)", "Қарағанды қ.", 49.7926, 73.0937,
     "Жолаушылар және жүк пойыздарының қозғалысы. " + NO_NOISE),
    ("Қарағанды-Сұрыптау станциясы (20+ жол, вагон сұрыптау)", "Қарағанды қ.", 49.9667, 73.2212,
     "Жүк вагондарын сұрыптау және маневр жұмыстары. " + NO_NOISE),
    ("Бұқар Жырау даңғылы мен Абай к-сінің қиылысы (ҚБП №3 маңы)", "Қарағанды қ.", 49.8040, 73.0900,
     "Қала орталығындағы тығыз көлік ағыны. " + NO_NOISE),
    ("Ермеков к-сі, 116 (ҚБП №7 маңы)", "Қарағанды қ.", 49.7820, 73.0682,
     "Көлік қозғалысы. " + NO_NOISE),
    ("Сары-Арқа халықаралық әуежайы", "Қарағанды қ.", 49.6708, 73.3344,
     "Әуе кемелерінің ұшуы мен қонуы. " + NO_NOISE),
]

NORM_DAY, NORM_NIGHT = 55, 45  # дБА, тұрғын аумақ. Нормативті санитарлық ережеден тексеріңіз.

# ---------------------------------------------------------------------
# 3. SIDEBAR — ШУ ӨЛШЕМДЕРІН ЕНГІЗУ
# ---------------------------------------------------------------------
st.sidebar.title("🗺️ Бақылау панелі")

with st.sidebar.expander("🔊 Шу өлшемдерін енгізу (дБА)", expanded=False):
    st.caption(f"Норма: күндіз {NORM_DAY} дБА, түнде {NORM_NIGHT} дБА. "
               "Өлшемді енгізгенде нысанның деңгейі автоматты есептеледі.")
    noise_base = pd.DataFrame({
        "Нысан": [r[0] for r in noise_raw],
        "Күндіз": [None] * len(noise_raw),
        "Түнде": [None] * len(noise_raw),
    })
    noise_edit = st.data_editor(
        noise_base, hide_index=True, disabled=["Нысан"], key="noise_editor",
        column_config={
            "Күндіз": st.column_config.NumberColumn("Күндіз, дБА", min_value=20, max_value=140),
            "Түнде": st.column_config.NumberColumn("Түнде, дБА", min_value=20, max_value=140),
        },
    )

def noise_level(day, night):
    excess = []
    if pd.notna(day):
        excess.append(day - NORM_DAY)
    if pd.notna(night):
        excess.append(night - NORM_NIGHT)
    if not excess:
        return "Өлшеу жоқ"
    m = max(excess)
    return "Жоғары" if m >= 10 else ("Орташа" if m > 0 else "Төмен")

noise = []
for i, (n, a, la, lo, d) in enumerate(noise_raw):
    day, night = noise_edit.loc[i, "Күндіз"], noise_edit.loc[i, "Түнде"]
    lvl = noise_level(day, night)
    extra = ""
    if lvl != "Өлшеу жоқ":
        extra = f" Өлшем: күндіз {day if pd.notna(day) else '—'}, түнде {night if pd.notna(night) else '—'} дБА."
    noise.append({
        "name": n, "area": a, "lat": la, "lon": lo, "risk_type": "Шу", "risk_level": lvl,
        "description": d + extra,
        "source": "Нысан орны: Google Places. Шу деңгейі: пайдаланушы өлшемі.",
        "coord_note": "Координата нысан мекенжайы бойынша.",
    })

df = pd.DataFrame(air + water + noise)

LEVELS = ["Жоғары", "Орташа", "Төмен", "Өлшеу жоқ"]
RISK_COLORS = {"Жоғары": "red", "Орташа": "orange", "Төмен": "green", "Өлшеу жоқ": "gray"}
RISK_TYPE_ICONS = {"Ауа": "cloud", "Су": "tint", "Шу": "volume-up"}
RISK_LEVEL_BADGE = {"Жоғары": "#e74c3c", "Орташа": "#f39c12", "Төмен": "#27ae60", "Өлшеу жоқ": "#7f8c8d"}
RISK_COLOR_PLOTLY = {"Жоғары": "#e74c3c", "Орташа": "#f1c40f", "Төмен": "#27ae60", "Өлшеу жоқ": "#95a5a6"}

st.sidebar.markdown("---")
selected_risk_types = st.sidebar.multiselect(
    "⚙️ Қауіп түрі:", options=["Ауа", "Су", "Шу"], default=["Ауа", "Су", "Шу"])
selected_risk_levels = st.sidebar.multiselect(
    "🚦 Қауіп деңгейі:", options=LEVELS, default=LEVELS)
selected_areas = st.sidebar.multiselect(
    "📍 Қала / аудан:", options=sorted(df["area"].unique()), default=list(df["area"].unique()))
show_heatmap = st.sidebar.checkbox("🔥 Жылу картасын қосу", value=False)

filtered_df = df[
    df["risk_type"].isin(selected_risk_types)
    & df["risk_level"].isin(selected_risk_levels)
    & df["area"].isin(selected_areas)
]

# ---------------------------------------------------------------------
# 4. НЕГІЗГІ БЕТ
# ---------------------------------------------------------------------
st.title("🌍 Қарағанды өңірінің экологиялық қауіп-қатерлерінің цифрлық картасы")
st.markdown(
    "Картада **15 нысан** бар: 5 ауа, 5 су, 5 шу. Ауа мен су нысандарының деңгейі "
    "**Қазгидромет РМК ресми бюллетенінің** деректеріне негізделген (2026 жылғы ақпан). "
    "Шу бойынша ресми жариялы өлшем жоқ, сондықтан деңгей тек сіз енгізген өлшем бойынша есептеледі."
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Жалпы нысандар", len(df))
c2.metric("Сүзгідегі нысандар", len(filtered_df))
c3.metric("Жоғары қауіп", int((filtered_df["risk_level"] == "Жоғары").sum()))
c4.metric("Өлшеу жоқ (шу)", int((filtered_df["risk_level"] == "Өлшеу жоқ").sum()))

st.markdown("---")

# ---------------------------------------------------------------------
# 5. КАРТА
# ---------------------------------------------------------------------
st.subheader("🗺️ 1. Экологиялық қауіп-қатерлердің картасы")

m = folium.Map(location=KARAGANDY_CENTER, zoom_start=START_ZOOM, tiles="OpenStreetMap")

for _, row in filtered_df.iterrows():
    badge = RISK_LEVEL_BADGE[row["risk_level"]]
    popup_html = f"""
    <div style="font-family: Arial, sans-serif; width: 280px;">
        <h4 style="margin-bottom:4px; color:#2c3e50;">{row['name']}</h4>
        <p style="margin:2px 0; color:#7f8c8d;"><b>Аудан:</b> {row['area']}</p>
        <p style="margin:2px 0;"><b>Түрі:</b> {row['risk_type']}</p>
        <p style="margin:6px 0;"><span style="background-color:{badge}; color:white; padding:3px 10px;
            border-radius:12px; font-size:12px; font-weight:bold;">Деңгей: {row['risk_level']}</span></p>
        <hr style="margin:6px 0;">
        <p style="margin:2px 0; font-size:12px; color:#34495e;">{row['description']}</p>
        <p style="margin:6px 0 2px 0; font-size:11px; color:#7f8c8d;"><b>Дереккөз:</b> {row['source']}</p>
        <p style="margin:2px 0; font-size:11px; color:#95a5a6;">{row['coord_note']}</p>
    </div>
    """
    folium.Marker(
        location=[row["lat"], row["lon"]],
        popup=folium.Popup(popup_html, max_width=320),
        tooltip=row["name"],
        icon=folium.Icon(color=RISK_COLORS[row["risk_level"]], icon=RISK_TYPE_ICONS[row["risk_type"]], prefix="fa"),
    ).add_to(m)

if show_heatmap:
    weight = {"Жоғары": 1.0, "Орташа": 0.6, "Төмен": 0.3}
    pts = [[r["lat"], r["lon"], weight[r["risk_level"]]]
           for _, r in filtered_df.iterrows() if r["risk_level"] in weight]
    if pts:
        HeatMap(pts, radius=25, blur=20, min_opacity=0.4).add_to(m)

st_folium(m, width=1200, height=600, returned_objects=[])

with st.expander("📋 Толық деректер кестесі"):
    st.dataframe(
        filtered_df[["name", "area", "risk_type", "risk_level", "description", "source"]].rename(
            columns={"name": "Атауы", "area": "Аудан", "risk_type": "Түрі", "risk_level": "Деңгей",
                     "description": "Көрсеткіштер", "source": "Дереккөз"}),
        use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------------
# 6. ДИАГРАММАЛАР
# ---------------------------------------------------------------------
st.subheader("📊 2. Статистика")

if filtered_df.empty:
    st.warning("Сүзгіге сәйкес деректер табылмады.")
else:
    left, right = st.columns(2)
    with left:
        st.markdown("**Түрлер бойынша деңгейлердің үлестірілуі**")
        fig_bar = px.histogram(
            filtered_df, x="risk_type", color="risk_level", barmode="group",
            category_orders={"risk_type": ["Ауа", "Су", "Шу"], "risk_level": LEVELS},
            color_discrete_map=RISK_COLOR_PLOTLY,
            labels={"risk_type": "Түрі", "risk_level": "Деңгей"})
        fig_bar.update_layout(template="plotly_white", yaxis_title="Саны", margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_bar, use_container_width=True)
    with right:
        st.markdown("**Қала / аудандар бойынша нысандар үлесі**")
        ac = filtered_df["area"].value_counts().reset_index()
        ac.columns = ["area", "count"]
        fig_pie = px.pie(ac, names="area", values="count", hole=0.3,
                         color_discrete_sequence=px.colors.sequential.RdBu)
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(template="plotly_white", margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")
st.caption(
    "Дереккөз: РМК «Қазгидромет» филиалы (Қарағанды және Ұлытау облыстары), ақпараттық бюллетень, "
    "2026 жылғы ақпан. Деректер бір айға ғана жатады. Қорғау алдында соңғы бюллетеньмен жаңартыңыз."
)