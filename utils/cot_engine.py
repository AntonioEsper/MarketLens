# marketlens/utils/cot_engine.py

from firebase_config import db
from .config import cot_market_map
from .data_loader import get_cot_data

def update_cot_data_in_firestore():
    """
    Motor que busca o histórico de dados do COT e os armazena no Firestore.
    Esta função é um gerador, que emite mensagens de status durante a sua execução.
    """
    if not cot_market_map:
        yield "❌ O `cot_market_map` no ficheiro de configuração está vazio."
        return

    total_assets = len(cot_market_map)
    yield f"ℹ️ A iniciar a atualização para {total_assets} ativos..."

    for i, (asset_name, contract_code) in enumerate(cot_market_map.items()):
        try:
            yield f"({i+1}/{total_assets}) 🔄 A buscar histórico para {asset_name}..."
            
            sanitized_asset_name = asset_name.replace('/', '_')
            df_cot = get_cot_data(contract_code)

            if df_cot is not None and not df_cot.empty:
                # Converte o DataFrame para um formato adequado para o Firestore
                df_cot.index = df_cot.index.strftime('%Y-%m-%d')
                data_to_store = df_cot.to_dict(orient='index')

                # Tenta escrever no Firestore
                doc_ref = db.collection("cot_data").document(sanitized_asset_name)
                doc_ref.set(data_to_store)
                
                # Confirma o sucesso da escrita
                yield f"({i+1}/{total_assets}) ✅ Sucesso: Dados de {asset_name} guardados no Firestore como '{sanitized_asset_name}'."
            else:
                yield f"({i+1}/{total_assets}) ⚠️ Aviso: Não foram encontrados dados do COT para {asset_name} na API."
        except Exception as e:
            yield f"({i+1}/{total_assets}) ❌ Falha ao processar {asset_name}. Erro: {e}"
    
    yield "✅ Processo Concluído!"

