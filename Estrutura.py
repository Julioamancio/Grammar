import os

# Estrutura de diretórios
folders = [
    "templates",
    "static",
    "instance"
]

# Arquivos principais e seus conteúdos
arquivos = {
    "requirements.txt": """Flask>=2.2
Flask-Login>=0.6
Flask-SQLAlchemy>=2.5
Werkzeug>=2.2
""",
    "app.py": '''from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

def inicializa_banco():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    inicializa_banco()
    app.run(debug=True)
''',
    os.path.join("static", "custom.css"): '''body { background: #f5f7fa; margin: 0; }
.sidebar {
    background: #1976d2;
    min-height: 100vh;
    color: #fff;
    position: fixed;
    left: 0; top: 0; bottom: 0; width: 230px;
    display: flex; flex-direction: column; align-items: stretch; z-index: 10;
    box-shadow: 2px 0 24px 0 rgba(21,101,192,0.08);
}
.sidebar .logo {
    font-size: 2rem; font-weight: 900; letter-spacing: 1px;
    display: flex; align-items: center; gap: 13px;
    margin: 42px 0 36px 22px;
    color: #fff;
    line-height: 1.1;
}
.menu-btn {
    background: #fff;
    color: #1976d2;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 1.21rem;
    padding: 13px 17px 13px 18px;
    margin: 8px 18px 0 18px;
    transition: background 0.18s, color 0.18s;
    display: flex;
    align-items: center;
    gap: 12px;
    text-decoration: none;
    box-shadow: 0 2px 10px rgba(21,101,192,0.07);
}
.menu-btn.active, .menu-btn:hover { background: #ffd600; color: #222;}
.sidebar-logout { margin-top: auto; margin-bottom: 28px; }
.sidebar-logout .menu-btn { background: #ff5252; color: #fff; }
.sidebar-logout .menu-btn:hover { background: #ff1744; color: #fff; }
@media (max-width: 950px) {
    .sidebar { width: 100vw; min-height: unset; flex-direction: row; height: 80px; position: static; box-shadow: none;}
    .sidebar .logo { margin: 18px 0 0 12px; font-size: 1.2rem;}
    .sidebar-logout { margin: 0 0 0 auto;}
    .menu-btn { font-size: 1rem; padding: 10px 11px 10px 14px; margin: 12px 0 0 10px;}
}
.footer-julio {
    position: fixed;
    left: 0;
    bottom: 0;
    width: 100vw;
    background: #1976d2;
    color: #fff;
    text-align: right;
    padding: 0 38px 0 0;
    height: 42px;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    font-size: 1.11rem;
    z-index: 99;
    box-shadow: 0 -3px 12px #1976d211;
    letter-spacing: 0.1px;
}
.footer-signature {
    font-weight: 500;
    font-family: 'Fira Sans', 'Inter', Arial, sans-serif;
    opacity: .93;
    display: flex;
    align-items: center;
    gap: 7px;
}
.footer-signature .fa-code {
    color: #ffd600;
    font-size: 1.19rem;
    margin-bottom: 1.5px;
}
@media (max-width: 900px) {
    .footer-julio { font-size: .98rem; padding-right: 10px; height: 35px;}
    .footer-signature .fa-code { font-size: 1.09rem;}
}
''',
    os.path.join("templates", "base.html"): '''<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Apostila Gramatical{% endblock %}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- Bootstrap & FontAwesome -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
    <link rel="stylesheet" href="{{ url_for('static', filename='custom.css') }}">
    {% block head_extras %}{% endblock %}
</head>
<body>
    {% include 'sidebar.html' %}
    <div class="main-content" style="min-height:100vh;">
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="container mt-3">
                <div class="alert alert-warning alert-dismissible fade show" role="alert">
                    {% for message in messages %}
                        <div>{{ message }}</div>
                    {% endfor %}
                    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fechar"></button>
                </div>
            </div>
          {% endif %}
        {% endwith %}
        {% block content %}{% endblock %}
    </div>
    <footer class="footer-julio">
        <div>
            <span class="footer-signature">
                <i class="fa-solid fa-code"></i> feito por <b>Júlio Amâncio</b>
            </span>
        </div>
    </footer>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
''',
    os.path.join("templates", "sidebar.html"): '''<div class="sidebar">
    <div class="logo">
        <i class="fa-solid fa-book"></i>
        <span style="font-size:1.23rem;font-weight:900;margin-left:2px;line-height:1.1;">
            Gramática<br>Plataforma
        </span>
    </div>
    <a class="menu-btn{% if request.endpoint == 'dashboard' %} active{% endif %}" href="{{ url_for('dashboard') }}">
        <i class="fa-solid fa-house-chimney"></i> Home
    </a>
    <a class="menu-btn{% if request.endpoint == 'apostilas' %} active{% endif %}" href="{{ url_for('apostilas') }}">
        <i class="fa-solid fa-book-open"></i> Apostilas
    </a>
    <form method="GET" action="{{ url_for('logout') }}" class="sidebar-logout">
        <button class="menu-btn" type="submit">
            <i class="fa-solid fa-arrow-right-from-bracket"></i> Sair
        </button>
    </form>
</div>
''',
    os.path.join("templates", "login.html"): '''{% extends 'base.html' %}
{% block title %}Entrar - Apostila Gramatical{% endblock %}
{% block content %}
<div class="container" style="max-width: 400px; margin-top: 80px;">
    <div class="card">
        <div class="card-header text-center bg-primary text-white">
            <i class="fa-solid fa-user"></i> Login
        </div>
        <div class="card-body">
            <form method="POST">
                <div class="mb-3">
                    <label for="email" class="form-label">E-mail</label>
                    <input type="email" class="form-control" id="email" name="email" required autofocus>
                </div>
                <div class="mb-3">
                    <label for="senha" class="form-label">Senha</label>
                    <input type="password" class="form-control" id="senha" name="senha" required>
                </div>
                <button type="submit" class="btn btn-primary w-100"><i class="fa-solid fa-arrow-right-to-bracket"></i> Entrar</button>
            </form>
            <div class="mt-3 text-center">
                <a href="{{ url_for('cadastro') }}">Não tem conta? Cadastre-se</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    os.path.join("templates", "cadastro.html"): '''{% extends 'base.html' %}
{% block title %}Cadastro - Apostila Gramatical{% endblock %}
{% block content %}
<div class="container" style="max-width: 400px; margin-top: 80px;">
    <div class="card">
        <div class="card-header text-center bg-success text-white">
            <i class="fa-solid fa-user-plus"></i> Cadastro
        </div>
        <div class="card-body">
            <form method="POST">
                <div class="mb-3">
                    <label for="nome" class="form-label">Nome</label>
                    <input type="text" class="form-control" id="nome" name="nome" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">E-mail</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                <div class="mb-3">
                    <label for="senha" class="form-label">Senha</label>
                    <input type="password" class="form-control" id="senha" name="senha" required>
                </div>
                <button type="submit" class="btn btn-success w-100"><i class="fa-solid fa-user-plus"></i> Cadastrar</button>
            </form>
            <div class="mt-3 text-center">
                <a href="{{ url_for('login') }}">Já tem conta? Entrar</a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',
    os.path.join("templates", "dashboard.html"): '''{% extends 'base.html' %}
{% block title %}Painel - Apostila Gramatical{% endblock %}
{% block content %}
<div class="container" style="max-width: 700px; margin-top: 70px;">
    <div class="card">
        <div class="card-header bg-info text-white">
            <i class="fa-solid fa-house-chimney"></i>
            Bem-vindo(a), {{ current_user.nome }}!
        </div>
        <div class="card-body">
            <p class="fs-4">Aqui você pode acessar todas as apostilas de gramática do nível A1 ao C2.</p>
            <a href="{{ url_for('apostilas') }}" class="btn btn-primary btn-lg"><i class="fa-solid fa-book-open"></i> Ir para as Apostilas</a>
        </div>
    </div>
</div>
{% endblock %}
''',
    os.path.join("templates", "apostilas.html"): '''{% extends 'base.html' %}
{% block title %}Apostilas Gramaticais{% endblock %}
{% block content %}
<div class="apostila-title mb-4 mt-3">
    <i class="fa-solid fa-book"></i> Apostila Gramatical Completa
</div>
<div class="accordion" id="accordion-niveis">
    {% for nivel in ['A1','A2','B1','B2','C1','C2'] %}
    <div class="accordion-item">
        <h2 class="accordion-header" id="{{ nivel }}-head">
            <button class="accordion-button nivel-{{ nivel|lower }}" type="button" data-bs-toggle="collapse" data-bs-target="#{{ nivel }}" aria-expanded="{{ 'true' if loop.first else 'false' }}" aria-controls="{{ nivel }}">
                <i class="fa-solid fa-leaf me-2"></i> Nível {{ nivel }}
            </button>
        </h2>
        <div id="{{ nivel }}" class="accordion-collapse collapse {% if loop.first %}show{% endif %}" aria-labelledby="{{ nivel }}-head" data-bs-parent="#accordion-niveis">
            <div class="accordion-body">
                {% include 'apostila_' + nivel + '.html' %}
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
''',
}

# Apostilas vazias para cada nível
apostilas_niveis = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
apostila_exemplo = '''<!-- Conteúdo do nível {nivel}. Edite este arquivo para colocar sua apostila do nível {nivel}. -->
<div class="topic-title mt-5 mb-2">
    <i class="fa-solid fa-book-open-reader text-success"></i>
    <span class="topic-text">Bem-vindo ao nível {nivel}!</span>
</div>
<p class="fs-3 mb-4">
    Coloque aqui o conteúdo gramatical, exemplos, tabelas e dicas deste nível.
</p>
'''

# Criação de diretórios
for folder in folders:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Criação de arquivos principais
for caminho, conteudo in arquivos.items():
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(conteudo)

# Criação dos arquivos de apostila por nível
for nivel in apostilas_niveis:
    arquivo_nivel = os.path.join("templates", f"apostila_{nivel}.html")
    with open(arquivo_nivel, "w", encoding="utf-8") as f:
        f.write(apostila_exemplo.format(nivel=nivel))

print("Estrutura do projeto Flask-Apostila criada com sucesso!")