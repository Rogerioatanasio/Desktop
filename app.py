from flask import Flask, render_template, request, redirect, url_for
import json
import os
import re

app = Flask(__name__)

from azulapp.extensions import db, migrate
from azulapp.models import Trabalhador

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///local.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev-key"

db.init_app(app)
migrate.init_app(app, db)


# ==============================
# FUNÇÕES AUXILIARES
# ==============================

def normalizar_whatsapp(numero):
    # remove tudo que não for número
    numero = re.sub(r'\D', '', numero)

    # se não tiver DDI, adiciona Brasil (55)
    if len(numero) == 11:  # ex: 11999999999
        numero = '55' + numero

    return f"https://wa.me/{numero}"


# ==============================
# CONFIGURAÇÃO DO CAMINHO DO JSON
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(BASE_DIR, "data", "trabalhadores.json")

# garante que a pasta exista
os.makedirs(os.path.dirname(CAMINHO_DADOS), exist_ok=True)

# garante que o arquivo exista
if not os.path.exists(CAMINHO_DADOS):
    with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
        json.dump([], f)

# Lê o arquivo JSON e retorna a lista de trabalhadores
# Se o arquivo estiver vazio ou corrompido, retorna lista vazia


def carregar_trabalhadores():
    with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


PROFISSOES_PERMITIDAS = [
    "Pedreiro",
    "Eletricista",
    "Encanador",
    "Pintor",
    "Faxineira",
    "Ajudante Geral"
]



# ==============================
# ROTAS
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/trabalhar", methods=["GET", "POST"])
def trabalhar():

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        profissao = request.form.get("profissao", "").strip()
        whatsapp = request.form.get("whatsapp", "").strip()

        if profissao not in PROFISSOES_PERMITIDAS:
            return redirect(url_for("trabalhar"))

        if not nome or not profissao or not whatsapp:
            return redirect(url_for("trabalhar"))

        novo = Trabalhador(
            nome=nome,
            profissao=profissao,
            whatsapp=whatsapp
        )

        db.session.add(novo)
        db.session.commit()

        return redirect(url_for("home"))

    return render_template("trabalhar.html")


# Estrutura padrão do trabalhador
# Futuro:
# "cidade": "Itanhaém"
# "estado": "SP"




# Página de contratação
# - Lê os trabalhadores do JSON
# - Aplica filtro por profissão (se existir)
# - Gera link de WhatsApp
# - Envia dados para o template


@app.route("/contratar")
def contratar():
    profissao = request.args.get("profissao")

    query = Trabalhador.query
    if profissao:
        query = query.filter_by(profissao=profissao)

    trabalhadores_db = query.all()

    trabalhadores = []
    for t in trabalhadores_db:
        trabalhadores.append({
            "nome": t.nome,
            "profissao": t.profissao,
            "whatsapp": t.whatsapp,
            "whatsapp_link": normalizar_whatsapp(t.whatsapp),

            # ainda não existe no banco/modelo, mas mantém o template pronto:
            "cidade": None,
            "estado": None
        })

    profissoes = sorted({t.profissao for t in Trabalhador.query.all()})
  
    print("DEBUG trabalhadores:", trabalhadores[:5])


    return render_template(
        "contratar.html",
        trabalhadores=trabalhadores,
        profissoes=profissoes,
        profissao_selecionada=profissao
    )



# ==============================
# EXECUÇÃO
# ==============================

if __name__ == "__main__":
    app.run(debug=True)
