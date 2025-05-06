import os
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
from extensions import db, migrate  # Importa las extensiones de base de datos y migraciones

# Configuración de la aplicación
app = Flask(__name__)

# Configuración de la base de datos y carpeta de uploads
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://usuario:contraseña@localhost:5432/tu_base_de_datos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Carpeta donde se guardarán las imágenes subidas
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png', 'gif'}  # Extensiones permitidas para las imágenes

# Inicialización de las extensiones
db.init_app(app)
migrate.init_app(app, db)

# Importa el modelo de la imagen
from models import Imagen  # Asegúrate de que el archivo `models.py` contiene la clase Imagen

# Función para verificar las extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    # Consulta todas las imágenes de la base de datos
    imagenes = Imagen.query.all()
    return render_template('Imagenes.html', imagenes=imagenes)

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Verifica si la solicitud contiene el archivo
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']

        if file.filename == '':
            return 'No selected file', 400
        
        if file and allowed_file(file.filename):
            # Guardar el archivo en la carpeta de uploads
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Obtén los datos JSON del formulario
            username = request.form['username']
            rojo = int(request.form['rojo'])
            verde = int(request.form['verde'])
            azul = int(request.form['azul'])
            date = datetime.utcnow()

            # Guardar la información en la base de datos
            nueva_imagen = Imagen(
                username=username,
                filename=filename,
                date=date,
                rojo=rojo,
                verde=verde,
                azul=azul
            )
            db.session.add(nueva_imagen)
            db.session.commit()

            return redirect(url_for('index'))  # Redirige al index para ver la imagen subida

    return render_template('upload.html')  # Si es GET, muestra el formulario de carga

if __name__ == '__main__':
    app.run(debug=True)
