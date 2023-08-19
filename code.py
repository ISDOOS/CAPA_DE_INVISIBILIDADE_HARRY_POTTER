#!/usr/bin/env python
# coding: utf-8

# In[8]:


import cv2
import time
import numpy as np
import ipywidgets as widgets
from IPython.display import display, clear_output

# Parâmetros ajustáveis
FRAME_SIZE = (640, 480)
FPS = 20
RECORDING_DURATION_SECONDS = 20
COUNTDOWN_SECONDS = 10

# Constantes de cor para detecção
COLORS = {
    'AMARELO': (np.array([20, 100, 100]), np.array([30, 255, 255])),
    'ROSA': (np.array([140, 100, 100]), np.array([160, 255, 255])),
    'VERMELHO': (np.array([0, 100, 100]), np.array([10, 255, 255]))
}

def detect_color(frame, color_name):
    lower_bound, upper_bound = COLORS[color_name]
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, np.ones((3, 3), np.uint8))
    return mask

def apply_effects(frame, background, mask):
    mask_inv = cv2.bitwise_not(mask)
    masked_frame = cv2.bitwise_and(frame, frame, mask=mask_inv)
    masked_background = cv2.bitwise_and(background, background, mask=mask)
    final_output = cv2.addWeighted(masked_frame, 1, masked_background, 1, 0)
    return final_output

# Preparação para escrever o vídeo de saída
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, FPS, FRAME_SIZE)

# Inicialização da captura da webcam
cap = cv2.VideoCapture(0)

# Interface gráfica
button_start = widgets.Button(description="Iniciar Gravação")
button_stop = widgets.Button(description="Parar Gravação")
color_selector = widgets.Dropdown(
    options=['AMARELO', 'ROSA', 'VERMELHO'],
    value='AMARELO',
    description='Escolha a Cor:'
)
output = widgets.Output()

# Exibir os elementos na interface
display(widgets.HBox([button_start, button_stop]), color_selector, output)

recording = False

def start_recording(b):
    global recording
    with output:
        print("Clique em 'Iniciar Gravação' novamente para iniciar a gravação em 10 segundos.")
        button_start.disabled = True
        button_stop.disabled = False
        color_name = color_selector.value
        time.sleep(COUNTDOWN_SECONDS)
        print(f"A gravação será iniciada em 5 segundos usando a cor {color_name}.")
        time.sleep(5)
        recording = True
        count = 0
        background = None
        for i in range(60):
            ret, background = cap.read()
            background = np.flip(background, axis=1)
        while recording and count < RECORDING_DURATION_SECONDS * FPS:
            ret, frame = cap.read()
            if not ret:
                break
            frame = np.flip(frame, axis=1)
            mask = detect_color(frame, color_name)
            final_output = apply_effects(frame, background, mask)
            out.write(final_output)
            cv2.imshow("Magic", final_output)
            cv2.waitKey(1)
            count += 1
        stop_recording(None)

def stop_recording(b):
    global recording
    recording = False
    button_start.disabled = False
    button_stop.disabled = True
    print("Gravação encerrada.")
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Configurar os botões para chamar as funções de início e parada de gravação
button_start.on_click(start_recording)
button_stop.on_click(stop_recording)


# In[ ]:




