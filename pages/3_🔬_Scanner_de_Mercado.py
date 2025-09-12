# marketlens/pages/3_🔬_Scanner_de_Mercado.py

import streamlit as st
import pandas as pd
from view_utils import setup_sidebar
from utils.config import ASSET_CATEGORIES
from utils.scoring_engine import calculate_synapse_score

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Scanner de Mercado")
setup_sidebar()

# Guarda de autenticação
if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- TÍTULO DA PÁGINA ---
st.title("🔬 Scanner de Mercado")
st.caption("Análise multifatorial para identificar os ativos com o maior viés direcional.")
st.markdown("---")

# --- LÓGICA DE CÁLCULO E EXIBIÇÃO ---
try:
    with st.spinner("A analisar o mercado... O nosso motor está a calcular os scores para todos os ativos."):
        # 1. Obter a lista completa de ativos a partir da configuração
        all_assets = []
        for category, assets in ASSET_CATEGORIES.items():
            all_assets.extend(assets)
        
        # 2. Iterar sobre cada ativo e calcular o seu score
        scan_results = []
        progress_bar = st.progress(0, text="A analisar ativos...")
        total_assets = len(all_assets)
        
        for i, asset_name in enumerate(all_assets):
            total_score, verdict, individual_scores = calculate_synapse_score(asset_name)
            
            # 3. Montar o dicionário de resultados para a tabela
            result = {
                "Ativo": asset_name,
                "Score": total_score,
                "Veredito": verdict,
                "COT": individual_scores.get('COT', {}).get('text', 'N/A'),
                "Sazonalidade": individual_scores.get('Sazonalidade', {}).get('text', 'N/A')
            }
            scan_results.append(result)
            
            # Atualizar a barra de progresso
            progress_text = f"A analisar {asset_name} ({i+1}/{total_assets})"
            progress_bar.progress((i + 1) / total_assets, text=progress_text)
        
        progress_bar.empty() # Limpar a barra de progresso após a conclusão

    # 4. Converter os resultados para um DataFrame do Pandas
    if scan_results:
        df_scan = pd.DataFrame(scan_results)
        df_scan = df_scan.sort_values(by="Score", ascending=False)
        
        # 5. Aplicar estilo para replicar o heatmap da referência
        st.dataframe(
            df_scan.style.background_gradient(
                cmap='RdYlGn', # Gradiente de Vermelho -> Amarelo -> Verde
                subset=['Score'],
                vmin=-4, # Valor mínimo para o score
                vmax=4   # Valor máximo para o score
            ).format({
                "Score": "{:+.0f}" # Formata o score para ter sinal (+/-)
            }),
            use_container_width=True,
            height=800
        )
    else:
        st.error("Não foi possível gerar a análise do scanner.")

except Exception as e:
    st.error(f"Ocorreu um erro inesperado ao gerar o scanner: {e}")
# --- FIM DO MÓDULO Scanner_de_Mercado.py ---