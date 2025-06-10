from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuração do Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.seuprovedor.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'julioamancio2014@email.com'
app.config['MAIL_PASSWORD'] = 'bbkdgkdekincbdlq'

# Corrige possíveis problemas de sessão no localhost
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    nivel_maximo = db.Column(db.String(10), default="A1")  # Controle de progresso

class MedalhaProgresso(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    nivel = db.Column(db.String(10), nullable=False)
    questao = db.Column(db.Integer, nullable=False)
    medalha = db.Column(db.String(10), nullable=False)  # 'ouro', 'prata', 'bronze'
    __table_args__ = (db.UniqueConstraint('user_id', 'nivel', 'questao', name='unq_medalha'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

NIVEIS_ORDEM = ["A1", "A2", "B1", "B2", "C1", "C2"]

def proximo_nivel(nivel):
    try:
        idx = NIVEIS_ORDEM.index(nivel)
        if idx+1 < len(NIVEIS_ORDEM):
            return NIVEIS_ORDEM[idx+1]
    except Exception:
        pass
    return None

@app.route('/exercicios')
@login_required
def exercicios():
    niveis_disponiveis = {nivel: True for nivel in NIVEIS_ORDEM}
    return render_template('exercicios.html',
                           nivel_maximo=current_user.nivel_maximo,
                           niveis=NIVEIS_ORDEM,
                           niveis_disponiveis=niveis_disponiveis)

@app.route("/exerciciosA1")
@login_required
def exerciciosA1():
    return render_template("exerciciosA1.html")

@app.route("/exerciciosA2")
@login_required
def exerciciosA2():
    return render_template("exerciciosA2.html")

@app.route("/exerciciosB1")
@login_required
def exerciciosB1():
    return render_template("exerciciosB1.html")

@app.route("/exerciciosB2")
@login_required
def exerciciosB2():
    return render_template("exerciciosB2.html")

@app.route("/exerciciosC1")
@login_required
def exerciciosC1():
    return render_template("exerciciosC1.html")

@app.route("/exerciciosC2")
@login_required
def exerciciosC2():
    return render_template("exerciciosC2.html")

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/apostilas')
@login_required
def apostilas():
    return render_template('apostilas.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.senha_hash, senha):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Email ou senha incorretos.')
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado!')
            return redirect(url_for('cadastro'))
        user = User(nome=nome, email=email, senha_hash=generate_password_hash(senha))
        db.session.add(user)
        db.session.commit()
        flash('Cadastro realizado com sucesso! Faça login.')
        return redirect(url_for('login'))
    return render_template('cadastro.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.')
    return redirect(url_for('login'))

@app.route('/registrar_medalha', methods=['POST'])
@login_required
def registrar_medalha():
    data = request.json
    nivel = data.get('nivel')
    questao = data.get('questao')
    medalha = data.get('medalha')  # 'ouro', 'prata', 'bronze'
    if not (nivel and questao is not None and medalha):
        return jsonify({'status': 'erro', 'mensagem': 'Dados incompletos'}), 400

    existente = MedalhaProgresso.query.filter_by(
        user_id=current_user.id,
        nivel=nivel,
        questao=questao
    ).first()

    if existente:
        medalha_rank = {'ouro': 3, 'prata': 2, 'bronze': 1}
        if medalha_rank.get(medalha, 0) > medalha_rank.get(existente.medalha, 0):
            existente.medalha = medalha
            db.session.commit()
            return jsonify({'status': 'ok', 'medalha': medalha})
        return jsonify({'status': 'ok', 'medalha': None})
    nova = MedalhaProgresso(
        user_id=current_user.id,
        nivel=nivel,
        questao=questao,
        medalha=medalha
    )
    db.session.add(nova)
    db.session.commit()
    return jsonify({'status': 'ok', 'medalha': medalha})

@app.route('/medalhas', methods=['GET'])
@login_required
def medalhas():
    medalhas = MedalhaProgresso.query.filter_by(user_id=current_user.id).all()
    contagem = {'ouro': 0, 'prata': 0, 'bronze': 0}
    for m in medalhas:
        if m.medalha in contagem:
            contagem[m.medalha] += 1
    return jsonify(contagem)

@app.route('/minhas_medalhas', methods=['GET'])
@login_required
def minhas_medalhas():
    medalhas = MedalhaProgresso.query.filter_by(user_id=current_user.id).all()
    contagem = {'ouro': 0, 'prata': 0, 'bronze': 0, 'questoes': {}}
    for m in medalhas:
        if m.medalha in contagem:
            contagem[m.medalha] += 1
        contagem['questoes'][f"{m.nivel}-{m.questao}"] = m.medalha
    return jsonify(contagem)

def gerar_certificado_pdf(nome, nivel, resultado):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont('Helvetica-Bold', 26)
    c.drawString(100, 770, "Certificado de Conclusão")
    c.setFont('Helvetica', 16)
    c.drawString(100, 710, f"Nome: {nome}")
    c.drawString(100, 680, f"Nível: {nivel}")
    c.drawString(100, 650, f"Pontuação: {resultado}%")
    c.setFont('Helvetica', 14)
    if resultado >= 60:
        c.drawString(100, 610, "Parabéns! Você atingiu a pontuação mínima para certificação.")
        c.drawString(100, 580, "Sugestão pedagógica: Continue revisando os tópicos e avance nos estudos!")
    else:
        c.drawString(100, 610, "Você não atingiu a pontuação mínima para certificação.")
        c.drawString(100, 580, "Sugestão pedagógica: Refaça os exercícios e revise os conteúdos antes de tentar novamente.")
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/enviar_resultado', methods=['POST'])
@login_required
def enviar_resultado():
    data = request.json
    nivel = data.get('nivel')
    resultado = data.get('resultado')
    nome = current_user.nome
    email = current_user.email
    if not (nivel and resultado is not None):
        return jsonify({'status': 'erro', 'mensagem': 'Dados incompletos'}), 400
    resultado = int(resultado)
    if resultado >= 60:
        prox = proximo_nivel(nivel)
        if prox:
            if NIVEIS_ORDEM.index(current_user.nivel_maximo) < NIVEIS_ORDEM.index(prox):
                current_user.nivel_maximo = prox
                db.session.commit()
        pdf_buffer = gerar_certificado_pdf(nome, nivel, resultado)
        try:
            msg = Message(
                subject=f"Certificado de Conclusão - Nível {nivel}",
                sender=app.config['MAIL_USERNAME'],
                recipients=[email]
            )
            msg.body = (
                f"Olá {nome},\n\n"
                f"Parabéns! Você concluiu o nível {nivel} com {resultado}% de acertos.\n"
                "Seu certificado está em anexo!\n\n"
                "Equipe Pedagógica"
            )
            pdf_buffer.seek(0)
            msg.attach(f"Certificado_{nivel}_{nome}.pdf", "application/pdf", pdf_buffer.read())
            mail.send(msg)
            return jsonify({
                'status': 'sucesso',
                'mensagem': 'Certificado enviado para seu e-mail.',
                'aprovado': True,
                'proximo_nivel': prox
            })
        except Exception as e:
            return jsonify({
                'status': 'parcial',
                'mensagem': 'Nível concluído, mas houve um erro ao enviar o certificado.',
                'erro': str(e),
                'aprovado': True,
                'proximo_nivel': prox
            })
    else:
        return jsonify({
            'status': 'falha',
            'mensagem': 'Pontuação insuficiente para obter o certificado (mínimo 60%).',
            'aprovado': False
        })

# --- NOVA ROTA PARA SERVIR EXERCÍCIOS ENEM COMO TEMPLATE (PROFISSIONAL E SEGURO) ---
@app.route('/enem/exercicio/<modulo>')
@login_required
def enem_exercicio(modulo):
    permitidos = {
        "anuncio", "cartum", "charge", "cientifico", "dialogo",
        "grafico", "informativo", "jornal", "musica", "opinativo",
        "poema", "publicidade", "tirinha"
    }
    if modulo not in permitidos:
        return "Exercício não encontrado", 404
    return render_template(f'enem/{modulo}.html')

@app.route('/enem-questoes')
@login_required
def enem_questoes():
    return render_template('enem.html')

@app.route('/reset_medalhas', methods=['POST'])
@login_required
def reset_medalhas():
    data = request.json
    nivel = data.get('nivel')
    if not nivel:
        return jsonify({'status': 'erro', 'mensagem': 'Nível não especificado.'}), 400
    if nivel == "ALL":
        MedalhaProgresso.query.filter_by(user_id=current_user.id).delete()
        if 'medalhas_enem' in session:
            session['medalhas_enem'][str(current_user.id)] = {}
            session.modified = True
    else:
        MedalhaProgresso.query.filter_by(user_id=current_user.id, nivel=nivel).delete()
        if nivel.startswith("ENEM_") and 'medalhas_enem' in session:
            usuario = str(current_user.id)
            if usuario in session['medalhas_enem'] and nivel in session['medalhas_enem'][usuario]:
                del session['medalhas_enem'][usuario][nivel]
                session.modified = True
    db.session.commit()
    return jsonify({'status': 'ok'})

# === ROTAS EXCLUSIVAS PARA MEDALHAS ENEM (session-based, não banco!) ===

@app.route('/registrar_medalha_enem', methods=['POST'])
@login_required
def registrar_medalha_enem():
    data = request.json
    nivel = data.get('nivel')
    questao = str(data.get('questao'))
    medalha = data.get('medalha')
    usuario = str(current_user.id)
    if not (nivel and questao and medalha):
        return jsonify({'status': 'erro', 'mensagem': 'Dados incompletos'}), 400

    medalhas_enem = session.get('medalhas_enem', {})
    user_medalhas = medalhas_enem.get(usuario, {})
    nivel_medalhas = user_medalhas.get(nivel, {})

    medalha_rank = {'ouro': 3, 'prata': 2, 'bronze': 1}
    medalha_atual = nivel_medalhas.get(questao)
    if medalha_atual:
        if medalha_rank[medalha] > medalha_rank.get(medalha_atual, 0):
            nivel_medalhas[questao] = medalha
        else:
            medalha = medalha_atual
    else:
        nivel_medalhas[questao] = medalha

    user_medalhas[nivel] = nivel_medalhas
    medalhas_enem[usuario] = user_medalhas
    session['medalhas_enem'] = medalhas_enem
    session.modified = True
    return jsonify({'medalha': medalha})

@app.route('/minhas_medalhas_enem')
@login_required
def minhas_medalhas_enem():
    nivel = request.args.get('nivel')
    usuario = str(current_user.id)
    medalhas_enem = session.get('medalhas_enem', {}).get(usuario, {})
    if nivel:
        return jsonify({'questoes': medalhas_enem.get(nivel, {})})
    else:
        return jsonify({'medalhas': medalhas_enem})

@app.route('/medalhas_enem')
@login_required
def medalhas_enem_totais():
    usuario = str(current_user.id)
    medalhas_enem = session.get('medalhas_enem', {}).get(usuario, {})
    total = {'ouro': 0, 'prata': 0, 'bronze': 0}
    for nivel, questoes in medalhas_enem.items():
        for med in questoes.values():
            if med in total:
                total[med] += 1
    return jsonify(total)

@app.route('/reset_medalhas_enem', methods=['POST'])
@login_required
def reset_medalhas_enem():
    usuario = str(current_user.id)
    medalhas_enem = session.get('medalhas_enem', {})
    medalhas_enem[usuario] = {}
    session['medalhas_enem'] = medalhas_enem
    session.modified = True
    return jsonify({'status': 'ok'})

def inicializa_banco():
    with app.app_context():
        db.create_all()
        if not User.query.first():
            user = User(
                nome="Usuário Teste",
                email="teste@exemplo.com",
                senha_hash=generate_password_hash("senha123"),
                nivel_maximo="A1"
            )
            db.session.add(user)
            db.session.commit()

if __name__ == '__main__':
    inicializa_banco()
    app.run(debug=True)