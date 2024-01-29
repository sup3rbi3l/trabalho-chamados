from hashlib import scrypt
import warnings
from flask import Flask, redirect, render_template, request, url_for
import mysql.connector
cnx = mysql.connector.connect(
  host='127.0.0.1',
  user='root',
  password=''
)

# Executar a instrução SQL para verificar se o banco de dados existe
cursor = cnx.cursor()
cursor.execute('SELECT COUNT(*) FROM information_schema.SCHEMATA WHERE SCHEMA_NAME = "chamadosti";')

# Obter o número de resultados
num_results = cursor.fetchone()[0]

# Fechar a conexão com o banco de dados
cnx.close()

# Se o número de resultados for maior que zero, o banco de dados existe
if num_results > 0:
  print('O banco de dados agenda existe e esta pronto para uso.')
else:
    # Conectar-se ao servidor MySQL para criar o banco de dados
    cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password=''
    )

    # Criar o banco de dados agenda
    cursor = cnx.cursor()
    cursor.execute('CREATE DATABASE chamadosti;')
    cnx.commit()

    # Conectar-se ao banco de dados agenda recém-criado
    cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='chamadosti'  # Especificar o banco de dados
    )

    # Criar a tabela contatos
    cursor = cnx.cursor()
    cursor.execute('CREATE TABLE usuarios (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), email VARCHAR(255),senha VARCHAR(255));')
    cursor.execute("""
      CREATE TABLE chamados (id INT AUTO_INCREMENT PRIMARY KEY,
      numero	int,
      data_abertura datetime,
      data_fechamento datetime,
      status varchar(20),
      prioridade varchar(20),
      tipo_problema varchar(20),
      descricao VARCHAR(500),
      solucao VARCHAR(500),
      usuario_id int,
      tecnico_id int,
      equipamento_id int,
      aplicativo_id int
    )
  """)
    cursor.execute('CREATE TABLE tecnicos(id INT AUTO_INCREMENT PRIMARY KEY, nome varchar(100),email varchar(100),telefone varchar(20),departamento varchar(50));')
    cursor.execute('CREATE TABLE equipamentos(id int AUTO_INCREMENT PRIMARY KEY,nome	varchar(100),modelo	varchar(50),numero_de_serie	varchar(50));')
    cursor.execute('CREATE TABLE aplicativos(id int AUTO_INCREMENT PRIMARY KEY,nome	varchar(100),versao	varchar(10));')
    cursor.execute('ALTER TABLE chamados ADD CONSTRAINT fk_chamados_usuarios FOREIGN KEY (usuario_id) REFERENCES usuarios (id),ADD CONSTRAINT fk_chamados_tecnicos FOREIGN KEY (tecnico_id) REFERENCES tecnicos (id),ADD CONSTRAINT fk_chamados_equipamentos FOREIGN KEY (equipamento_id) REFERENCES equipamentos (id),ADD CONSTRAINT fk_chamados_aplicativos FOREIGN KEY (aplicativo_id) REFERENCES aplicativos (id)')
    cnx.close()
    
 
 
app = Flask(__name__)
#login_maneger = LoginManager()
#bcrypt = Bcrypt()
@app.route('/login',methods=['POST','GET'])
def pagina_login():
     return render_template("login.html")

@app.route('/')
def pagina_inicial():
     return render_template("paginainicial.html")
   
   
   
@app.route('/chamados')
def pagina_chamados():
  cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='chamadosti'  # Especificar o banco de dados
    )
  cursor = cnx.cursor()
  cursor.execute('SELECT * FROM chamados')
  chamados = cursor.fetchall()

  return render_template("chamados.html", chamados=chamados)
@app.route('/usuarios')
def pagina_usuarios():
  cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='chamadosti'  # Especificar o banco de dados
    )
  cursor = cnx.cursor()
  cursor.execute('SELECT * FROM usuarios')
  usuarios = cursor.fetchall()

  return render_template("usuarios.html", usuarios=usuarios)

@app.route('/cadastro', methods=["POST","GET"])
def cadastro():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    if request.method != 'POST':
        return render_template('cadastro.html', error='Método HTTP inválido.')
    if not nome:
        return render_template('cadastro.html', error='O nome é obrigatório.')
    if not email:
        return render_template('cadastro.html', error='O e-mail é obrigatório.')
    if not senha:
        return render_template('cadastro.html', error='A senha é obrigatória.')
    if len(senha) < 8:
        return render_template('cadastro.html', error='A senha deve ter pelo menos 8 caracteres.')  
   
    #senha = bcrypt.generate_password_hash(senha).decode('utf-8')
    # Verificando se o usuário já existe
    cnx = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='',
        database='chamadosti'
    )
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT COUNT(*)
        FROM usuarios
        WHERE email = %s;
    """, (email,))
    existe = cursor.fetchone()[0]
    cursor.close()
    cnx.close()

    if existe > 0:
        return render_template('cadastro.html', error='O usuário já existe.')
    else:
      try:
          cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='chamadosti'
          )
          cursor = cnx.cursor()
          

          sql = 'INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)'
          values = (nome, email, senha)

          cursor.execute(sql, list(values))
          cursor.close()
          cnx.commit()

          return redirect(url_for('pagina_inicial'))
      
      except mysql.connector.Error as e:
        return render_template('cadastro.html', error=str(e))  
    
    # Salvando os dados
@app.route('/excluir_usuario/<id>', methods=['GET', 'POST'])
def excluir_usuario(id):
    # Validar o ID
    if not id.isdigit():
        return render_template('excluir-usuario.html', error='ID inválido')
    # Executando a exclusão
    try:
        cnx = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='chamadosti'
        )
        cursor = cnx.cursor()
        cursor.execute("""
            DELETE FROM usuarios
            WHERE id = %s;
        """, (id,))
        cursor.close()
        cnx.commit()

        return redirect(url_for('pagina_usuarios'))
    except mysql.connector.Error as e:
        return render_template('excluir-usuario.html', error=str(e))
   
      
      
    

if __name__ == '__main__':
      app.run