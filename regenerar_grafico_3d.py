"""
Regenera o gráfico do ângulo do braço, agora usando o ângulo 3D
(x, y, z) em vez de só 2D, e corre a verificação de sanidade antes
de gerar o gráfico.

Este script assume que já tens, algures no teu main.py, o código que:
  1. Lê o vídeo frame a frame
  2. Corre o MediaPipe Pose em cada frame
  3. Guarda os landmarks do ombro, cotovelo e pulso por frame

Se ainda não tiveres essa lista de landmarks guardada por frame,
adapta a função `extrair_landmarks_do_video()` abaixo ao teu código
real do main.py — ou envia-me o teu main.py e eu faço a integração
diretamente.
"""

import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt

from angle_3d import calcular_angulo_3d, calcular_angulo_2d
from sanity_check import relatorio_sanidade


mp_pose = mp.solutions.pose


def extrair_landmarks_do_video(video_path: str):
    """
    Lê o vídeo e devolve, por frame, os landmarks do ombro, cotovelo
    e pulso direito (ajusta o lado se o teu QB lançar com a esquerda).

    Ajusta os índices de landmark conforme o que já usas no teu main.py
    (MediaPipe usa RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST por default
    aqui — troca para LEFT_* se for o caso).
    """
    cap = cv2.VideoCapture(video_path)
    landmarks_por_frame = []

    with mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resultado = pose.process(frame_rgb)

            if resultado.pose_landmarks:
                lm = resultado.pose_landmarks.landmark
                ombro = lm[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                cotovelo = lm[mp_pose.PoseLandmark.RIGHT_ELBOW]
                pulso = lm[mp_pose.PoseLandmark.RIGHT_WRIST]
                landmarks_por_frame.append((ombro, cotovelo, pulso))
            else:
                # sem deteção neste frame — repete o último válido
                # para não partir a série (ajusta se preferires outra estratégia)
                if landmarks_por_frame:
                    landmarks_por_frame.append(landmarks_por_frame[-1])

    cap.release()
    return landmarks_por_frame


def main():
    video_path = "passe.mp4"

    print("A extrair landmarks do vídeo...")
    landmarks_por_frame = extrair_landmarks_do_video(video_path)
    print(f"Total de frames processados: {len(landmarks_por_frame)}")

    # calcular ambas as versões, para comparares lado a lado
    angulos_2d = [calcular_angulo_2d(o, c, p) for o, c, p in landmarks_por_frame]
    angulos_3d = [calcular_angulo_3d(o, c, p) for o, c, p in landmarks_por_frame]

    # filtro de mediana, igual ao que já tinhas
    angulos_2d_filtrados = medfilt(angulos_2d, kernel_size=5)
    angulos_3d_filtrados = medfilt(angulos_3d, kernel_size=5)

    # verificação de sanidade em ambas, para veres a diferença
    print("\n=== Ângulo 2D (original) ===")
    relatorio_sanidade(angulos_2d_filtrados, limite_graus_por_frame=25, nome_video="passe.mp4 (2D)")

    print("\n=== Ângulo 3D (corrigido) ===")
    relatorio_sanidade(angulos_3d_filtrados, limite_graus_por_frame=25, nome_video="passe.mp4 (3D)")

    # gráfico comparativo lado a lado
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

    ax1.plot(angulos_2d_filtrados, linewidth=2)
    ax1.set_title("Ângulo do cotovelo — 2D (x, y)")
    ax1.set_xlabel("Frame")
    ax1.set_ylabel("Ângulo (graus)")
    ax1.grid(alpha=0.3)

    ax2.plot(angulos_3d_filtrados, linewidth=2, color="darkorange")
    ax2.set_title("Ângulo do cotovelo — 3D (x, y, z)")
    ax2.set_xlabel("Frame")
    ax2.grid(alpha=0.3)

    plt.suptitle("Comparação: correção de foreshortening com eixo Z")
    plt.tight_layout()
    plt.savefig("output/comparacao_2d_vs_3d.png", dpi=150)
    print("\nGráfico comparativo guardado em output/comparacao_2d_vs_3d.png")
    plt.show()


if __name__ == "__main__":
    main()