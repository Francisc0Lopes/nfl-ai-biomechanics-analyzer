"""
Cálculo de ângulo articular em 3D (x, y, z), em vez de só 2D (x, y).

Porquê: quando o braço roda numa direção que aponta para a câmara,
a projeção 2D "encolhe" a distância entre as articulações e o ângulo
calculado fica artificialmente pequeno (foreshortening). O MediaPipe
já devolve uma coordenada z (profundidade relativa) para cada landmark,
por isso usá-la no cálculo remove a maior parte deste artefacto.

Nota sobre o z do MediaPipe: não é uma distância absoluta em metros,
é uma profundidade relativa ao ponto médio das ancas, na mesma escala
aproximada que x e y. Para o objetivo aqui (ângulo entre 3 pontos),
isso é suficiente — não precisamos do valor absoluto, só da direção
correta do vetor no espaço 3D.
"""

import numpy as np


def calcular_angulo_3d(ombro, cotovelo, pulso):
    """
    Calcula o ângulo no cotovelo, usando as 3 coordenadas (x, y, z)
    de cada landmark do MediaPipe.

    Args:
        ombro, cotovelo, pulso: cada um um objeto/tuplo com atributos
            ou índices .x, .y, .z (landmarks do MediaPipe Pose)

    Returns:
        Ângulo em graus (0-180), no espaço 3D.
    """
    p_ombro = np.array([ombro.x, ombro.y, ombro.z])
    p_cotovelo = np.array([cotovelo.x, cotovelo.y, cotovelo.z])
    p_pulso = np.array([pulso.x, pulso.y, pulso.z])

    vetor_superior = p_ombro - p_cotovelo   # cotovelo -> ombro
    vetor_inferior = p_pulso - p_cotovelo   # cotovelo -> pulso

    # ângulo entre os dois vetores, via produto escalar
    cos_theta = np.dot(vetor_superior, vetor_inferior) / (
        np.linalg.norm(vetor_superior) * np.linalg.norm(vetor_inferior) + 1e-8
    )
    # clip por segurança numérica (evita erros de arccos por arredondamento)
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    angulo_rad = np.arccos(cos_theta)
    return np.degrees(angulo_rad)


def calcular_angulo_2d(ombro, cotovelo, pulso):
    """
    Versão original 2D (x, y), mantida para comparação lado a lado
    e para confirmares visualmente a diferença antes/depois do fix.
    """
    p_ombro = np.array([ombro.x, ombro.y])
    p_cotovelo = np.array([cotovelo.x, cotovelo.y])
    p_pulso = np.array([pulso.x, pulso.y])

    vetor_superior = p_ombro - p_cotovelo
    vetor_inferior = p_pulso - p_cotovelo

    cos_theta = np.dot(vetor_superior, vetor_inferior) / (
        np.linalg.norm(vetor_superior) * np.linalg.norm(vetor_inferior) + 1e-8
    )
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    angulo_rad = np.arccos(cos_theta)
    return np.degrees(angulo_rad)