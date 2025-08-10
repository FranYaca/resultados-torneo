import sqlite3
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
DATABASE = 'torneo.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS partidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            equipo_a_nombre TEXT NOT NULL,
            equipo_a_puntos INTEGER NOT NULL DEFAULT 0,
            equipo_b_nombre TEXT NOT NULL,
            equipo_b_puntos INTEGER NOT NULL DEFAULT 0,
            estado TEXT NOT NULL DEFAULT 'no iniciado'
        );
    ''')
    conn.commit()
    conn.close()

# Crea la tabla al iniciar la aplicación
create_table()

@app.route('/')
def index():
    conn = get_db_connection()
    partidos_db = conn.execute('SELECT * FROM partidos').fetchall()
    conn.close()
    
    # Convertir los resultados de la base de datos a un formato que el HTML pueda usar
    partidos = []
    for p in partidos_db:
        partidos.append({
            'id': p['id'],
            'equipo_a': {'nombre': p['equipo_a_nombre'], 'puntos': p['equipo_a_puntos']},
            'equipo_b': {'nombre': p['equipo_b_nombre'], 'puntos': p['equipo_b_puntos']},
            'estado': p['estado']
        })

    return render_template('index.html', partidos=partidos)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = get_db_connection()
    if request.method == 'POST':
        match_id = request.form.get('id', type=int)
        puntos_a = request.form.get('puntos_a', type=int)
        puntos_b = request.form.get('puntos_b', type=int)
        estado = request.form.get('estado')

        if match_id:
            conn.execute('''
                UPDATE partidos SET 
                equipo_a_puntos = ?, 
                equipo_b_puntos = ?, 
                estado = ? 
                WHERE id = ?
            ''', (puntos_a, puntos_b, estado, match_id))
            conn.commit()
    
    partidos_db = conn.execute('SELECT * FROM partidos').fetchall()
    conn.close()
    
    # Convertir los resultados de la base de datos a un formato que el HTML pueda usar
    partidos = []
    for p in partidos_db:
        partidos.append({
            'id': p['id'],
            'equipo_a': {'nombre': p['equipo_a_nombre'], 'puntos': p['equipo_a_puntos']},
            'equipo_b': {'nombre': p['equipo_b_nombre'], 'puntos': p['equipo_b_puntos']},
            'estado': p['estado']
        })

    return render_template('admin.html', partidos=partidos)

@app.route('/add_match', methods=['POST'])
def add_match():
    conn = get_db_connection()
    equipo_a = request.form.get('nombre_equipo_a')
    equipo_b = request.form.get('nombre_equipo_b')
    
    conn.execute('''
        INSERT INTO partidos (equipo_a_nombre, equipo_b_nombre) VALUES (?, ?)
    ''', (equipo_a, equipo_b))
    conn.commit()
    conn.close()

    return redirect(url_for('admin'))

@app.route('/resultados_json')
def resultados_json():
    conn = get_db_connection()
    partidos_db = conn.execute('SELECT * FROM partidos').fetchall()
    conn.close()
    
    partidos = []
    for p in partidos_db:
        partidos.append({
            'id': p['id'],
            'equipo_a': {'nombre': p['equipo_a_nombre'], 'puntos': p['equipo_a_puntos']},
            'equipo_b': {'nombre': p['equipo_b_nombre'], 'puntos': p['equipo_b_puntos']},
            'estado': p['estado']
        })
    
    return jsonify(partidos)
@app.route('/delete_match/<int:match_id>', methods=['POST'])
def delete_match(match_id):
    """Elimina un partido de la base de datos."""
    conn = get_db_connection()
    conn.execute('DELETE FROM partidos WHERE id = ?', (match_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)