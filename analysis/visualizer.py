import cv2

def desenhar_telemetria(frame, angulo, velocidade):
    """Desenha os dados de ângulo e velocidade no ecrã."""
    cv2.putText(frame, f"Angulo: {angulo:.1f} graus", (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    
    cv2.putText(frame, f"Velocidade: {velocidade:.1f} gr/s", (50, 90), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 2, cv2.LINE_AA)
    return frame

def desenhar_angulo_cotovelo(frame, cotovelo, angulo):
    """Desenha o valor do ângulo diretamente em cima do cotovelo do jogador."""
    posicao_texto = (int(cotovelo[0] * 1280), int(cotovelo[1] * 720))
    cv2.putText(frame, str(int(angulo)), posicao_texto, 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3, cv2.LINE_AA)
    return frame