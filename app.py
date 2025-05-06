import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, send_from_directory, url_for, jsonify
from extensions import db, migrate  # Importa db y migrate desde extensions
from flask_wtf.csrf import CSRFProtect

# Creación de la aplicación Flask
app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# Cargar configuración basada en el entorno
if 'WEBSITE_HOSTNAME' not in os.environ:
    # Desarrollo local
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # Producción
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

# Configuración de la base de datos
app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Inicializar db con la app
db.init_app(app)

# Inicializar las migraciones
migrate.init_app(app, db)

# Importar los modelos después de la inicialización de db para evitar problemas de importación circular
from models import Restaurant, Review, Imagen

# Ruta de inicio
@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

# Ruta para los detalles de un restaurante
@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Restaurant.query.where(Restaurant.id == id).first()
    reviews = Review.query.where(Review.restaurant == id)
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

# Ruta para crear un restaurante
@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

# Ruta para agregar un restaurante a la base de datos
@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
    except (KeyError):
        return render_template('add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant()
        restaurant.name = name
        restaurant.street_address = street_address
        restaurant.description = description
        db.session.add(restaurant)
        db.session.commit()
        return redirect(url_for('details', id=restaurant.id))

# Ruta para agregar una reseña a un restaurante
@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        user_name = request.values.get('user_name')
        rating = request.values.get('rating')
        review_text = request.values.get('review_text')
    except (KeyError):
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review()
        review.restaurant = id
        review.review_date = datetime.now()
        review.user_name = user_name
        review.rating = int(rating)
        review.review_text = review_text
        db.session.add(review)
        db.session.commit()
    return redirect(url_for('details', id=id))

# Contexto para calcular la calificación promedio de un restaurante
@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = Review.query.where(Review.restaurant == id)

        ratings = []
        review_count = 0
        for review in reviews:
            ratings += [review.rating]
            review_count += 1

        avg_rating = sum(ratings) / len(ratings) if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

# Ruta para el favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Ruta para subir los datos de la imagen al Cloud
@app.route('/api/upload', methods=['POST'])
@csrf.exempt
def api_upload():
    data = request.get_json()

    if not data:
        return jsonify({"error": "No se recibió ningún JSON"}), 400

    try:
        # Crear un objeto Imagen basado en los datos recibidos
        imagen = Imagen(
            username=data["username"],
            filename=data["filename"],
            date=datetime.fromisoformat(data["date"]),
            rojo=data["colorStats"]["rojo"],
            verde=data["colorStats"]["verde"],
            azul=data["colorStats"]["azul"]
        )
        db.session.add(imagen)
        db.session.commit()
        return jsonify({"status": "ok", "mensaje": "Datos guardados correctamente"}), 200
    
    except Exception as e:
        print("ERROR en api_upload:", repr(e))  # Mostrar el error real en los logs de Azure
        return jsonify({"status": "error", "mensaje": "No se pudo guardar"}), 500

# Ruta para ver todas las imágenes subidas
@app.route('/imagenes', methods=['GET'])
def ver_imagenes():
    imagenes = Imagen.query.order_by(Imagen.date.desc()).all()
    print(imagenes)  # Verifica si las imágenes se están recuperando correctamente
    return render_template("imagenes.html", imagenes=imagenes)

# Configuración para correr la aplicación
application = app

if __name__ == '__main__':  # Corregir el nombre de la condición para ejecutar la app
    app.run(host='0.0.0.0', port=5000)  # Usa el puerto 5000, ya que Azure espera este puerto



