from flask import Flask, render_template, request, jsonify
# Importa aquí tus módulos de práctica_bazilio si es necesario
# from practica_bazilio.tu_archivo import tu_funcion_analizadora

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    datos = request.json.get('texto', '')
    # Aquí procesas el texto usando tus parsers/lexers de ANTLR
    resultado = f"Procesado correctamente: {datos}"
    return jsonify({'resultado': resultado})

if __name__ == '__main__':
    app.run(debug=True)