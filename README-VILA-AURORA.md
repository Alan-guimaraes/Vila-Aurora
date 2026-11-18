# Vila Aurora — arquivos para integrar ao WorkAdventure Map Starter Kit

Este ZIP é um **pacote de conteúdo para adicionar ao repositório criado a partir do template oficial**. Ele não substitui o Starter Kit.

## Publicação correta
1. No GitHub, abra https://github.com/workadventure/map-starter-kit e clique em **Use this template**.
2. Crie um repositório público chamado `vila-aurora` e marque **Include all branches**. Isso cria a estrutura e o fluxo GitHub Pages do Starter Kit.
3. Extraia este ZIP e envie os arquivos/pastas para a raiz do repositório `vila-aurora`, mantendo a estrutura.
4. Substitua o `.env` do template pelo `.env` deste pacote (UPLOAD_MODE=GH_PAGES).
5. Faça commit na branch principal e aguarde o GitHub Actions concluir a publicação.
6. Em Settings > Pages, confirme que a publicação está usando a branch `gh-pages` se o workflow pedir essa configuração.
7. Use a URL pública gerada pelo GitHub Pages no WorkAdventure.

## Arquivos
- `vila-aurora.tmj`: mapa Tiled na raiz do projeto.
- `map.png`: miniatura do mapa.
- `tilesets/aurora_tiles.png`: tileset original.
- `src/main.ts`: interações demonstrativas com a API do WorkAdventure.
- `.env`: seleciona publicação via GitHub Pages.

## Limitações do MVP
- Os edifícios têm áreas de interação e mensagens, mas ainda não têm interiores separados/transições.
- As criaturas são sprites decorativos com zonas de encontro; captura e inventário ainda não existem.
- A arena sorteia perguntas e exibe no chat; ainda não valida respostas nem mantém placar.
- Colisões e comportamento precisam ser testados no Tiled e dentro do WorkAdventure após publicar.

## Compatibilidade
Estrutura alinhada à organização documentada no WorkAdventure Map Starter Kit: mapas `.tmj` na raiz, scripts em `src/`, tilesets em `tilesets/`, script indicado pela propriedade `script` do mapa.
Documentação: https://github.com/workadventure/map-starter-kit
