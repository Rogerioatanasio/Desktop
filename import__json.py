import json
import os

from azulapp import create_app
from azulapp.extensions import db
from azulapp.models import Trabalhador

# caminho do seu JSON atual (igual no app.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAMINHO_DADOS = os.path.join(BASE_DIR, "data", "trabalhadores.json")


def carregar_trabalhadores_json():
    if not os.path.exists(CAMINHO_DADOS):
        return []

    with open(CAMINHO_DADOS, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def main():
    app = create_app()

    with app.app_context():
        dados = carregar_trabalhadores_json()

        if not dados:
            print("JSON vazio ou inexistente. Nada para importar.")
            return

        inseridos = 0
        pulados = 0

        for t in dados:
            nome = (t.get("nome") or "").strip()
            profissao = (t.get("profissao") or "").strip()
            whatsapp = (t.get("whatsapp") or "").strip()

            if not nome or not profissao or not whatsapp:
                pulados += 1
                continue

            # evita duplicar: regra simples (nome + profissão + whatsapp)
            existe = Trabalhador.query.filter_by(
                nome=nome, profissao=profissao, whatsapp=whatsapp
            ).first()

            if existe:
                pulados += 1
                continue

            db.session.add(Trabalhador(
                nome=nome,
                profissao=profissao,
                whatsapp=whatsapp
            ))
            inseridos += 1

        db.session.commit()

        print(f"Import finalizado. Inseridos: {inseridos} | Pulados: {pulados} | Total JSON: {len(dados)}")


if __name__ == "__main__":
    main()
