# Vila Aurora

Uma vila de aventura para WorkAdventure, construída com mapas Tiled de 32 × 32.

## Explore

- Praça central, seis construções, trilhas, mata e lagoa.
- Quatro criaturas originais: Voltinho, Gotim, Broto e Brasin. Aproxime-se e pressione espaço para registrá-las no Pokédex local.
- Treinadores e moradores oferecem dicas e uma missão de descoberta.
- Centro Pokémon, Poké Mart e Laboratório têm salas internas próprias, com caminhos de ida e volta para a vila.
- A praça tem desafios rápidos pelo chat.

## Mapas

- `vila-aurora.tmj`: mapa exterior e entradas dos edifícios.
- `centro-pokemon.tmj`, `poke-mart.tmj`, `laboratorio.tmj`: salas internas.
- `src/main.ts` e `src/rooms.ts`: diálogos, encontros e transições.
- `tilesets/aurora/`: tilesets, criaturas, personagens e acessórios internos.
- `map.png`: prévia da vila.

Os tiles externos e interiores são baseados nos mapas de referência Tuto e Starter do WorkAdventure. Licenças e créditos estão em `LICENSE.assets` e `tilesets/aurora/credits/`. As criaturas e acessórios originais foram criados para Vila Aurora.

## Desenvolver

```powershell
npm.cmd run buildmap
```

O GitHub Pages publica os mapas em:

- [Vila Aurora](https://play.workadventu.re/_/global/alan-guimaraes.github.io/Vila-Aurora/vila-aurora.tmj)
- [Centro Pokémon](https://play.workadventu.re/_/global/alan-guimaraes.github.io/Vila-Aurora/centro-pokemon.tmj)
- [Poké Mart](https://play.workadventu.re/_/global/alan-guimaraes.github.io/Vila-Aurora/poke-mart.tmj)
- [Laboratório](https://play.workadventu.re/_/global/alan-guimaraes.github.io/Vila-Aurora/laboratorio.tmj)