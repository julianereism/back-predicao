from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import firebase_admin
from firebase_admin import credentials, firestore
import os

app = Flask(__name__)
CORS(app)

# Caminho absoluto baseado no local do app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'modelos', 'decision_tree.pkl')

modelo = joblib.load(MODEL_PATH)


# Inicializar Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("dados-para-predicao-firebase-adminsdk-fbsvc-4166d88581.json")  # troque pelo seu arquivo
    firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/prever", methods=["POST"])
def prever():
    try:
        dados = request.get_json()

        # Verifica se todos os campos obrigatórios estão presentes
        campos_necessarios = [
            "distancia-casa", "distancia-ultima-transacao", "razao-media-compras",
            "loja-repetida", "uso-chip", "uso-codigo-seguranca", "loja-online",
            "cidade", "bairro"
        ]
        for campo in campos_necessarios:
            if campo not in dados:
                return jsonify({"erro": f"Campo obrigatório ausente: {campo}"}), 400

        # Formatar os dados para o modelo (apenas os 7 campos relevantes)
        entrada_modelo = [
            dados["distancia-casa"],
            dados["distancia-ultima-transacao"],
            dados["razao-media-compras"],
            dados["loja-repetida"],
            dados["uso-chip"],
            dados["uso-codigo-seguranca"],
            dados["loja-online"]
        ]

        # Fazer predição
        predicao = modelo.predict([entrada_modelo])[0]

        # Criar documento para Firestore
        doc = {
            "distancia-casa": dados["distancia-casa"],
            "distancia-ultima-transacao": dados["distancia-ultima-transacao"],
            "razao-media-compras": dados["razao-media-compras"],
            "loja-repetida": dados["loja-repetida"],
            "uso-chip": dados["uso-chip"],
            "uso-codigo-seguranca": dados["uso-codigo-seguranca"],
            "loja-online": dados["loja-online"],
            "cidade": dados["cidade"],
            "bairro": dados["bairro"],
            "fraude": bool(predicao),
            "timestamp": firestore.SERVER_TIMESTAMP
        }

        db.collection("dados-formulario").add(doc)

        return jsonify({"fraude": bool(predicao)})

    except Exception as e:
        return jsonify({"erro": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
