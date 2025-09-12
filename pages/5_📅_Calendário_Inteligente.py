# marketlens/pages/5_📅_Calendário_Inteligente.py

import streamlit as st
import streamlit.components.v1 as components
from view_utils import setup_sidebar

# --- CONFIGURAÇÃO DA PÁGINA E AUTENTICAÇÃO ---
st.set_page_config(layout="wide", page_title="Calendário Económico")
setup_sidebar()

if 'user_info' not in st.session_state or st.session_state['user_info'] is None:
    st.warning("Acesso restrito. Por favor, faça o login.")
    st.stop()

# --- CABEÇALHO ---
st.title("📅 Calendário Económico em Tempo Real")
st.caption("Fornecido por TradingView.")
st.markdown("---")

# --- LÓGICA DE EMBEBIMENTO DO WIDGET ---

# O código HTML para o widget é fornecido diretamente pelo TradingView.
# A correção chave, identificada por si, é definir uma altura fixa DENTRO do script.
tradingview_widget_html = """
<!-- TradingView Widget BEGIN -->
<div class="tradingview-widget-container" style="height:100%;width:100%">
  <div class="tradingview-widget-container__widget" style="height:calc(100% - 32px);width:100%"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
  {
  "colorTheme": "dark",
  "isTransparent": false,
  "width": "100%",
  "height": "800",
  "locale": "pt",
  "importanceFilter": "-1,0,1",
  "currencyFilter": "USD,EUR,JPY,GBP,CAD,AUD,NZD,CHF,CNY"
}
  </script>
</div>
<!-- TradingView Widget END -->
"""

# Usamos a função de componentes do Streamlit para renderizar o HTML.
# A altura aqui define a altura do 'iframe' que o Streamlit cria.
# Definimos um valor ligeiramente maior para acomodar o widget e a sua pequena barra de branding.
components.html(tradingview_widget_html, height=820, scrolling=False)

