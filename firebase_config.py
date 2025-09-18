# marketlens/firebase_config.py

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, storage
import pyrebase

def initialize_firebase_admin():
    """
    Inicializa a conexão de ADMIN com o Firebase, incluindo o Storage.
    """
    if not firebase_admin._apps:
        try:
            service_account_creds = st.secrets["firebase_service_account"]
            creds_dict = dict(service_account_creds)
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
            cred = credentials.Certificate(creds_dict)
            
            # CORREÇÃO DEFINITIVA: Obtém o nome do bucket a partir dos segredos
            # para garantir que está sempre correto.
            storage_bucket_name = st.secrets.get("firebase_storage_bucket")
            if not storage_bucket_name:
                # Se não estiver nos segredos, constrói-o a partir do project_id como um fallback.
                storage_bucket_name = f"{creds_dict['project_id']}.firebasestorage.app"
            
            firebase_admin.initialize_app(cred, {
                'storageBucket': storage_bucket_name
            })
            print(f"Firebase Admin SDK (com Storage em '{storage_bucket_name}') inicializado com sucesso!")

        except Exception as e:
            st.error("Falha ao inicializar o Firebase Admin SDK.")
            print(f"Erro detalhado (Admin SDK): {e}")
            return None
    return firestore.client()

def initialize_pyrebase():
    """
    Inicializa a conexão de CLIENTE com o Firebase.
    """
    try:
        web_config = st.secrets["firebase_web_config"]
        firebase_client = pyrebase.initialize_app(dict(web_config))
        print("Pyrebase (Client) inicializado com sucesso!")
        return firebase_client.auth()
    except Exception as e:
        st.error("Falha ao inicializar o Pyrebase (Client).")
        print(f"Erro detalhado (Pyrebase): {e}")
        return None

# Inicializa as conexões
db = initialize_firebase_admin()
auth_client = initialize_pyrebase()

