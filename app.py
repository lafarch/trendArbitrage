import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import json
from main import TrendArbitrageEngine

# 1. Configuración de página
st.set_page_config(
    page_title="TrendArbitrage", layout="wide", initial_sidebar_state="collapsed"
)

# 2. Inyección de CSS (Tipografía, Alineación y Ocultar elementos de Streamlit)
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

        /* FUENTE GLOBAL */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: #1E293B;
        }
        
        /* OCULTAR ELEMENTOS DE STREAMLIT (Deploy btn, Menu, Footer) */
        .stDeployButton {display:none;}
        [data-testid="stToolbar"] {visibility: hidden !important;}
        footer {visibility: hidden;}
        #MainMenu {visibility: hidden;}

        /* ESTILO DEL INPUT */
        .stTextInput>div>div>input {
            border-radius: 6px;
            border: 1px solid #E2E8F0;
            padding: 10px;
            font-size: 16px;
        }

        /* ESTILO DEL BOTÓN ANALYZE */
        .stButton>button {
            width: 100%;
            border-radius: 6px;
            height: 48px; /* Altura forzada para igualar al input */
            background-color: #0F172A; 
            color: white;
            font-weight: 600;
            letter-spacing: 0.5px;
            border: none;
            transition: all 0.2s ease;
        }
        .stButton>button:hover {
            background-color: #334155;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transform: translateY(-1px);
        }
        
        /* ESTILO DE TABLAS */
        [data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0;
            border-radius: 8px;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# --- CABECERA DE MARCA ---

# Título con diseño HTML personalizado
st.markdown(
    """
    <div style='margin-bottom: 30px;'>
        <h1 style='
            font-family: "Inter", sans-serif; 
            font-weight: 800; 
            font-size: 3.5rem; 
            color: #0F172A; 
            letter-spacing: -1.5px; 
            margin-bottom: 0;
            line-height: 1.1;
        '>
            Trend<span style='color: #64748B;'>Arbitrage</span><span style='color: #3B82F6; font-size: 1rem; vertical-align: super;'>BETA</span>
        </h1>
        <p style='
            color: #64748B; 
            font-size: 1.1rem; 
            font-weight: 400; 
            margin-top: 10px;
        '>
            Advanced Intelligence Engine for Dropshipping Niche Discovery
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

# --- SECCIÓN DE CONTROL ---

# Contenedor con fondo sutil para agrupar los controles
with st.container():
    # Alineación vertical "bottom" para que el botón y el input queden perfectos
    col_search, col_btn = st.columns([5, 1], vertical_alignment="bottom")

    with col_search:
        user_keywords = st.text_input(
            "Target Keywords",
            placeholder="Type keywords separated by commas (e.g., yoga mat, mechanical keyboard...)",
            label_visibility="visible",  # Visible pero discreto gracias al diseño
        )

    with col_btn:
        run_btn = st.button("ANALYZE MARKET")

    # Selector de tiendas limpio
    selected_stores = st.multiselect(
        "Data Sources",
        ["Amazon", "eBay", "Walmart", "AliExpress"],
        default=["Amazon"],
        help="Select marketplaces to scan for competition supply.",
    )

st.markdown("---")

# --- LÓGICA PRINCIPAL ---

if run_btn and user_keywords:
    with st.spinner(f'Processing intelligence from {", ".join(selected_stores)}...'):
        try:
            engine = TrendArbitrageEngine()
            keywords_list = [k.strip() for k in user_keywords.split(",") if k.strip()]
            platforms_lower = [store.lower() for store in selected_stores]

            if keywords_list:
                df_results = engine.run_pipeline(
                    keywords=keywords_list,
                    use_trending=False,
                    temporal_analysis=False,
                    platforms=platforms_lower,
                )

                if not df_results.empty:
                    st.session_state["data"] = df_results
                else:
                    st.error("No data found. Please check API limits.")
            else:
                st.warning("Please enter at least one keyword.")

        except Exception as e:
            st.error(f"System Error: {e}")

elif run_btn and not user_keywords:
    st.warning("Please enter keywords to begin analysis.")


# --- VISUALIZACIÓN DE RESULTADOS ---

if "data" in st.session_state:
    df = st.session_state["data"]

    # 1. KPIs
    best_product = df.iloc[0]

    st.markdown(
        "<h3 style='margin-bottom: 20px;'>Executive Summary</h3>",
        unsafe_allow_html=True,
    )

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Winning Product", best_product["keyword"])
    with kpi2:
        st.metric(
            "Opportunity Score",
            f"{best_product['opportunity_score']:.1f}/100",
            delta=f"{best_product['momentum_multiplier']:.2f}x Momentum",
        )
    with kpi3:
        st.metric(
            "Qualified Demand", f"{best_product['demand_signal']:,.0f}", "Vol/Month"
        )
    with kpi4:
        st.metric(
            "Total Supply",
            f"{best_product['total_supply']:,}",
            best_product["competition_level"],
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. Tabla
    st.markdown(
        "<h3 style='margin-bottom: 15px;'>Market Opportunities</h3>",
        unsafe_allow_html=True,
    )

    display_df = df[
        [
            "rank",
            "keyword",
            "opportunity_score",
            "demand_signal",
            "total_supply",
            "competition_level",
            "base_ratio",
            "verdict",
        ]
    ].copy()
    display_df.columns = [
        "Rank",
        "Keyword",
        "Score",
        "Demand (Est)",
        "Supply (Total)",
        "Competition",
        "Ratio",
        "Verdict",
    ]

    st.dataframe(
        display_df.style.background_gradient(subset=["Score"], cmap="Greys"),
        use_container_width=True,
        hide_index=True,
    )

    # 3. Gráficos
    st.markdown(
        "<br><h3 style='margin-bottom: 15px;'>Demand vs. Supply Matrix</h3>",
        unsafe_allow_html=True,
    )

    fig_scatter = px.scatter(
        df,
        x="supply_pressure",
        y="demand_signal",
        size="opportunity_score",
        color="competition_level",
        hover_name="keyword",
        log_x=False,
        template="plotly_white",
        labels={
            "supply_pressure": "Supply Pressure (Logarithmic)",
            "demand_signal": "Qualified Demand Signal",
        },
    )
    fig_scatter.update_traces(
        marker=dict(line=dict(width=1, color="DarkSlateGrey"), opacity=0.8)
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)

    # 4. Detalle
    st.markdown("---")
    st.markdown(
        "<h3 style='margin-bottom: 15px;'>Deep Dive Analysis</h3>",
        unsafe_allow_html=True,
    )

    selected_keyword = st.selectbox(
        "Select product to inspect:", df["keyword"].tolist()
    )

    safe_filename = (
        selected_keyword.replace(" ", "_").replace("/", "-").lower() + ".json"
    )
    json_path = os.path.join("data", "frontend", safe_filename)

    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            sim_data = json.load(f)

        timeline = sim_data.get("timeline", [])
        if timeline:
            dates = [item["date"] for item in timeline]
            trend_vals = [item["trend_index"] for item in timeline]
            sales_est = [item["estimated_sales"] for item in timeline]

            fig_detail = go.Figure()

            fig_detail.add_trace(
                go.Scatter(
                    x=dates,
                    y=trend_vals,
                    name="Search Interest Index",
                    line=dict(color="#0F172A", width=3),
                    fill="tozeroy",
                    fillcolor="rgba(15, 23, 42, 0.1)",
                )
            )

            fig_detail.add_trace(
                go.Scatter(
                    x=dates,
                    y=sales_est,
                    name="Proj. Monthly Sales",
                    line=dict(color="#3B82F6", width=2, dash="dash"),
                    yaxis="y2",
                )
            )

            fig_detail.update_layout(
                template="plotly_white",
                title=dict(
                    text=f"Trend Velocity: {selected_keyword.title()}",
                    font=dict(size=20),
                ),
                yaxis=dict(title="Interest Index (0-100)", showgrid=False),
                yaxis2=dict(
                    title="Sales Projection",
                    overlaying="y",
                    side="right",
                    showgrid=True,
                    gridcolor="#F1F5F9",
                ),
                hovermode="x unified",
                legend=dict(orientation="h", y=1.1),
                height=450,
            )

            st.plotly_chart(fig_detail, use_container_width=True)

            st.markdown(f"**Analyst Verdict for {selected_keyword.title()}:**")
            verdict_text = df[df["keyword"] == selected_keyword]["verdict"].values[0]
            st.info(verdict_text, icon="📋")
