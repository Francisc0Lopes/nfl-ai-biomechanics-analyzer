import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path


# Diretório raiz do projeto
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Caminhos dos ficheiros
DATA_FILE = PROJECT_ROOT / "data" / "historico_limpo.npy"
OUTPUT_DIR = PROJECT_ROOT / "output"
OUTPUT_FILE = OUTPUT_DIR / "fases_lancamento.png"


# =========================
# 1. Carregar os dados
# =========================

historico_limpo = np.load(DATA_FILE)

if len(historico_limpo) == 0:
    raise ValueError("O histórico de ângulos está vazio.")


# =========================
# 2. Identificar eventos
# =========================

i_inicio = 0
i_maximo = np.argmax(historico_limpo)
i_fim = len(historico_limpo) - 1

angulo_inicio = historico_limpo[i_inicio]
angulo_maximo = historico_limpo[i_maximo]
angulo_fim = historico_limpo[i_fim]

frames = np.arange(len(historico_limpo))


# =========================
# 3. Criar gráfico
# =========================

plt.figure(figsize=(12, 6))

plt.plot(
    frames,
    historico_limpo,
    linewidth=2,
    label="Ângulo do cotovelo"
)


# =========================
# 4. Início
# =========================

plt.axvline(
    x=i_inicio,
    linestyle="--",
    label=f"Início — frame {i_inicio}"
)

plt.scatter(
    i_inicio,
    angulo_inicio,
    s=80,
    zorder=5
)

plt.annotate(
    f"Início\nFrame: {i_inicio}\nÂngulo: {angulo_inicio:.1f}°",
    xy=(i_inicio, angulo_inicio),
    xytext=(15, 45),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->")
)


# =========================
# 5. Máximo
# =========================

plt.axvline(
    x=i_maximo,
    linestyle="--",
    label=f"Máximo — frame {i_maximo}"
)

plt.scatter(
    i_maximo,
    angulo_maximo,
    s=100,
    zorder=5
)

plt.annotate(
    f"Máximo\nFrame: {i_maximo}\nÂngulo: {angulo_maximo:.1f}°",
    xy=(i_maximo, angulo_maximo),
    xytext=(-80, -65),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->")
)


# =========================
# 6. Fim
# =========================

plt.axvline(
    x=i_fim,
    linestyle="--",
    label=f"Fim — frame {i_fim}"
)

plt.scatter(
    i_fim,
    angulo_fim,
    s=80,
    zorder=5
)

plt.annotate(
    f"Fim\nFrame: {i_fim}\nÂngulo: {angulo_fim:.1f}°",
    xy=(i_fim, angulo_fim),
    xytext=(-100, -65),
    textcoords="offset points",
    arrowprops=dict(arrowstyle="->")
)


# =========================
# 7. Configuração visual
# =========================

plt.title(
    "Análise do Ângulo do Braço durante o Lançamento"
)

plt.xlabel("Frame")

plt.ylabel("Ângulo do cotovelo (graus)")

# Dar espaço acima dos 180° para as anotações
plt.ylim(-5, 190)

plt.legend(loc="lower right")

plt.grid(True, alpha=0.3)

plt.tight_layout()


# =========================
# 8. Guardar
# =========================

OUTPUT_DIR.mkdir(exist_ok=True)

plt.savefig(
    OUTPUT_FILE,
    dpi=150
)

plt.close()


# =========================
# 9. Resultado no terminal
# =========================

print("\n--- EVENTOS DETETADOS ---")

print(
    f"Início:  frame {i_inicio} | "
    f"ângulo {angulo_inicio:.1f}°"
)

print(
    f"Máximo:  frame {i_maximo} | "
    f"ângulo {angulo_maximo:.1f}°"
)

print(
    f"Fim:     frame {i_fim} | "
    f"ângulo {angulo_fim:.1f}°"
)

print(f"\nGráfico guardado em: {OUTPUT_FILE}")