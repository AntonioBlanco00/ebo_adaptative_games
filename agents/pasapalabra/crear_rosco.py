import csv
import json

# Nombre del archivo CSV
csv_file = 'partes_de_la_casa.csv'
# Nombre del archivo JSON de salida
json_file = 'partes_de_la_casa.json'

# Lista que almacenará las preguntas
preguntas = []

# Leer el archivo CSV y procesarlo
with open(csv_file, mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Crear una entrada para cada fila del CSV
        pregunta = {
            "letra": row["letra"],
            "definicion": row["definicion"],
            "respuesta": row["respuesta"]
        }
        preguntas.append(pregunta)

# Estructura final para el JSON
resultado = {
    "preguntas": preguntas
}

# Guardar el JSON
with open(json_file, mode='w', encoding='utf-8') as file:
    json.dump(resultado, file, indent=4, ensure_ascii=False)

print(f"Archivo JSON creado exitosamente: {json_file}")

