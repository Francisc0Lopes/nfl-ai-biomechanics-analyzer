# 🏈 NFL Biomechanics Analyzer

Um pipeline de Visão Computacional e Processamento de Sinal desenvolvido em Python para extrair, limpar e analisar dados de *Quarterbacks* a partir de vídeo.

---

## 🚀 Sobre o Projeto
Este projeto foi desenvolvido como um MVP (Minimum Viable Product) para explorar a aplicação de inteligência artificial baseada em heurísticas e análise de séries temporais na biomecânica de passes de Futebol Americano. 

O sistema automatiza a extração de movimentos humanos em vídeo, remove o ruído causado por oclusões e classifica a jogada com base na extensão e velocidade angular do braço.

---

## 🛠️ Stack Tecnológica
* **Python** (Linguagem principal)
* **OpenCV** (Ingestão, manipulação e renderização de vídeo)
* **MediaPipe Pose** (Extração de *landmarks* corporais e esqueleto 3D/2D)
* **SciPy** (Filtragem de sinal digital com filtros de mediana para eliminação de ruído)
* **NumPy & Matplotlib** (Cálculos trigonométricos e visualização de dados)

---

## ⚙️ Arquitetura do Pipeline
1. **Ingestão de Vídeo:** Leitura *frame-by-frame* do ficheiro de vídeo de origem.
2. **Pose Estimation:** Deteção das coordenadas articulares (ombro, cotovelo e pulso direito) através do MediaPipe.
3. **Cálculo Cinemático:** Conversão de píxeis em ângulos trigonométricos absolutos utilizando trigonometria vetorial.
4. **Processamento de Sinal:** Aplicação de um filtro de mediana (`scipy.signal.medfilt`) para eliminar anomalias de oclusão e ruído visual.
5. **Heurística de Decisão:** Extração de métricas-chave (Preparação, Pico/Lançamento, Follow-through) para classificação automática da jogada.
