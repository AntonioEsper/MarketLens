# marketlens/pages/3_🔬_Scanner_de_Mercado.py

import streamlit as st
import pandas as pd
from view_utils import setup_sidebar
# CORREÇÃO: Importa também o cot_market_map para a verificação
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

# Cria uma lista de todos os ativos a serem processados, mantendo a sua categoria
assets_to_scan = []
for category, assets in ASSET_CATEGORIES.items():
    for asset in assets:
        assets_to_scan.append({"asset": asset, "category": category})

# Barra de progresso única para uma melhor experiência do utilizador
progress_bar = st.progress(0, text="A iniciar a análise...")

results = []
total_assets = len(assets_to_scan)

# Itera sobre cada ativo para calcular o seu score
for i, item in enumerate(assets_to_scan):
    asset = item["asset"]
    category = item["category"]
    
    progress_text = f"A analisar {asset} ({i+1}/{total_assets})..."
    progress_bar.progress((i + 1) / total_assets, text=progress_text)
    
    final_score, verdict, individual_scores = calculate_synapse_score(asset)
    
    # Converte o score do COT para "N/A" se for o caso
    if individual_scores.get('COT') == 0 and asset not in cot_market_map:
        individual_scores['COT'] = "N/A"

    row = {"Ativo": asset, "Score Final": final_score, "Veredito": verdict, "Categoria": category}
    row.update(individual_scores)
    results.append(row)

progress_bar.empty()

# --- EXIBIÇÃO DA TABELA DE RESULTADOS ---

if results:
    df_all = pd.DataFrame(results)
    
    # --- Lógica de Estilização (Heatmap) ---
    def style_scores(val):
        """Aplica cores às células de score."""
        if isinstance(val, (int, float)):
            if val > 0.5: return f'background-color: rgba(0, 150, 0, {min(abs(val), 1)}); color: white;'
            elif val < -0.5: return f'background-color: rgba(150, 0, 0, {min(abs(val), 1)}); color: white;'
        return ''

    def style_verdict(verdict):
        """Aplica cores à célula de veredito."""
        color = 'grey'
        if "Very Bullish" in verdict: color = '#006400'
        elif "Bullish" in verdict: color = '#2E8B57'
        elif "Very Bearish" in verdict: color = '#8B0000'
        elif "Bearish" in verdict: color = '#B22222'
        return f'color: {color}; font-weight: bold;'

    # Itera sobre cada categoria para exibir uma tabela agrupada
    for category_name in ASSET_CATEGORIES.keys():
        st.subheader(category_name.replace("---", "").strip())
        
        df_category = df_all[df_all["Categoria"] == category_name]
        
        if not df_category.empty:
            df_display = df_category.sort_values(by="Score Final", ascending=False).reset_index(drop=True)
            
            column_order = ["Ativo", "Score Final", "Veredito", "Economia", "COT", "Sazonalidade"]
            df_display = df_display[[col for col in column_order if col in df_display.columns]]
            
            # Formatação específica para a coluna COT
            formatters = {
                "Score Final": "{:.2f}",
                "Economia": "{:.2f}",
                "COT": lambda x: "N/A" if isinstance(x, str) else f"{x:.0f}"
            }
            
            styled_df = df_display.style.apply(
                lambda x: x.map(style_scores), subset=[col for col in df_display.columns if col not in ['Ativo', 'Veredito']]
            ).apply(
                lambda x: x.map(style_verdict), subset=['Veredito']
            ).format(formatters)
            
            st.dataframe(styled_df, use_container_width=True, hide_index=True)

else:
    st.error("Não foi possível calcular os scores. Verifique os motores de dados.")

# --- RODAPÉ ---