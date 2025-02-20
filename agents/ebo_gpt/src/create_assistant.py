# Para crear un asistente al que acceder despues por su ID. Almacena el ID del asistente en un .txt para acceder a el desde otros codigos.

import openai
from dotenv import find_dotenv, load_dotenv

load_dotenv()

client = openai.OpenAI()

model = "gpt-4-1106-preview" # gpt-4-1106-preview // gpt-3.5-turbo // gpt-3.5-turbo-16k no se puede con pdfs

### Creación del asistente ####
    # CUIDADO CON BETA, cuando deje de estar en beta cambiará.
EBO_assistant = client.beta.assistants.create(
    name="Colegios",
    instructions="""Eres EBO, un robot simpático y parlanchín con un tono amigable, lleno de energía y curiosidad. EBO está diseñado para interactuar con las personas de manera cálida, respetuosa y con un toque de humor. Tu misión es hacer que la persona se divierta mientras interactúa contigo y crear una conversación amena.
    Ahora mismo te encuentras en una clase de primaria con niños encantandos de conocerte. Te van a ir haciendo distintas preguntas y tu debes contestar a todas.
    Si te preguntan cosas de cultura o matemáticas, responde correctamente, eres un robot muy listo.
    Si te preguntan por tus gustos inventate cualquier cosa, aunque puedes tener en cuenta los siguientes gustos:
        Edad: 4 años
        Amigos: Alexa
        Comida favorita: hamburguesa
        Cantante favorito: Aitana
        Serie favorita: Patrulla Canina
    """,
    model=model
)
## Obtener el ID del asistente
assistant_id = EBO_assistant.id
print("Creado asistente con ID::: ", assistant_id)  #ID del asistente

def clean_empty_lines(filename='assistants.txt'):
    with open(filename, 'r') as file:
        lines = file.readlines()  # Leer todas las líneas del archivo

    # Filtrar las líneas vacías
    cleaned_lines = [line for line in lines if line.strip()]

    # Escribir las líneas limpiadas de vuelta en el archivo
    with open(filename, 'w') as file:
        file.writelines(cleaned_lines)

# Guardar el nombre y el ID en un archivo de texto
def save_assistant_info(name, assistant_id, filename='assistants.txt'):
    # Sustituir los espacios por barras bajas en el nombre
    name_with_underscores = name.replace(" ", "_")

    # Guardar en el archivo .txt con separación por punto y coma
    with open(filename, 'a') as file:
        file.write("\n")  # Añadir una línea vacía antes de escribir
        file.write(f"{name_with_underscores};{assistant_id}\n")  # Guardar el nombre con el ID

    clean_empty_lines()

# Guardar la información del asistente
save_assistant_info(EBO_assistant.name, assistant_id)
print("ID guardado en assistants.txt")