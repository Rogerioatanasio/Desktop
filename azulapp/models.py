from .extensions import db

class Trabalhador(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    profissao = db.Column(db.String(80), nullable=False)
    whatsapp = db.Column(db.String(40), nullable=False)

    def __repr__(self):
        return f"<Trabalhador {self.nome}>"
