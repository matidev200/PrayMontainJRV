from flask import Flask, render_template, request, g, jsonify
import sqlite3
from configparser import ConfigParser

app = Flask(__name__)
config = ConfigParser()
config.read('config.conf')
app.static_folder = 'static'
app.config['SECRET_KEY'] = config.get('flask', 'SECRET_KEY')
app.config['DEBUG'] = config.getboolean('flask', 'DEBUG')


class OradorError(Exception):
    pass
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(config.get('flask', 'DB_URL'))
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()
        
@app.route('/dias/', methods=['GET'])
def get_dias_disponibles():
    db = get_db()
    cursor = db.execute('SELECT DISTINCT dia_oracion FROM horarios_disponibles')
    dias_disponibles =  [row['dia_oracion'] for row in cursor.fetchall()]

    return jsonify(dias_disponibles)

@app.route('/horarios/<dia>/', methods=['GET'])
def get_horarios_disponibles(dia):
    db = get_db()
    cursor = db.execute('SELECT horario_disponible FROM horarios_disponibles WHERE dia_oracion = ?', (dia,))
    horarios =  [row['horario_disponible'] for row in cursor.fetchall()]
    return jsonify(horarios)

def guardar_orador(nombre,telefono, dia_oracion, rango_horario):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('INSERT INTO orador (nombre, telefono , dia_oracion, rango_horario) VALUES (?, ?, ?, ?)',
                       (nombre, telefono,dia_oracion,rango_horario)) 
        db.commit()

        eliminar_horario(dia_oracion, rango_horario)
    
    except sqlite3.Error as e:
        print(f"Error al guardar el orador: {e}")
        db.rollback()
        raise OradorError("Error al guardar el orador en la base de datos")
    finally:
        cursor.close()


def eliminar_horario(dia_oracion, rango_horario):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('DELETE FROM horarios_disponibles WHERE dia_oracion = ? AND horario_disponible = ?', (dia_oracion, rango_horario))
        db.commit()
    except sqlite3.Error as e:
        print(f"Error al eliminar el horario: {e}")
        db.rollback()
    finally:
        cursor.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            nombre = request.form['nombre']
            telefono = request.form['telefono']
            dia_oracion = request.form['dia_oracion']
            rango_horario = request.form['rango_horario']
            guardar_orador(nombre, telefono,dia_oracion, rango_horario)
            mensaje = 'aprobado'
            return render_template('index.html', mensaje = mensaje)
        except Exception as e:

            if str(e) == 'Error al guardar el orador en la base de datos':
                mensaje = 'error'
                return render_template('index.html', mensaje = mensaje)
            
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
