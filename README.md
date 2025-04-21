# Top-Down Pixel RPG

Bem-vindo ao repositório do **Top-Down Pixel RPG**, um jogo 2D desenvolvido em Python com Pygame para a disciplina de Computação Gráfica (2025). Este projeto implementa conceitos gráficos como texturas, animações, iluminação e transformações geométricas em um RPG inspirado em clássicos como Pokémon.

\
*Observação: Substitua o link acima por uma captura de tela real do jogo.*

---

## Descrição do Projeto

O **Top-Down Pixel RPG** é um jogo de RPG 2D ambientado em um mapa de 100x100 tiles com ambientes variados, incluindo grama, rios, montanhas, vilarejos e cavernas. O jogador controla um herói que explora o mundo, luta contra inimigos (goblins e lobos), interage com NPCs para completar missões (ex.: entregar mensagens, matar um lobo) e gerencia itens no inventário. O jogo apresenta:

- **Ciclo de Dia e Noite**: Escurecimento dinâmico com base na hora.
- **Sistema de Clima**: Chuva, neve e neblina com partículas animadas.
- **Minimapa**: Exibição do mapa com zoom opcional.
- **Interface (HUD)**: Mostra saúde, estamina, missões e notificações.

Desenvolvido por Hyago Colares para demonstrar conceitos de Computação Gráfica, o projeto usa Pygame para renderização 2D eficiente.

---

## Conceitos Gráficos Implementados

O jogo incorpora os seguintes conceitos de Computação Gráfica:

- **Textura**: Tiles coloridos (ex.: grama verde, rio azul) renderizados em `src/map.py` com `pygame.draw.rect`, simulando texturas via cores RGB.
- **Animação**: Partículas climáticas (chuva, neve, neblina) animadas em `src/weather.py` com atualizações de posição por frame, usando delta time.
- **Iluminação**: Ciclo de dia e noite em `src/time_system.py`, com camada semitransparente de alfa 0 (dia) a 150 (noite), aplicada em `src/main.py`.
- **Transformações Geométricas**:
  - Câmera com translação para seguir o jogador (`src/camera.py`).
  - Minimapa com escalonamento de 2 ou 4 pixels por tile (`src/map.py`).
  - Pathfinding de inimigos com algoritmo A\* (`src/enemy.py`).

---

## Apresentação do Projeto

Assista à nossa apresentação em vídeo (5 minutos), que explica o jogo, os conceitos gráficos e inclui uma demonstração ao vivo:

📺 **Vídeo no YouTube**: https://youtu.be/4tddWM_byE8

---

## Pré-requisitos

- **Python**: 3.13.1
- **Pygame**: 2.6.1

---

## Instalação

1. Clone o repositório:

   ```bash
   git clone https://github.com/Hyagocolares/Game-Top-Down-rpg.git
   cd Game-Top-Down-rpg
   ```

2. Instale as dependências:

   ```bash
   pip install pygame==2.6.1
   ```

3. Execute o jogo:

   ```bash
   python src/main.py
   ```

   - Alternativamente, abra `src/main.py` em um IDE (ex.: PyCharm) e execute com `Shift+F10`.

---

## Controles

- **Movimento**: WASD
- **Correr**: Shift Esquerdo
- **Interagir**: E
- **Atacar**: Espaço
- **Inventário**: I
- **Registro de Missões**: T
- **Pausar**: Esc

---

## Estrutura do Projeto

```plaintext
Game-Top-Down-rpg/
├── src/
│   ├── assets/              # Arquivos de recursos (se houver)
│   ├── main.py              # Loop principal e integração
│   ├── player.py            # Lógica do jogador
│   ├── enemy.py             # Lógica dos inimigos
│   ├── npc.py               # Lógica dos NPCs
│   ├── camera.py            # Sistema de câmera
│   ├── hud.py               # Interface do usuário
│   ├── inventory.py         # Sistema de inventário
│   ├── map.py               # Renderização do mapa e minimapa
│   ├── quest.py             # Sistema de missões
│   ├── time_system.py       # Ciclo de dia e noite
│   ├── weather.py           # Efeitos climáticos
│   ├── menu.py              # Menu principal
│   ├── pause_menu.py        # Menu de pausa
│   ├── settings.py          # Configurações do jogo
├── README.md                # Este arquivo
```

---

## Notas de Execução

- Para testar efeitos climáticos, modifique `time_system.hour` em `src/main.py` antes do loop `while True`:
  - `21` para chuva
  - `22` para noite
  - `0` para neve
  - `19` para neblina
- Se o mapa escurecer demais, verifique se `src/weather.py` usa `weather_surface.fill((0, 0, 0, 0))`.
- Para melhor desempenho, ajuste `REAL_SECONDS_PER_GAME_DAY` em `src/settings.py` para 60 ou use o modo “Fast” no menu principal.

---

## Solução de Problemas

- **Jogo não executa**:

  - Confirme Python 3.13.1 e Pygame 2.6.1.
  - Limpe a pasta `__pycache__`:

    ```bash
    find . -name "__pycache__" -exec rm -rf {} +
    ```

- **Erros de renderização**:

  - Certifique-se de que o Python está usando a versão correta:

    ```bash
    python --version
    pip show pygame
    ```

---

## Contribuições

Este projeto foi desenvolvido para um trabalho acadêmico e não está aberto a contribuições no momento. No entanto, sinta-se à vontade para abrir uma *issue* se encontrar problemas ou sugerir melhorias!

---

## Autores

- Hyago Colares

---

## Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` (a ser adicionado, se necessário) para mais detalhes.

---
