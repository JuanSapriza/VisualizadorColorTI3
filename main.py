# Lectura del puerto serial basado en: https://maker.pro/pic/tutorial/introduction-to-python-serial-ports

import serial
from time import sleep
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv
import re
from math import floor
from time import time

plt.rcParams["figure.figsize"] = [6, 4]
fig, (raw, boosted) = plt.subplots(1,2)
imgRaw = raw.imshow([[[0,0,0]]])
imgBoosted = boosted.imshow([[[0,0,0]]])
plt.ion()

raw.set_title("Sensado")
raw.axis('off')

boosted.set_title("Sat.& Valor amplificado")
boosted.axis('off')

puerto = "COM16"
br = 9600
master = False

startTime = time()
samplesText = fig.text(0.5, 0.1, "Muestras: 0", ha='center', va='center')
timeText = fig.text(0.5, 0.04, "Tiempo transcurrido: 0 s", ha='center', va='center')

while 1:

    while 1:
        try: # Intenta abrir el puerto serial indicado en <<puerto>> con el baudrate <<br>>
            s = serial.Serial(port = puerto , baudrate = br, bytesize = 8, timeout = 2, stopbits=serial.STOPBITS_ONE)
            print("Puerto Serial "+puerto + " abierto exitosamente!" )
            samples = 0
            break
        except serial.serialutil.SerialException: # Mientras no haya nada conectado al puerto envía un mensaje y espera un tiempo para volver a intentar
            print("No hay nada en el puerto "+puerto+"!!")
            sleep(3)

    while 1:
        try:
           # Espera a que haya algo en el puerto serial
            if(s.in_waiting > 0):
                receivedString = s.readline()
                print(receivedString)
                try:
                    # Del string que llega por el puerto serial, se queda con los números
                    valueStrings = re.findall("\d*\.?\d+",str(receivedString))
                    # Pasa esos números a enteros
                    values = [floor(float(value)) for value in valueStrings]

                    # Los primeros tres son los valores RGB, los siguientes tres los valores HSL
                    rgb = values[0:3]
                    hsl = values[3:6]

                    # Muestra la gráfica en su versión sin amplificar
                    raw.imshow([[rgb]])

                    # Toma el RGB y lo normaliza (0-1)
                    rgb = [[value / 255 for value in rgb]]
                    # Lo pasa a HSV
                    hsv = rgb_to_hsv(rgb)

                    if hsl[2] >= 80:   # ES BLANCO
                        print("BLANCO")
                        hsv[0][1] = 0
                        hsv[0][2] = 1
                    elif hsl[2] < 10:  # ES NEGRO
                        hsv[0][2] = 0
                        '''
                        elif hsl[1] < 10:  # ES GRIS
                            hsv[0][1] = 0
                            hsv[0][2] = 0.5
                        '''
                    else:               # ES UN COLOR
                        # Aumento al máximo la saturación y el valor
                        hsv[0][1] = 1
                        hsv[0][2] = 1

                    # Lo devuelve a RGB para ser representado
                    rgb = hsv_to_rgb(hsv)[0]

                    # Muestra la versión amplificada
                    boosted.imshow([[rgb]])

                    # AUmenta la cantidad de muestras que se han tomado
                    samples = samples +1
                    samplesText.set_text("Muestras: " + str(samples))

                    # Muestra el tiempo de ejecución
                    currentTime = time() - startTime
                    timeText.set_text("Tiempo transcurrido: " + str(floor(currentTime)) + " s")

                    # Actualziación de la gráfica
                    plt.pause(0.2)
                    plt.draw()
                except:
                    print("Error al detectar color")

                if( master ):
                    sleep(0.1)
                    s.write('h'.encode('utf-8'))

        except serial.serialutil.SerialException: # Si el puerto se desconecta envía un mensaje y vuelve al comienzo a intentar registrarse.
            print("Error de conexión")
            break

