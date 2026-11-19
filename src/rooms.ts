/// <reference types="@workadventure/iframe-api-typings" />

const VILLAGE_MAP = "https://play.workadventu.re/_/global/alan-guimaraes.github.io/Vila-Aurora/vila-aurora.tmj";

const rooms: Record<string, { author: string; message: string }> = {
  Enfermeira: { author: "Enfermeira Flora", message: "Bem-vindo ao Centro Pokémon! Descanse um pouco. Sua equipe está pronta para continuar a jornada." },
  Atendente: { author: "Lia, do Poké Mart", message: "Temos poções, frutas locais e mapas da mata. A lagoa fica a leste da praça." },
  Professor: { author: "Professor Ipê", message: "A região tem quatro criaturas conhecidas. Procure pegadas perto das flores e da água e registre cada encontro no Pokédex." },
};

WA.onInit().then(() => {
  WA.chat.sendChatMessage("Você chegou. Explore a sala e fale com a pessoa atrás do balcão.", { scope: "local", author: "Vila Aurora" });

  WA.room.area.onEnter("VoltarVila").subscribe(({ reason }) => {
    if (reason === "move") WA.nav.goToRoom(VILLAGE_MAP);
  });

  for (const [areaName, dialogue] of Object.entries(rooms)) {
    WA.room.area.onEnter(areaName).subscribe(({ reason }) => {
      if (reason !== "move") return;
      WA.chat.sendChatMessage(dialogue.message, { scope: "local", author: dialogue.author });
    });
  }
}).catch((error) => console.error("Erro ao iniciar sala de Vila Aurora:", error));

export {};
