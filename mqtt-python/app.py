from flask import Flask, render_template
import paho.mqtt.subscribe as suscribir
import threading
import time
import os

app = Flask(__name__)

# Archivo para guardar los datos
arch = "LLegada.csv"

# Crear el archivo si no existe
if not os.path.exists(arch):
    with open(arch, "a") as archivo:
        print("Archivo no encontrado, creando...")
        archivo.write("Nombre,Matricula,Humedad,Temperatura,Fecha,Hora,\n")

# Variable global para almacenar los datos recibidos
datos_recibidos = []

# Función para manejar la recepción de datos MQTT
def recibir_datos():
    global datos_recibidos
    while True:
        try:
            # Suscribirse al tópico
            mensaje = suscribir.simple("iot", hostname='') #ingresa tu ip o dominio en el parametro hostname

            
            proceso = mensaje.payload.decode()  # Decodificar el mensaje recibido

            # Separar los datos usando el delimitador '@'
            array = proceso.split('@')

            fecha_actual = time.strftime("%Y-%m-%d")
            hora_actual = time.strftime("%H:%M:%S")

            with open(arch, "a") as archivo:
                archivo.write(f"{array[0]},{array[1]},{array[3]},{array[5]},{array[7]},{fecha_actual},{hora_actual},\n")

            datos_recibidos.append({
                "nombre": array[0],
                "matricula": array[1],
                "humedad": array[3],
                "temperatura": array[5],
                "nivel_agua": array[7],
                "fecha": fecha_actual,
                "hora": hora_actual
            })

            ''' Mantener solo los últimos 10 datos para evitar uso excesivo de memoria
            if len(datos_recibidos) > 10:
                datos_recibidos.pop(0)
            '''

            print("Datos guardados:", array, fecha_actual, hora_actual)

        except Exception as e:
            print("Error:", e)

# Ruta para mostrar los datos en el HTML
@app.route('/')
def home():
    return render_template('index.html', datos=datos_recibidos)

# Iniciar el hilo para recibir datos MQTT
hilo_mqtt = threading.Thread(target=recibir_datos)
hilo_mqtt.daemon = True
hilo_mqtt.start()

if __name__ == '__main__':
    app.run(debug=True)
