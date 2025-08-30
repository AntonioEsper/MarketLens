# marketlens/firebase_config.py (Versão com firebase-admin e Pyrebase)

import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

def initialize_firebase_admin():
    """
    Inicializa a conexão de ADMIN com o Firebase.
    Usada para gerir utilizadores e aceder ao Firestore pelo servidor.
    Retorna a instância do cliente Firestore.
    """
    if not firebase_admin._apps:
        try:
            service_account_creds = st.secrets["firebase_service_account"]
            creds_dict = dict(service_account_creds)
            creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK inicializado com sucesso!")
        except Exception as e:
            st.error("Falha ao inicializar o Firebase Admin SDK.")
            print(f"Erro detalhado (Admin SDK): {e}")
            return None
    return firestore.client()

def initialize_pyrebase():
    """
    Inicializa a conexão de CLIENTE com o Firebase.
    Usada para autenticação de utilizadores (login com email/password).
    Retorna o objeto de autenticação do Pyrebase.
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

# Inicializa as duas conexões
db = initialize_firebase_admin()
auth_client = initialize_pyrebase()
