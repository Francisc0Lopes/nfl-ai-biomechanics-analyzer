# NFL Biomechanics Analyzer

Um pipeline em Python que pega num vídeo de um quarterback a lançar e tenta perceber, de forma automática, como foi o gesto: onde começou a preparação, onde está o pico do lançamento e como foi o follow-through.

Comecei este projeto por curiosidade em juntar duas coisas que gosto: visão computacional e desporto. Não é um produto acabado, é um MVP para testar se dava para extrair sinal útil de um vídeo simples sem precisar de datasets gigantes ou modelos treinados de raiz.

## Como funciona

O vídeo é lido frame a frame com o OpenCV. Em cada frame, o MediaPipe Pose deteta os pontos do corpo do QB — o essencial aqui é o ombro, o cotovelo e o pulso do braço de lançamento. A partir dessas coordenadas, calculo o ângulo do braço usando trigonometria vetorial simples (nada de magia, é só o ângulo entre dois vetores em cada frame).

O problema é que a deteção de pose nem sempre é perfeita: há oclusões, o braço passa à frente do corpo, a qualidade do vídeo varia, e isso gera picos de ruído na série de ângulos ao longo do tempo. Para limpar isso, aplico um filtro de mediana (`scipy.signal.medfilt`), que corta esses saltos bruscos sem distorcer o movimento real.

Com a série de ângulos já limpa, uma heurística simples identifica os três momentos do gesto — preparação, pico do lançamento e follow-through — com base em onde o ângulo sobe, atinge o máximo e volta a descer.

## Stack

- Python
- OpenCV — leitura e manipulação do vídeo
- MediaPipe Pose — deteção do esqueleto
- SciPy — filtro de mediana para limpar o sinal
- NumPy e Matplotlib — cálculos e gráficos

## Estado atual

Isto é um MVP. Funciona bem com o vídeo de exemplo (`passe.mp4`), mas ainda não foi testado noutros vídeos com ângulos de câmara ou iluminação diferentes. A heurística de classificação é simples de propósito — a ideia era primeiro validar o pipeline todo, do vídeo ao resultado, antes de complicar a lógica de deteção.

## Próximos passos

- Gerar um gráfico do ângulo do braço ao longo do tempo com as fases marcadas
- Exportar o vídeo com o esqueleto desenhado por cima, para dar para ver o resultado visualmente
- Testar com mais vídeos para ver se a heurística aguenta variações de câmara e de gesto
- Adicionar um `requirements.txt` e instruções simples de instalação

## Como correr

```bash
python main.py
```

(vou adicionar argumentos de linha de comando para escolher o vídeo assim que tiver o `requirements.txt` pronto)