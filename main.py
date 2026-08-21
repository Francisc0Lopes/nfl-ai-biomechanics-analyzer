import cv2
import mediapipe as mp
import math
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.signal import medfilt

parser = argparse.ArgumentParser(description="Analisador Biomecânico de Passes da NFL")
parser.add_argument("--input", type=str, required=True, help="Caminho para o ficheiro de vídeo")
parser.add_argument("--headless", action="store_true", help="Executar sem abrir a janela de vídeo")

args = parser.parse_args()

print("Caminho do mediapipe:", mp.__file__)
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calcular_angulo(a,b,c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radianos = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angulo = np.abs(radianos * 180.0 / np.pi)
    if angulo > 180.0:
        angulo = 360.0 - angulo
        
    return angulo
    
    
cap = cv2.VideoCapture(args.input)

if not cap.isOpened():
    print("Erro ao abrir o ficheiro")

pose = mp_pose.Pose()
angulo_anterior = None
historico_angulos= []


while cap.isOpened():
    ret, frame=cap.read()
    if not ret:
        break
    
    frame_redimensionado = cv2.resize(frame, (1280,720))
    frame_rgb = cv2.cvtColor(frame_redimensionado, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame_redimensionado, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark
        cotovelo = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        ombro = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        pulso = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        
        arm_angle= calcular_angulo(ombro, cotovelo, pulso)
        historico_angulos.append(arm_angle)
        print(arm_angle)

        posicao_texto = (int(cotovelo[0] * 1280), int(cotovelo[1] * 720))
        cv2.putText(frame_redimensionado, str(int(arm_angle)), 
                    posicao_texto, 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255,255,255), 3, cv2.LINE_AA)
    if not args.headless:
        cv2.imshow("Passe", frame_redimensionado)
    
    if cv2.waitKey(25) & 0xFF == ord("q"):
        break
    
cap.release()
cv2.destroyAllWindows()

historico_limpo = medfilt(historico_angulos, kernel_size=7)
velocidade_maxima = 0
for i in range(1, len(historico_limpo)):
    diferenca = abs(historico_limpo[i] - historico_limpo[i-1])
    velocidade_atual = diferenca * 30.0 # Multiplicar por 30 frames por segundo
    
    if velocidade_atual > velocidade_maxima:
        velocidade_maxima = velocidade_atual
print(f"Velocidade Máxima Real do Braço: {velocidade_maxima:.1f} graus/segundo")

        

angulo_inicial= historico_limpo[0]
angulo_lancamento =max(historico_limpo)
angulo_final= historico_limpo[-1]
print(f"Preparação: {angulo_inicial:.1f}º | Pico (Lançamento): {angulo_lancamento:.1f}º | Follow-through: {angulo_final:.1f}º")
plt.plot(historico_angulos, label="Dados Brutos (Com Ruído)", alpha=0.5, linestyle='--')
plt.plot(historico_limpo, label="Sinal Limpo (Para a IA)", color='red', linewidth=2)
plt.legend()
plt.show()


print("\n--- ANÁLISE DA JOGADA ---")

if angulo_lancamento > 165:
    print("Classificação: PASSE LONGO (Deep Pass)")
    print("Motivo: Máxima extensão do braço detetada.")
elif 130 <= angulo_lancamento <= 165:
    print("Classificação: PASSE CURTO / BULLET (Slant/Screen)")
    print("Motivo: Extensão intermédia, foco na rapidez do lançamento.")
else:
    print("Classificação: MOVIMENTO INVÁLIDO / PUMP FAKE")
    print("Motivo: O braço não atingiu extensão suficiente para um passe.")