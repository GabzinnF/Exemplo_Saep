from flask import Flask, render_template, request, redirect, url_for ,flash
from sqlalchemy import select
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import Usuario, Produto, Movimentacao , db_session
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta' #Nome da senha


#config flask login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Faça login para acessar o sistema'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db_session.get(Usuario, int(user_id))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    email = request.form['form_email']
    senha = request.form['form_senha']
    if not email:
        flash('Campo email é obrigatório','danger')
        return render_template('login.html')
    if not senha:
        flash('Campo senha é obrigatório','danger')
        return render_template('login.html')

    usuario = db_session.execute(select(Usuario).where(Usuario.email == email)).scalar()
    #ou assim
    #sql_user = select(Usuario).where(Usuario.email == email)
    #usuario_exist = db_session.execute(sql_user).scalar()
    if usuario and usuario.check_password(senha):
        login_user(usuario)
        return redirect(url_for('dashboard'))
    else:
        flash('Falha na autenticacao:Email ou senha incorretos','danger')
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/produto/salvar', methods=['POST'])
@login_required
def salvar_produto():
    produto_id = request.form.get('id')
    nome = request.form.get('nome')
    descricao = request.form.get('descricao')
    estoque_minimo = int(request.form.get('estoque_minimo', 5))

    if produto_id:
        produto = db_session.get(Produto, int(produto_id))
        if produto:
            produto.nome = nome
            produto.descricao = descricao
            produto.estoque_minimo = estoque_minimo
            flash('Produto atualizado com sucesso!', 'success')
    else:
        novo_produto = Produto(
            nome=nome,
            descricao=descricao,
            estoque_minimo=estoque_minimo
        )
        db_session.add(novo_produto)
        flash('Produto cadastrado com sucesso!', 'success')

    db_session.commit()
    return redirect(url_for('gerenciar_produto'))

@app.route('/produto/', methods=['GET', 'POST'])
@login_required
def gerenciar_produto():
    if request.method == 'POST':
        termo_busca = request.form.get('busca')
        busca = select(Produto).where(Produto.nome.like(f'%{termo_busca}%'))
        busca_resultado = db_session.execute(busca).scalars().all()
        return render_template('produtos.html', produtos=busca_resultado)
    lista = select(Produto).order_by(Produto.nome.asc())
    lista_resultado = db_session.execute(lista).scalars().all()
    return render_template('produtos.html', produtos=lista_resultado)

@app.route('/produto/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_produto(id):
    produto = db_session.get(Produto, id)
    if produto:
        db_session.delete(produto)
        db_session.commit()
        flash('Produto excluído com sucesso!', 'success')
    else:
        flash('Produto não encontrado.', 'warning')

    return redirect(url_for('gerenciar_produto'))

if __name__ == '__main__':
    app.run(debug=True, port=5006, host='0.0.0.0')


@app.route('/produto/', methods=['GET','POST'])
@login_required
def gerenciar_produto():
    if request.method == 'POST':
        termo_busca = request.form.get('busca')
        busca = select(Produto).where(Produto.nome.like(f'%{termo_busca}%'))
        busca_resultado = db_session.execute(busca).scalars().all()
        return render_template('produtos.html', produtos=busca_resultado)
    lista = select(Produto).order_by(Produto.nome.asc())
    lista_resultado = db_session.execute(lista).scalars().all()
    return render_template('produtos.html', produtos=lista_resultado)


if __name__ == '__main__':
    app.run(debug=True, port=5006, host='0.0.0.0')