"""
Interpolação de landmarks com base na confiança de deteção (visibility).

Em vez de tentar adivinhar profundidade com o eixo z (que se mostrou
mais ruidoso do que o problema que queríamos resolver), esta abordagem
usa o campo `.visibility` que o MediaPipe já devolve para cada landmark
(0 a 1, quão confiante está o modelo naquele ponto naquele frame).

Quando a visibilidade de um ponto cai abaixo de um limite, tratamos
esse frame como "dado em falta" e interpolamos a partir dos frames
vizinhos com boa confiança, em vez de confiarmos numa deteção fraca.
"""

import numpy as np


def marcar_frames_baixa_confianca(landmarks_por_frame, limite_visibilidade=0.6):
    """
    Percorre os landmarks de cada frame e identifica quais têm
    confiança baixa (ombro, cotovelo ou pulso).

    Args:
        landmarks_por_frame: lista de tuplos (ombro, cotovelo, pulso),
            cada um com atributos .x, .y, .z, .visibility (landmarks MediaPipe)
        limite_visibilidade: abaixo disto, o frame é considerado não-confiável

    Returns:
        Array booleano, True onde o frame é confiável, False onde não é.
    """
    confiavel = []
    for ombro, cotovelo, pulso in landmarks_por_frame:
        vis_minima = min(ombro.visibility, cotovelo.visibility, pulso.visibility)
        confiavel.append(vis_minima >= limite_visibilidade)

    return np.array(confiavel)


def interpolar_angulos(angulos, mascara_confiavel):
    """
    Substitui os ângulos em frames não-confiáveis por uma interpolação
    linear entre o último e o próximo frame confiável.

    Args:
        angulos: array de ângulos, um por frame (já calculados em 2D)
        mascara_confiavel: array booleano da função acima

    Returns:
        Array de ângulos com os frames não-confiáveis substituídos.
    """
    angulos = np.array(angulos, dtype=float)
    indices = np.arange(len(angulos))

    indices_confiaveis = indices[mascara_confiavel]
    angulos_confiaveis = angulos[mascara_confiavel]

    if len(indices_confiaveis) < 2:
        print("Aviso: poucos frames confiáveis para interpolar. "
              "A devolver os ângulos originais sem alteração.")
        return angulos

    # interpola todos os índices a partir dos pontos confiáveis
    # (nos extremos, usa o valor confiável mais próximo em vez de extrapolar)
    angulos_interpolados = np.interp(
        indices, indices_confiaveis, angulos_confiaveis
    )

    return angulos_interpolados


def relatorio_interpolacao(mascara_confiavel, nome_video="vídeo"):
    """
    Imprime quantos frames foram considerados não-confiáveis e onde,
    para saberes exatamente que troços do vídeo foram interpolados.
    """
    total = len(mascara_confiavel)
    nao_confiaveis = np.where(~mascara_confiavel)[0]

    print(f"\n--- Interpolação por confiança: {nome_video} ---")
    print(f"{len(nao_confiaveis)} de {total} frames tinham confiança baixa "
          f"({100 * len(nao_confiaveis) / total:.1f}%).")

    if len(nao_confiaveis) > 0:
        # agrupa frames consecutivos em intervalos, para leitura mais fácil
        intervalos = []
        inicio = nao_confiaveis[0]
        anterior = nao_confiaveis[0]
        for f in nao_confiaveis[1:]:
            if f != anterior + 1:
                intervalos.append((inicio, anterior))
                inicio = f
            anterior = f
        intervalos.append((inicio, anterior))

        print("Intervalos interpolados:")
        for ini, fim in intervalos:
            print(f"  Frame {ini} a {fim}")
    print()