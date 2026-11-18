/// <reference types="@workadventure/iframe-api-typings" />

// Vila Aurora — MVP para WorkAdventure
// Interações demonstrativas locais; captura, inventário e pontuação compartilhada
// ficam para uma próxima versão.

WA.onInit().then(() => {
  WA.chat.sendChatMessage(
    "Bem-vindo à Vila Aurora! Explore a praça, visite os prédios e procure criaturas escondidas.",
    { scope: "local", author: "Guia da Vila" }
  );

  const buildingMessages: Record<string, string> = {
    CentroPokemon: "Centro Pokémon: ponto de encontro dos treinadores. A área interna completa será adicionada na próxima etapa.",
    PokeMart: "Poké Mart: loja da cidade. Sistema de compras e inventário ainda será desenvolvido.",
    CasaNorte: "Casa de morador: explore e procure pistas da região.",
    Laboratorio: "Laboratório: pesquisas sobre as criaturas de Vila Aurora estão em andamento.",
    CasaSul: "Casa de morador: alguém pode ter deixado uma pista por aqui.",
    ArenaEventos: "Arena de eventos: entre para iniciar um desafio demonstrativo!"
  };

  for (const [areaName, message] of Object.entries(buildingMessages)) {
    WA.room.area.onEnter(areaName).subscribe(({ reason }) => {
      if (reason !== "move") return;
      WA.chat.sendChatMessage(message, { scope: "local", author: "Vila Aurora" });
    });
  }

  const encounters: Record<string, string> = {
    EncontroPikachu: "Você encontrou Voltinho, uma criatura elétrica curiosa!",
    EncontroAquatico: "Você encontrou Gotim, uma criatura aquática brincalhona!",
    EncontroFolha: "Você encontrou Broto, uma criatura que adora jardins!",
    EncontroNoturno: "Você encontrou Lunito, uma criatura misteriosa!"
  };

  for (const [areaName, message] of Object.entries(encounters)) {
    WA.room.area.onEnter(areaName).subscribe(({ reason }) => {
      if (reason !== "move") return;
      WA.chat.sendChatMessage(
        `${message} (Encontro demonstrativo: captura será implementada depois.)`,
        { scope: "local", author: "Pokédex" }
      );
      WA.event.broadcast("aurora-creature-found", { creature: areaName });
    });
  }

  WA.room.area.onEnter("ArenaEventos").subscribe(({ reason }) => {
    if (reason !== "move") return;
    const questions = [
      "QUIZ: Qual tipo costuma ser forte contra Água? Responda: ELÉTRICO, FOGO ou PEDRA.",
      "QUIZ: Quantas casas há em um tabuleiro 3x3? Responda com um número.",
      "QUIZ: O que um treinador precisa para começar uma jornada? Responda: MAPA, EQUIPE ou INSÍGNIA."
    ];
    const question = questions[Math.floor(Math.random() * questions.length)];
    WA.chat.sendChatMessage(question, { scope: "local", author: "Arena de Vila Aurora" });
    WA.chat.sendChatMessage(
      "Protótipo de quiz: perguntas aparecem no chat; validação de respostas e placar ainda serão adicionados.",
      { scope: "local", author: "Arena de Vila Aurora" }
    );
  });
}).catch((error) => console.error("Erro ao iniciar Vila Aurora:", error));

export {};
