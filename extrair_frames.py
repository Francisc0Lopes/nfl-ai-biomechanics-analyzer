"""
Extrai frames específicos de um vídeo para inspeção visual.
Útil para perceber o que aconteceu num intervalo de frames onde
os dados de ângulo mostraram um comportamento estranho.

Uso:
    python extrair_frames.py --video passe.mp4 --inicio 40 --fim 65 --saida frames_debug/
"""

import cv2
import os
import argparse


def extrair_frames(video_path: str, frame_inicio: int, frame_fim: int, pasta_saida: str):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Não encontrei o vídeo em: {video_path}")

    os.makedirs(pasta_saida, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Não consegui abrir o vídeo: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Vídeo tem {total_frames} frames no total, a {fps:.1f} fps.")

    if frame_fim >= total_frames:
        print(f"Aviso: frame_fim ({frame_fim}) é maior que o total de frames "
              f"({total_frames}). Vou limitar ao último frame disponível.")
        frame_fim = total_frames - 1

    frame_atual = 0
    guardados = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_inicio <= frame_atual <= frame_fim:
            nome_ficheiro = os.path.join(pasta_saida, f"frame_{frame_atual:03d}.png")
            cv2.imwrite(nome_ficheiro, frame)
            guardados += 1

        if frame_atual > frame_fim:
            break

        frame_atual += 1

    cap.release()
    print(f"Guardei {guardados} frames em '{pasta_saida}/' "
          f"(do frame {frame_inicio} ao {frame_fim}).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extrai frames de um vídeo para inspeção.")
    parser.add_argument("--video", type=str, default="passe.mp4",
                         help="Caminho para o ficheiro de vídeo (default: passe.mp4)")
    parser.add_argument("--inicio", type=int, default=40,
                         help="Frame inicial a extrair (default: 40)")
    parser.add_argument("--fim", type=int, default=65,
                         help="Frame final a extrair (default: 65)")
    parser.add_argument("--saida", type=str, default="frames_debug",
                         help="Pasta onde guardar os frames extraídos (default: frames_debug)")

    args = parser.parse_args()
    extrair_frames(args.video, args.inicio, args.fim, args.saida)