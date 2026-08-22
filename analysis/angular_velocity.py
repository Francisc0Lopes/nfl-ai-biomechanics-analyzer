import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import medfilt
import os

historico_limpo = np.load('data/historico_limpo.npy')

fps = 30.0
velocidade_bruta = np.gradient(historico_limpo) * fps
velocidade_limpa = medfilt(velocidade_bruta, kernel_size=5)
# pico da velocidade
pico_vel = np.max(velocidade_limpa)
frame_pico = np.argmax(velocidade_limpa)

print(f"Velocidade Angular Máxima Real: {pico_vel:.1f} graus/segundo (No frame {frame_pico})")

plt.figure(figsize=(10, 6))
plt.plot(velocidade_bruta, label='Velocidade (Bruta)', color='gray', alpha=0.5)
plt.plot(velocidade_limpa, label='Velocidade Angular (Limpa)', color='purple', linewidth=2)

plt.axvline(x=frame_pico, color='red', linestyle='--', label='Pico de Lançamento')

plt.title('Dinâmica do Passe: Velocidade Angular do Braço')
plt.xlabel('Frame')
plt.ylabel('Velocidade (Graus/Segundo)')
plt.legend()
plt.grid(True, alpha=0.3)

os.makedirs('./output', exist_ok=True)
plt.savefig('./output/velocidade_angular.png')
print("Gráfico guardado em 'output/velocidade_angular.png'")