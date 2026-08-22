"""
Pipeline corrigido: ângulo 2D + interpolação por confiança de deteção
+ verificação de sanidade automática.

Abandonámos a correção via eixo z (mais ruidosa do que o problema
original). Esta versão trata os frames de baixa confiança como dados
em falta e interpola-os, em vez de confiar cegamente na deteção 2D
em todos os frames.
"""

import cv2
import mediapipe as mp
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt

from angle_3d import calcular_angulo_2d
from visibility_interpolation import (
    marcar_frames_baixa_confianca,
    interpolar_angulos,
    relatorio_interpolacao,
)
from sanity_check import relatorio_sanidade


mp_pose = mp.solutions.pose


def extrair_landmarks_do_video(video_path: str):
    """
    Igual ao script anterior — ajusta RIGHT_* para LEFT_* se necessário,
    e ajusta ao teu main.py real se a estrutura for diferente.
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
                if landmarks_por_frame:
                    landmarks_por_frame.append(landmarks_por_frame[-1])

    cap.release()
    return landmarks_por_frame


def main():
    video_path = "passe.mp4"

    print("A extrair landmarks do vídeo...")
    landmarks_por_frame = extrair_landmarks_do_video(video_path)
    print(f"Total de frames processados: {len(landmarks_por_frame)}")

    # 1. ângulo 2D bruto (a versão original, sem z)
    angulos_2d = [calcular_angulo_2d(o, c, p) for o, c, p in landmarks_por_frame]

    # 2. marcar frames de baixa confiança e interpolar
    mascara_confiavel = marcar_frames_baixa_confianca(
        landmarks_por_frame, limite_visibilidade=0.6
    )
    relatorio_interpolacao(mascara_confiavel, nome_video="passe.mp4")

    angulos_interpolados = interpolar_angulos(angulos_2d, mascara_confiavel)

    # 3. filtro de mediana por cima, igual ao que já tinhas
    angulos_finais = medfilt(angulos_interpolados, kernel_size=5)

    # 4. verificação de sanidade, para veres se ainda sobra algum salto
    relatorio_sanidade(angulos_finais, limite_graus_por_frame=25, nome_video="passe.mp4 (corrigido)")

    # gráfico comparativo: antes (2D bruto) vs depois (interpolado)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), sharey=True)

    ax1.plot(medfilt(angulos_2d, kernel_size=5), linewidth=2, color="steelblue")
    ax1.set_title("Antes — 2D bruto + filtro de mediana")
    ax1.set_xlabel("Frame")
    ax1.set_ylabel("Ângulo (graus)")
    ax1.grid(alpha=0.3)

    ax2.plot(angulos_finais, linewidth=2, color="darkorange")
    ax2.set_title("Depois — interpolado por confiança + filtro de mediana")
    ax2.set_xlabel("Frame")
    ax2.grid(alpha=0.3)

    plt.suptitle("Correção por visibilidade (não por eixo z)")
    plt.tight_layout()
    plt.savefig("output/comparacao_antes_depois_visibility.png", dpi=150)
    print("\nGráfico guardado em output/comparacao_antes_depois_visibility.png")
    plt.show()


if __name__ == "__main__":
    main()