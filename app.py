from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# Ruta para mostrar un mensaje de bienvenida
@app.route('/')
def index():
    return "Bienvenido a la API de Carga de Archivos"

# Ruta para manejar la carga de archivos y datos en formato JSON
@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        # Guardar el archivo en el servidor local
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Obtener datos JSON adicionales
        data = request.get_json()
        usuario = data.get('username', '')
        nombre_archivo = data.get('filename', file.filename)
        fecha = data.get('date', datetime.now().isoformat())
        color_stats = data.get('colorStats', {})

        rojo = color_stats.get('rojo', 0)
        verde = color_stats.get('verde', 0)
        azul = color_stats.get('azul', 0)

        # Simulamos el procesamiento del archivo (puedes agregar más lógica aquí)
        resultado = procesar_archivo(file_path)

        # Responder con un mensaje de éxito
        return jsonify({
            "mensaje": f"Archivo {nombre_archivo} subido exitosamente",
            "usuario": usuario,
            "fecha": fecha,
            "colorStats": {
                "rojo": rojo,
                "verde": verde,
                "azul": azul
            },
            "procesamiento": resultado
        }), 200

# Función que simula el procesamiento del archivo
def procesar_archivo(ruta):
    try:
        with open(ruta, 'r', encoding='utf-8', errors='ignore') as f:
            lineas = f.readlines()
        return f"{len(lineas)} líneas encontradas"
    except Exception as e:
        return f"Error procesando el archivo: {str(e)}"

if __name__ == '__main__':
    # Crear directorio de uploads si no existe
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    app.run(debug=True)
