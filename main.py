import cv2
import mediapipe as mp
import argparse
import os
import numpy as np

# Importar a tua nova biblioteca interna!
from analysis.processor import calcular_angulo, limpar_sinal, calcular_velocidade_maxima, classificar_passe
from analysis.visualizer import desenhar_telemetria, desenhar_angulo_cotovelo

parser = argparse.ArgumentParser(description="Analisador Biomecânico de Passes da NFL")
parser.add_argument("--input", type=str, required=True, help="Caminho para o ficheiro de vídeo")
parser.add_argument("--headless", action="store_true", help="Executar sem abrir a janela de vídeo")
args = parser.parse_args()

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

cap = cv2.VideoCapture(args.input)
if not cap.isOpened():
    print("Erro ao abrir o ficheiro de vídeo.")
    exit()

# Configurar VideoWriter para 1280x720 (o tamanho exato onde desenhas o esqueleto)
fps = cap.get(cv2.CAP_PROP_FPS)
if fps == 0 or fps is None: fps = 30.0
os.makedirs('output', exist_ok=True)
fourcc = cv2.VideoWriter_fourcc(*'mp4v') 
out = cv2.VideoWriter('output/passe_anotado.mp4', fourcc, fps, (1280, 720))

angulo_anterior = None
historico_angulos = []

print(f"A processar vídeo: {args.input}...")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Prepara a imagem
    frame_redimensionado = cv2.resize(frame, (1280, 720))
    frame_rgb = cv2.cvtColor(frame_redimensionado, cv2.COLOR_BGR2RGB)
    results = pose.process(frame_rgb)
    
    velocidade_atual = 0
    
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame_redimensionado, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
        landmarks = results.pose_landmarks.landmark
        
        cotovelo = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
        ombro = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        pulso = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]
        
        # 1. Usa o teu Processor
        angulo = calcular_angulo(ombro, cotovelo, pulso)
        historico_angulos.append(angulo)
        
        if angulo_anterior is not None:
            velocidade_atual = abs(angulo - angulo_anterior) * fps
        angulo_anterior = angulo
        
        # 2. Usa o teu Visualizer
        frame_redimensionado = desenhar_telemetria(frame_redimensionado, angulo, velocidade_atual)
        frame_redimensionado = desenhar_angulo_cotovelo(frame_redimensionado, cotovelo, angulo)

    # 3. Gravar o frame JÁ com os desenhos!
    out.write(frame_redimensionado)

    if not args.headless:
        cv2.imshow("Passe", frame_redimensionado)
    
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

# --- ANÁLISE PÓS-VÍDEO (A Lógica pura) ---
print("Processamento do vídeo concluído. A gerar análise final...")

# Limpar o sinal e guardar
historico_limpo = limpar_sinal(historico_angulos, tamanho_janela=7)
os.makedirs('data', exist_ok=True)
np.save('data/historico_limpo.npy', historico_limpo)

# Calcular métricas
velocidade_maxima = calcular_velocidade_maxima(historico_limpo, fps)
angulo_inicial = historico_limpo[0]
angulo_lancamento = max(historico_limpo)
angulo_final = historico_limpo[-1]

print(f"\nVelocidade Máxima Real do Braço: {velocidade_maxima:.1f} graus/segundo")
print(f"Cinemática -> Preparação: {angulo_inicial:.1f}º | Pico: {angulo_lancamento:.1f}º | Follow: {angulo_final:.1f}º")

print("\n--- CLASSIFICAÇÃO DA JOGADA ---")
classificacao, motivo = classificar_passe(angulo_lancamento)
print(f"Classificação: {classificacao}")
print(f"Motivo: {motivo}")