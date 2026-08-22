"""
Verificação automática de sanidade da série de ângulos.

Objetivo: detetar automaticamente saltos bruscos entre frames
consecutivos que provavelmente são artefactos de deteção (oclusão,
foreshortening, perda momentânea de tracking) em vez de movimento real.

Isto substitui a inspeção manual "olhar para o gráfico e reparar
a olho que há um salto estranho" por um processo repetível, que
vai continuar a funcionar mesmo quando tiveres muitos vídeos e não
puderes inspecionar cada um manualmente.
"""

import numpy as np


def detetar_saltos_suspeitos(angulos, limite_graus_por_frame=25):
    """
    Percorre a série de ângulos e assinala frames onde a diferença
    para o frame anterior excede o limite definido.

    Args:
        angulos: lista ou array com o ângulo em cada frame
        limite_graus_por_frame: diferença máxima considerada "normal"
            entre dois frames consecutivos. 25°/frame é um ponto de
            partida razoável para vídeo a ~30fps num gesto de lançamento;
            ajusta consoante a taxa de frames do teu vídeo e a
            velocidade real do movimento.

    Returns:
        Lista de dicionários, um por salto suspeito encontrado, com
        o frame, o ângulo antes, o ângulo depois, e a diferença.
    """
    angulos = np.array(angulos)
    diferencas = np.abs(np.diff(angulos))

    saltos = []
    for i, diff in enumerate(diferencas):
        if diff > limite_graus_por_frame:
            saltos.append({
                "frame": i + 1,
                "angulo_anterior": round(float(angulos[i]), 1),
                "angulo_atual": round(float(angulos[i + 1]), 1),
                "diferenca": round(float(diff), 1),
            })

    return saltos


def relatorio_sanidade(angulos, limite_graus_por_frame=25, nome_video="vídeo"):
    """
    Corre a verificação e imprime um resumo legível.
    Não interrompe o pipeline — só avisa, para decidires o que fazer.
    """
    saltos = detetar_saltos_suspeitos(angulos, limite_graus_por_frame)

    print(f"\n--- Verificação de sanidade: {nome_video} ---")
    if not saltos:
        print("Nenhum salto suspeito encontrado. Dados parecem consistentes.")
        return saltos

    print(f"{len(saltos)} salto(s) suspeito(s) encontrado(s):")
    for s in saltos:
        print(
            f"  Frame {s['frame']}: {s['angulo_anterior']}° -> "
            f"{s['angulo_atual']}° (diferença de {s['diferenca']}°)"
        )
    print(
        "Recomenda-se inspecionar visualmente estes frames "
        "(ex: com extrair_frames.py) antes de confiar nas métricas "
        "derivadas (ex: velocidade angular) nessa zona.\n"
    )
    return saltos