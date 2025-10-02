from app import app, db
from flask import render_template, url_for, request, redirect, flash
from .forms import UserForm, LoginForm, PacienteForm, ProntuarioRegistroForm 
from flask_login import login_user, logout_user, current_user, login_required
from .models import Paciente, Prontuario
from sqlalchemy import or_

# Tela inicial (Dashboard do Médico)
@app.route("/", methods=['GET', 'POST'])
@login_required
def homepage():
    pacientes_recentes = Paciente.query.order_by(Paciente.data_cadastro.desc()).limit(5).all()
    total_pacientes = Paciente.query.count()
    return render_template(
        "index.html",
        pacientes_recentes=pacientes_recentes,
        total_pacientes=total_pacientes
    )

# Página de Login
@app.route ('/login', methods=['GET', 'POST'])
def LoginPage():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
        
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = form.login()
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Login bem-sucedido. Bem-vindo(a), {user.nome}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('homepage'))
        except Exception as e:
            flash(str(e), 'danger')
            
    return render_template("login.html", form=form)

# Página de Cadastro
@app.route ('/cadastro', methods=['GET', 'POST'])
def RegisterPage():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
        
    form = UserForm()
    if form.validate_on_submit():
        try:
            user = form.save()
            flash(f'Conta criada para {user.nome}! Você já pode fazer login.', 'success')
            return redirect(url_for('LoginPage'))
        except Exception as e:
            flash(f'Erro ao cadastrar: {e}', 'danger')
            
    return render_template("cadastro.html", form=form)

# Deslogar
@app.route('/sair/')
@login_required
def logout():
    logout_user()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('LoginPage')) # Redireciona para o login


# Página de Pacientes (Lista)
@app.route('/pacientes', methods=['GET', 'POST'])
@login_required
def listar_pacientes():
    pesquisa = request.args.get('pesquisa', '')
    dados = Paciente.query.order_by(Paciente.nome)
    
    if pesquisa:
        dados = dados.filter(or_(
            Paciente.nome.ilike(f"%{pesquisa}%"),
            Paciente.cpf.ilike(f"%{pesquisa}%")
        ))
        
    pacientes = dados.all()
    return render_template("listar_pacientes.html", pacientes=pacientes) # Novo template

# Página Pacientes Cadastro
@app.route('/pacientes/cadastro', methods=['GET', 'POST'])
@login_required
def novo_paciente():
    form = PacienteForm()
    if form.validate_on_submit():
        try:
            paciente = form.save()
            flash(f'Paciente {paciente.nome} cadastrado com sucesso.', 'success')
            return redirect(url_for('ver_prontuario', paciente_id=paciente.id))
        except Exception as e:
            flash(f'Erro ao cadastrar paciente. Verifique o CPF: {e}', 'danger')
            
    return render_template("novo_paciente.html", form=form) # Novo template

# Página Prontuário (Visualização e Adição de Registro)
@app.route('/prontuario/<int:paciente_id>', methods=['GET', 'POST'])
@login_required
def ver_prontuario(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    # Form para adicionar registro, deve ser passado para o template
    form_registro = ProntuarioRegistroForm() 
    
    # Lógica de Adição de Registro (POST na mesma página)
    if form_registro.validate_on_submit() and form_registro.btnSubmit.data:
        try:
            # Assumimos que o form_registro tem um método save que requer paciente_id e user_id
            form_registro.save(paciente_id=paciente.id, user_id=current_user.id)
            flash('Registro adicionado ao prontuário com sucesso.', 'success')
            return redirect(url_for('ver_prontuario', paciente_id=paciente.id))
        except Exception as e:
            flash(f'Erro ao salvar registro: {e}', 'danger')

    registros = Prontuario.query.filter_by(paciente_id=paciente_id).order_by(Prontuario.data_registro.desc()).all()

    return render_template(
        'ver_prontuario.html', 
        paciente=paciente, 
        registros=registros, 
        form_registro=form_registro
    )

# Página Paciente Edição (Edita dados cadastrais do paciente)
@app.route('/paciente/edicao/<int:paciente_id>', methods=['GET', 'POST'])
@login_required
def edit_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    form = PacienteForm(obj=paciente)

    if form.validate_on_submit():
        try:
            form.update(paciente)
            flash('Dados do paciente atualizados com sucesso.', 'success')
            return redirect(url_for('ver_prontuario', paciente_id=paciente.id))
        except Exception as e:
            flash(f'Erro ao atualizar dados: {e}', 'danger')

    return render_template('paciente_edicao.html', form=form, paciente=paciente)

# Deletar um Paciente
@app.route('/paciente/excluir/<int:paciente_id>', methods=['POST'])
@login_required
def delete_paciente(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    try:
        Prontuario.query.filter_by(paciente_id=paciente.id).delete()
        db.session.delete(paciente)
        db.session.commit()
        flash(f'Paciente {paciente.nome} e seu prontuário foram excluídos.', 'info')
        return redirect(url_for('listar_pacientes'))
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir paciente: {e}', 'danger')
        return redirect(url_for('ver_prontuario', paciente_id=paciente_id))
