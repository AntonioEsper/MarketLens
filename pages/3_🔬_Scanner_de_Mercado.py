# marketlens/pages/3_🔬_Scanner_de_Mercado.py

import streamlit as st
import pandas as pd
from view_utils import setup_sidebar
from utils.config import ASSET_CATEGORIES, cot_market_map
from utils.scoring_engine import calculate_synapse_score

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Scanner de Mercado")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("🔬 Scanner de Mercado (Synapse Score)")
st.caption("Uma visão geral do mercado baseada na confluência de múltiplos fatores.")
st.markdown("---")

# --- LÓGICA DO SCANNER ---
scanner_categories = ASSET_CATEGORIES.copy()
scanner_categories.pop("--- US Stocks (MAG7) ---", None)

assets_to_scan = []
for category, assets in scanner_categories.items():
    for asset in assets:
        assets_to_scan.append({"asset": asset, "category": category})

progress_bar = st.progress(0, text="A iniciar a análise...")
results = []
total_assets = len(assets_to_scan)

for i, item in enumerate(assets_to_scan):
    asset = item["asset"]
    category = item["category"]
    
    progress_text = f"A analisar {asset} ({i+1}/{total_assets})..."
    progress_bar.progress((i + 1) / total_assets, text=progress_text)
    
    final_score, verdict, individual_scores = calculate_synapse_score(asset)
    
    row = {"Ativo": asset, "Score Final": final_score, "Veredito": verdict, "Categoria": category}
    row.update(individual_scores)
    results.append(row)

progress_bar.empty()

# --- EXIBIÇÃO DA TABELA DE RESULTADOS ---
if results:
    df_all = pd.DataFrame(results)
    
    def style_scores(val):
        if isinstance(val, (int, float)):
            if val > 0.5: return 'background-color: rgba(0, 150, 0, 0.6); color: white;'
            elif val < -0.5: return 'background-color: rgba(150, 0, 0, 0.6); color: white;'
        return ''

    def style_verdict(verdict):
        color = 'grey'
        if "Very Bullish" in verdict: color = '#00FF00'
        elif "Bullish" in verdict: color = '#2E8B57'
        elif "Very Bearish" in verdict: color = '#FF0000'
        elif "Bearish" in verdict: color = '#B22222'
        return f'color: {color}; font-weight: bold;'

    st.markdown("""
    <style>
        .styled-table { width: 100%; border-collapse: collapse; }
        .styled-table thead th { text-align: left; padding: 8px; border-bottom: 1px solid #3d3d3d; }
        .styled-table tbody td { padding: 8px; }
    </style>
    """, unsafe_allow_html=True)

    for category_name in scanner_categories.keys():
        st.subheader(category_name.replace("---", "").strip())
        
        df_category = df_all[df_all["Categoria"] == category_name]
        
        if not df_category.empty:
            df_display = df_category.sort_values(by="Score Final", ascending=False)
            
            column_order = ["Ativo", "Score Final", "Veredito", "Economia", "COT", "Sazonalidade"]
            df_display = df_display[[col for col in column_order if col in df_display.columns]]
            
            formatters = {
                "Score Final": "{:.2f}", "Economia": "{:.2f}",
                "COT": lambda x: "N/A" if pd.isna(x) else f"{x:.0f}",
                "Sazonalidade": "{:.0f}"
            }
            
            styled_df = df_display.style.apply(
                lambda x: x.map(style_scores), subset=['Score Final', 'Economia', 'COT', 'Sazonalidade']
            ).apply(
                lambda x: x.map(style_verdict), subset=['Veredito']
            ).format(formatters).hide(axis="index")
            
            table_html = styled_df.set_table_attributes('class="styled-table"').to_html()
            st.markdown(table_html, unsafe_allow_html=True)

    st.markdown("---")
    with st.expander("ℹ️ Como interpretar o Synapse Score? Clique para expandir"):
        st.markdown("""
        O **Synapse Score** é uma métrica proprietária desenhada para agregar múltiplos fatores de análise num único indicador de viés direcional.

        #### Componentes do Score:
        * **Economia:** Analisa o *momentum* dos principais indicadores económicos (PIB, Inflação, etc.) de um país em relação à sua média histórica. Para pares de moedas, o score representa a **diferença** entre a força económica das duas moedas.
        * **COT (Commitment of Traders):** Mede o posicionamento líquido dos grandes especuladores (dinheiro institucional). Um score positivo indica um otimismo institucional acima da média recente. Um valor "N/A" significa que o ativo não possui dados de posicionamento.
        * **Sazonalidade:** Avalia a performance média histórica do ativo para o mês atual. Um score positivo indica que o mês atual é historicamente favorável para o ativo.

        #### Tabela e Cores:
        * As células são coloridas com base na força do indicador: **verde** para positivo (bullish) e **vermelho** para negativo (bearish). A intensidade da cor reflete a magnitude do score.
        * **Score Final:** É a soma dos scores individuais. Um valor fortemente positivo ou negativo indica uma maior confluência de fatores.
        * **Veredito:** Traduz o Score Final numa classificação qualitativa, de **Very Bearish** a **Very Bullish**.
        """)
else:
    st.error("Não foi possível calcular os scores. Verifique os motores de dados.")

# --- FIM DO FICHEIRO ---