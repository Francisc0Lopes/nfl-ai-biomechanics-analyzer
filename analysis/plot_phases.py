import numpy as np
import matplotlib.pyplot as plt
import os

# Carregar os dados
historico_limpo = np.load('../data/historico_limpo.npy')

# Encontrar os índices das fases
# Preparação: índice 0
# Pico: onde o ângulo é máximo
# Fim: último índice
i_prep = 0
i_pico = np.argmax(historico_limpo)
i_fim = len(historico_limpo) - 1

# Configurar o gráfico
plt.figure(figsize=(10, 6))
plt.plot(historico_limpo, label='Ângulo do Cotovelo (Limpo)', color='red', linewidth=2)

# Linhas verticais
plt.axvline(x=i_prep, color='green', linestyle='--', label='Início (Prep)')
plt.axvline(x=i_pico, color='blue', linestyle='--', label='Pico (Lançamento)')
plt.axvline(x=i_fim, color='orange', linestyle='--', label='Fim (Follow-through)')

# Estilização
plt.title('Análise Biomecânica do Passe')
plt.xlabel('Frame')
plt.ylabel('Ângulo (graus)')
plt.legend()
plt.grid(True, alpha=0.3)

os.makedirs('../output', exist_ok=True)

# Guardar
plt.savefig('../output/fases_lancamento.png')
print("Gráfico guardado em 'output/fases_lancamento.png'")
# plt.show() # Descomenta se quiseres ver na hora