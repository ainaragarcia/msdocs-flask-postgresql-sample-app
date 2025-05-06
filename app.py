import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Crear la aplicación Flask
app = Flask(__name__)

# Configuración de la base de datos
db_host = os.getenv('AZURE_POSTGRESQL_HOST')
db_name = os.getenv('AZURE_POSTGRESQL_NAME')
db_user = os.getenv('AZURE_POSTGRESQL_USER')

# Acceder a la contraseña desde Azure Key Vault (si es necesario)
key_vault_url = "https://AlmacenClavesPapAinara.vault.azure.net/"
credential = DefaultAzureCredential()
client = SecretClient(vault_url=key_vault_url, credential=credential)

# Obtener la contraseña del secreto almacenado en Azure Key Vault
db_password = client.get_secret('AZURE_POSTGRESQL_PASSWORD').value

# Formar el URI de conexión a PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:5432/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desactivar el seguimiento de modificaciones para mejorar el rendimiento

# Crear la instancia de SQLAlchemy
db = SQLAlchemy(app)

# Definir un modelo de base de datos (ejemplo)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Ruta principal
@app.route('/')
def index():
    # Crear las tablas de la base de datos si no existen
    db.create_all()

    # Agregar un usuario de ejemplo
    new_user = User(username='john_doe', email='john@example.com')
    db.session.add(new_user)
    db.session.commit()

    return 'User added to database!'

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run(debug=True)
