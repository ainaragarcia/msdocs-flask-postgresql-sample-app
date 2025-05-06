import os
from datetime import datetime
from flask import Flask, redirect, render_template, request, send_from_directory, url_for, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from models import Imagen, Restaurant, Review  # Importa todo de models al inicio

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# Configuración por entorno
if 'WEBSITE_HOSTNAME' not in os.environ:
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Inicializar DB y migraciones
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Rutas principales
@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    restaurants = Restaurant.query.all()
    return render_template('index.html', restaurants=restaurants)

@app.route('/<int:id>', methods=['GET'])
def details(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    reviews = Review.query.filter_by(restaurant=id).all()
    return render_template('details.html', restaurant=restaurant, reviews=reviews)

@app.route('/create', methods=['GET'])
def create_restaurant():
    print('Request for add restaurant page received')
    return render_template('create_restaurant.html')

@app.route('/add', methods=['POST'])
@csrf.exempt
def add_restaurant():
    try:
        name = request.values.get('restaurant_name')
        street_address = request.values.get('street_address')
        description = request.values.get('description')
    except KeyError:
        return render_template('add_restaurant.html', {
            'error_message': "You must include a restaurant name, address, and description",
        })
    else:
        restaurant = Restaurant(
            name=name,
            street_address=street_address,
            description=description
        )
        db.session.add(restaurant)
        db.session.commit()
        return redirect(url_for('details', id=restaurant.id))

@app.route('/review/<int:id>', methods=['POST'])
@csrf.exempt
def add_review(id):
    try:
        user_name = request.values.get('user_name')
        rating = int(request.values.get('rating'))
        review_text = request.values.get('review_text')
    except (KeyError, ValueError):
        return render_template('add_review.html', {
            'error_message': "Error adding review",
        })
    else:
        review = Review(
            restaurant=id,
            user_name=user_name,
            rating=rating,
            review_text=review_text,
            review_date=datetime.now()
        )
        db.session.add(review)
        db.session.commit()
        return redirect(url_for('details', id=id))

@app.context_processor
def utility_processor():
    def star_rating(id):
        reviews = Review.query.filter_by(restaurant=id).all()
        ratings = [r.rating for r in reviews]
        review_count = len(ratings)
        avg_rating = sum(ratings) / review_count if ratings else 0
        stars_percent = round((avg_rating / 5.0) * 100) if review_count > 0 else 0
        return {'avg_rating': avg_rating, 'review_count': review_count, 'stars_percent': stars_percent}

    return dict(star_rating=star_rating)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# ---------------------------
# Rutas para manejo de imágenes
# ---------------------------

@app.route('/api/upload', methods=['POST'])
@csrf.exempt
def upload_imagen():
    data = request.get_json()
    try:
        imagen = Imagen(
            username=data['username'],
            filename=data['filename'],
            date=datetime.fromisoformat(data['date']),
            rojo=data['colorStats']['rojo'],
            verde=data['colorStats']['verde'],
            azul=data['colorStats']['azul']
        )
        db.session.add(imagen)
        db.session.commit()
        return {"status": "ok"}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 400

@app.route('/imagenes', methods=['GET'])
def mostrar_imagenes():
    imagenes = Imagen.query.all()
    return render_template('imagenes.html', imagenes=imagenes)

# ---------------------------

if __name__ == '__main__':
    app.run()
