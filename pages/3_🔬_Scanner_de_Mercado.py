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
assets_to_scan = []
for category, assets in ASSET_CATEGORIES.items():
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
            if val > 0.5: return f'background-color: rgba(0, 150, 0, {min(abs(val), 1)}); color: white;'
            elif val < -0.5: return f'background-color: rgba(150, 0, 0, {min(abs(val), 1)}); color: white;'
        return ''

    def style_verdict(verdict):
        color = 'grey'
        if "Very Bullish" in verdict: color = '#006400'
        elif "Bullish" in verdict: color = '#2E8B57'
        elif "Very Bearish" in verdict: color = '#8B0000'
        elif "Bearish" in verdict: color = '#B22222'
        return f'color: {color}; font-weight: bold;'

    for category_name in ASSET_CATEGORIES.keys():
        st.subheader(category_name.replace("---", "").strip())
        
        df_category = df_all[df_all["Categoria"] == category_name]
        
        if not df_category.empty:
            df_display = df_category.sort_values(by="Score Final", ascending=False).reset_index(drop=True)
            
            column_order = ["Ativo", "Score Final", "Veredito", "Economia", "COT", "Sazonalidade"]
            df_display = df_display[[col for col in column_order if col in df_display.columns]]
            
            # CORREÇÃO: Substitui None por 'N/A' antes de formatar.
            df_display['COT'] = df_display['COT'].apply(lambda x: 'N/A' if pd.isna(x) else x)

            formatters = {
                "Score Final": "{:.2f}",
                "Economia": "{:.2f}",
                # CORREÇÃO: Formatação condicional para lidar com números e strings.
                "COT": lambda x: f"{x:.0f}" if isinstance(x, (int, float)) else x
            }
            
            styled_df = df_display.style.apply(
                lambda x: x.map(style_scores), subset=[col for col in df_display.columns if col not in ['Ativo', 'Veredito']]
            ).apply(
                lambda x: x.map(style_verdict), subset=['Veredito']
            ).format(formatters)
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

    # --- NOVA SECÇÃO: LEGENDA EXPLICATIVA ---
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

