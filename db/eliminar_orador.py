import sqlite3
import sys
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), '../horarios.db')

def eliminar_orador(nombre):
    db = sqlite3.connect(DATABASE_PATH)
    cursor = db.cursor()
    try:
        # Obtener el día y el rango horario del orador antes de eliminarlo
        cursor.execute('SELECT dia_oracion, rango_horario FROM orador WHERE nombre = ?', (nombre,))
        dia_oracion, rango_horario = cursor.fetchone()

        # Eliminar al orador
        cursor.execute('DELETE FROM orador WHERE nombre = ?', (nombre,))
        db.commit()

        # Restaurar el horario en la tabla de horarios disponibles
        cursor.execute('INSERT INTO horarios_disponibles (dia_oracion, horario_disponible) VALUES (?, ?)', (dia_oracion, rango_horario))
        db.commit()
    
    except sqlite3.Error as e:
        print(f"Error al eliminar el orador: {e}")
        db.rollback()
    finally:
        cursor.close()
        
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python eliminar_orador.py <nombre>")
    else:
        nombre = sys.argv[1]
        eliminar_orador(nombre)
