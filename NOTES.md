# Notas Técnicas do Projeto

Registo de decisões técnicas, testes e limitações encontradas ao longo do desenvolvimento. Não é documentação de utilizador (isso está no README) — é o histórico de raciocínio por trás das decisões de engenharia tomadas neste projeto.

---

## Gráfico das fases do lançamento

Gerado o gráfico do ângulo do cotovelo ao longo do vídeo `passe.mp4`, com marcação automática de 3 fases: início, pico (máximo), fim. Resultado visual claro e as anotações batem certo com o vídeo — início no frame 0 (1.5°), máximo no frame 75 (177.5°), fim no frame 84 (155.6°).

**Problema identificado:** entre os frames ~44 e ~60, o ângulo sobe até 172°, cai bruscamente para ~37°, e só depois volta a subir até ao máximo real (frame 75). Isto é um comportamento suspeito — parece um segundo pico dentro do mesmo lançamento.

---

## Investigação do mergulho entre os frames 44-60

### Hipótese 1: são dois lançamentos/gestos diferentes no vídeo

Descartada. Extraí os frames com `extrair_frames.py` e inspecionei visualmente o frame ~52 — é claramente o mesmo gesto contínuo de lançamento, não dois eventos separados. O QB está a meio da rotação do braço, filmado de costas.

### Hipótese 2: foreshortening — o braço aponta para a câmara durante a rotação

O vídeo foi filmado com a câmara **atrás do QB**, na mesma direção do lançamento. Quando o braço, durante a rotação, passa por uma posição que aponta mais para a câmara do que lateralmente, a projeção 2D (x, y) "encolhe" a distância entre ombro-cotovelo-pulso, fazendo o ângulo calculado cair artificialmente — mesmo que o braço, no espaço real (3D), esteja esticado.

**Tentativa de correção 1 — usar o eixo z do MediaPipe no cálculo do ângulo:**
Implementado em `angle_3d.py` (função `calcular_angulo_3d`), comparado lado a lado com a versão 2D original em `regenerar_grafico_3d.py`.

Resultado: **piorou.** O gráfico 3D passou a ter oscilações constantes ao longo de todo o gesto, não só na zona do mergulho. Motivo: o `z` do MediaPipe é uma estimativa monocular de profundidade (não é medido, é inferido pelo modelo), muito mais ruidosa do que x/y. Ao usá-lo, introduzi mais ruído do que o problema que queria resolver.

**Decisão: reverter.** Voltar à versão 2D como base (`calcular_angulo_2d`), não usar o eixo z para este cálculo.

**Tentativa de correção 2 — interpolação por confiança de deteção (visibility):**
Hipótese: talvez o mergulho fosse causado por baixa confiança de deteção (oclusão momentânea), não por geometria. Implementado em `visibility_interpolation.py` — marca frames com `visibility` abaixo de 0.6 como não-confiáveis e interpola a partir dos frames vizinhos confiáveis.

Resultado: **sem efeito relevante.** O mergulho manteve-se praticamente idêntico (mesmo valor mínimo, ~33°, no mesmo intervalo de frames). Isto indica que o MediaPipe estava confiante na deteção nesses frames — o problema não é deteção fraca, é geometria genuína da projeção 2D.

### Conclusão

O mergulho é **foreshortening real**, não um bug de deteção nem dois gestos separados. É uma limitação conhecida de calcular ângulos a partir de uma única câmara 2D quando o membro em análise roda numa direção alinhada com o eixo da câmara.

### Decisão final para a Fase 1

Não perseguir mais correções agora — já foram testadas duas abordagens razoáveis (z bruto, interpolação por confiança) e nenhuma resolveu sem introduzir mais problemas. Documentar como limitação conhecida e avançar.

**Para o futuro (Fase 3+):** uma correção robusta exigiria algo como um modelo de "3D lifting" mais sofisticado (ex: VideoPose3D) ou triangulação com múltiplas câmaras — fora do âmbito deste MVP. Fica registado aqui para retomar se o projeto justificar o investimento.

**Ação de validação sugerida (ainda por fazer):** gravar um vídeo curto de perfil (câmara de lado, perpendicular ao braço) para confirmar que, nesse ângulo, a deteção de fases fica limpa e sem mergulho — isso reforça que a causa é mesmo o ângulo de câmara, não outra coisa no pipeline.

---

## Limitações conhecidas

- **Foreshortening 2D:** ângulos calculados a partir de vídeo filmado de trás/costas do jogador sofrem distorção durante parte da rotação do braço. Ver secção acima para detalhe.
- **Testado apenas com 1 vídeo até agora** (`passe.mp4`). Ainda não validado com vídeos de ângulos de câmara diferentes ou com outros lançadores.
- **Deteção de fases é heurística simples** (baseada em mínimo/máximo do ângulo), não um modelo treinado — pode falhar em gestos atípicos.

---

## Próximos passos técnicos

- [ ] Gravar vídeo de perfil para validação cruzada
- [X] Calcular velocidade angular (derivada do ângulo)
- [X] Exportar vídeo anotado com esqueleto sobreposto
- [ ] Testar pipeline com 1-2 vídeos adicionais
- https://github.com/Francisc0Lopes/nfl-ai-biomechanics-analyzer/issues/1