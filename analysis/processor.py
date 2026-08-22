import numpy as np
from scipy.signal import medfilt

def calcular_angulo(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radianos = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angulo = np.abs(radianos * 180.0 / np.pi)
    if angulo > 180.0:
        angulo = 360.0 - angulo
    return angulo

def limpar_sinal(historico_angulos, tamanho_janela=7):
    return medfilt(historico_angulos, kernel_size=tamanho_janela)

def calcular_velocidade_maxima(historico_limpo, fps=30.0):
    """Calcula a derivada máxima (graus/segundo) de uma série temporal."""
    velocidade_maxima = 0
    for i in range(1, len(historico_limpo)):
        diferenca = abs(historico_limpo[i] - historico_limpo[i-1])
        velocidade_atual = diferenca * fps
        if velocidade_atual > velocidade_maxima:
            velocidade_maxima = velocidade_atual
    return velocidade_maxima

def classificar_passe(angulo_lancamento):
    if angulo_lancamento > 165:
        return "PASSE LONGO (Deep Pass)", "Máxima extensão do braço detetada."
    elif 130 <= angulo_lancamento <= 165:
        return "PASSE CURTO / BULLET", "Extensão intermédia, foco na rapidez."
    else:
        return "MOVIMENTO INVÁLIDO", "O braço não atingiu extensão suficiente."