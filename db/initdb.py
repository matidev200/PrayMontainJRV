import sqlite3
import os

# Conectarse a la base de datos (o crearla si no existe)
DATABASE_PATH = os.path.join(os.path.dirname(__file__), '../horarios.db')

conn = sqlite3.connect(DATABASE_PATH)
cursor = conn.cursor()

# Crear la tabla de horarios_disponibles si no existe
cursor.execute('''
    CREATE TABLE IF NOT EXISTS horarios_disponibles (
        dia_oracion TEXT,
        horario_disponible TEXT
    )
''')

# Crear los días de la semana
dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

# Crear los horarios disponibles (1 hora a 1 hora desde las 00:00)
horas = [f"{str(i).zfill(2)}:00 - {str((i+1)%24).zfill(2)}:00" for i in range(24)]

# Insertar los días y horarios en la tabla horarios_disponibles
for dia in dias_semana:
    for horario in horas:
        cursor.execute('INSERT INTO horarios_disponibles (dia_oracion, horario_disponible) VALUES (?, ?)', (dia, horario))

# Guardar los cambios y cerrar la conexión a la base de datos
conn.commit()

try:
    cursor.execute('''
        CREATE TABLE orador (
            id INTEGER PRIMARY KEY,
            nombre VARCHAR(50),
            telefono VARCHAR(15) CHECK(telefono GLOB '[0-9]*'), -- Nueva columna telefono con restricción de solo números
            dia_oracion VARCHAR(20),
            rango_horario_deseado TEXT,
            rango_horario TEXT,
            CONSTRAINT unique_orador UNIQUE (dia_oracion, rango_horario)
        )
    ''')
    conn.commit()
    print("Tabla orador creada correctamente.")
except sqlite3.Error as e:
    print(f"Error al crear la tabla orador: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
