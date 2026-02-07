from flask import Flask, render_template, request, redirect, url_for
import json
import os
import re

app = Flask(__name__)

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
        if profissao not in PROFISSOES_PERMITIDAS:
         return redirect(url_for("trabalhar"))

        whatsapp = request.form.get("whatsapp", "").strip()

        # 🔒 validação básica
        if not nome or not profissao or not whatsapp:
            # não salva nada, só volta pro formulário
            return redirect(url_for("trabalhar"))

        dados = carregar_trabalhadores()

# Estrutura padrão do trabalhador
# Futuro:
# "cidade": "Itanhaém"
# "estado": "SP"

        dados.append({
            "nome": nome,
            "profissao": profissao,
            "whatsapp": whatsapp
        })

        with open(CAMINHO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        return redirect(url_for("home"))

    return render_template("trabalhar.html")

# Página de contratação
# - Lê os trabalhadores do JSON
# - Aplica filtro por profissão (se existir)
# - Gera link de WhatsApp
# - Envia dados para o template


@app.route("/contratar")
def contratar():
    trabalhadores = carregar_trabalhadores()
    profissao = request.args.get("profissao")

    if profissao:
        trabalhadores = [
            t for t in trabalhadores
            if t["profissao"] == profissao
        ]

    # gera link do WhatsApp já pronto pro HTML
    for t in trabalhadores:
        t["whatsapp_link"] = normalizar_whatsapp(t["whatsapp"])

    profissoes = sorted(
        set(t["profissao"] for t in carregar_trabalhadores())
    )

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
