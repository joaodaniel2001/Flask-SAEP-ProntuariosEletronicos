from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, DateField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_bcrypt import Bcrypt

from app import db, Bcrypt
bcrypt = Bcrypt()

class UserForm (FlaskForm):
    nome = StringField ('Nome', validators=[DataRequired()])
    sobrenome = StringField ('Sobrenome', validators=[DataRequired()])
    tipo_profissional = SelectField(
        'Tipo de Profissional', 
        choices=[('Medico', 'Médico(a)'), ('Enfermeiro', 'Enfermeiro(a)'), ('Administrador', 'Administrador')],
        validators=[DataRequired()]
    )
    email = StringField ('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmacao_senha = PasswordField('Confirme sua senha', validators=[DataRequired(), EqualTo('senha')])
    btnSubmit = SubmitField('Cadastrar Profissional')

    def validate_email(self, email):
        from app.models import User
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('E-mail já cadastrado.')

    def save (self):
        from app.models import User
        senha = bcrypt.generate_password_hash(self.senha.data.encode('utf-8'))
        user = User (
            nome = self.nome.data,
            sobrenome = self.sobrenome.data,
            email = self.email.data,
            senha = senha.decode('utf-8'),
            tipo_profissional = self.tipo_profissional.data
        )

        db.session.add(user)
        db.session.commit()
        return (user)

class LoginForm (FlaskForm):
    email = StringField ('E-mail', validators=[DataRequired(),Email()])
    senha = PasswordField ('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Login')

    def login (self):
        from app.models import User
        user = User.query.filter_by (email=self.email.data).first()

        if user:
            if bcrypt.check_password_hash (user.senha, self.senha.data.encode ('utf-8')):
                return user
            else:
                raise Exception ('Senha incorreta!')
        else:
            raise Exception ('Usuário não encontrado!')

class PacienteForm(FlaskForm):
    nome = StringField('Nome Completo', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[DataRequired(), Length(min=11, max=14)])
    data_nascimento = DateField('Data de Nascimento (AAAA-MM-DD)', format='%Y-%m-%d', validators=[DataRequired()])
    alergias = TextAreaField('Alergias Conhecidas', default='Nenhuma')
    medicamentos_uso = TextAreaField('Medicamentos em Uso', default='Nenhum')
    btnSubmit = SubmitField('Salvar Paciente')

    def save(self):
        from app.models import Paciente
        paciente = Paciente(
            nome=self.nome.data,
            cpf=self.cpf.data,
            data_nascimento=self.data_nascimento.data,
            alergias=self.alergias.data,
            medicamentos_uso=self.medicamentos_uso.data,
        )
        db.session.add(paciente)
        db.session.commit()
        return paciente

    def update(self, paciente):
        paciente.nome = self.nome.data
        paciente.cpf = self.cpf.data
        paciente.data_nascimento = self.data_nascimento.data
        paciente.alergias = self.alergias.data
        paciente.medicamentos_uso = self.medicamentos_uso.data
        db.session.commit()
        return paciente

class ProntuarioRegistroForm(FlaskForm):
    tipo_registro = SelectField(
        'Tipo de Registro', 
        choices=[
            ('Consulta', 'Consulta Médica'), 
            ('Exame', 'Resultado de Exame'), 
            ('Procedimento', 'Procedimento Realizado'), 
            ('Prescricao', 'Prescrição'),
            ('Evolucao', 'Evolução Diária/Internação')
        ],
        validators=[DataRequired()]
    )
    descricao = TextAreaField('Detalhes do Registro', validators=[DataRequired()])
    btnSubmit = SubmitField('Adicionar Registro')
    
    def save(self, paciente_id, user_id):
        from app.models import Prontuario
        prontuario = Prontuario(
            paciente_id=paciente_id,
            user_id=user_id,
            tipo_registro=self.tipo_registro.data,
            descricao=self.descricao.data
        )
        db.session.add(prontuario)
        db.session.commit()
        return prontuario