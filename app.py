from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data-dev.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JSON_SORT_KEYS"] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    idade = db.Column(db.Integer, default=0)
    
    def json(self):
        user_json = {'id': self.id,
                     'name': self.name,
                     'email': self.email,
                     'idade': self.idade}
        return user_json


@app.route('/users/', methods=['POST'])
def create():

    data = request.json
    name = data.get('name')
    email = data.get('email')
    idade = data.get('idade')
    
    if not name or not email:
        return {'error': 'Dados insuficientes'}, 400

    if (User.query.filter(User.email == email).count()) > 0:
      return {'error': 'Email já existente'}, 409
      # Aqui o erro é 409 pois ele é de conflito com o status atual. Como atualmente já existe
      # o email fornecido, então o erro deve ser o 409

      # - - - - I M P O R T A N T E - - - -  #
      # Infelizmente não consegui verificar se o email já havia sido digitado usando o PATCH ou PUT. Usei o mesmo código acima, mas
      # não deu certo

    user = User(name=name, email=email, idade=idade)

    db.session.add(user)
    db.session.commit()

    return user.json(), 201
    # o 201 é para quando um novo recurso é criado de forma bem sucedida


@app.route('/users/', methods=['GET'])
def index():
    data = request.args
    idade = data.get('idade')  

    if not idade:  
        users = User.query.all()  
    else:
        idade = idade.split('-')
        if len(idade) == 1:
            users = User.query.filter_by(idade=idade[0])
        else:
            users = User.query.filter(
                db.and_(User.idade >= idade[0], User.idade <= idade[1]))

    return jsonify([user.json() for user in users]), 200
    # É 200 porque foi uma ação bem sucedida, sem especialidade


@app.route('/users/<int:id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def user_detail(id):
    if request.method == 'GET': #----- USANDO O GET
        user = User.query.get_or_404(id)
        return user.json(), 200
        # É 200 porque foi uma ação bem sucedida, sem especialidade
    
    if request.method == 'PUT': # -----USANDO O PUT
      user = User.query.get_or_404(id)
      data = request.json

      if not data.get('name') or not data.get('email') or not data.get('idade'): # Verifica se algum dos campos enviados é nullo
        return {'error': 'Dados insuficientes'}, 400
        # É 400 pois o servidor não entendeu a requisição, é uma sintaxe inválida. O usuário deveria informar nome, email e idade. Como um deles
        #não foi informado, é um erro de sintaxe
      
      else: # Se nenhum deles for nulo, cada variável recebe seu valor
        user.name = data.get('name')
        user.email = data.get('email')
        user.idade = data.get('idade')

      db.session.commit() # E o banco de dados é atualizado
      return user.json(), 200
      

    if request.method == 'PATCH': #-----------PATCH
      user = User.query.get_or_404(id)
      data = request.json

      if not data.get('name') and not data.get('email') and not data.get('idade'):
        return {'error': 'Dados insuficientes'}, 400

          #Aqui verifica se um dos campos é nulo ou não
          #Caso algum campo seja nulo, o que está dentro de um dos ifs não será executado
          #Logo, o valor recebido não será substituído
      
      else:
        if data.get('name'):
          user.name = data.get('name')
        if data.get('email'):
          user.email = data.get('email')
        if data.get('idade'):
          user.idade = data.get('idade')

      db.session.commit() 
      return user.json(), 200
    
    if request.method == 'DELETE':
      #Na variável user fica armazenado o Usuário com o id fornecido. Se for fornecido um id inexistente, user deve ficar com valor nulo
      user = User.query.get_or_404(id)

      #Se user não possuir valor nulo, o usuário é apagado
      if user:
        User.query.filter(User.id == id).delete()
        db.session.commit()
        return 'Usuario apagado', 200
      else:
        return 'Usuario não encontrado', 404

      


if __name__ == '__main__':
    app.run(debug=True)