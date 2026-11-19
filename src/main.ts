/// <reference types="@workadventure/iframe-api-typings" />

const MAIN_MAP = "https://play.workadventu.re/_/global/alan-guimaraes.github.io/Vila-Aurora/vila-aurora.tmj";
const rooms: Record<string, string> = {
  CentroPokemon: "centro-pokemon.tmj",
  PokeMart: "poke-mart.tmj",
  Laboratorio: "laboratorio.tmj",
};

const creatures: Record<string, { name: string; description: string }> = {
  EncontroPikachu: { name: "Voltinho", description: "uma criaturinha elétrica que adora ficar perto das pedras quentes" },
  EncontroAquatico: { name: "Gotim", description: "uma criatura aquática brincalhona que vive na lagoa" },
  EncontroFolha: { name: "Broto", description: "uma criaturinha de folhas que se esconde perto das flores" },
  EncontroNoturno: { name: "Brasin", description: "uma raposinha de fogo que aparece ao entardecer" },
};

const discovered = new Set<string>();

function onMoveInto(areaName: string, callback: () => void): void {
  WA.room.area.onEnter(areaName).subscribe(({ reason }) => {
    if (reason === "move") callback();
  });
}

WA.onInit().then(() => {
  WA.chat.sendChatMessage(
    "Bem-vindo à Vila Aurora! As criaturas passeiam pela mata e pela lagoa. Entre nas casas para conhecer a enfermeira, a lojista e o Professor Ipê.",
    { scope: "local", author: "Guia da Vila" }
  );

  onMoveInto("PracaCentral", () => {
    WA.chat.sendChatMessage(
      "A praça está cheia de treinadores hoje. Converse com o Professor Aurora e depois explore as trilhas!",
      { scope: "local", author: "Guia da Vila" }
    );
  });

  for (const [areaName, roomFile] of Object.entries(rooms)) {
    onMoveInto(areaName, () => {
      const destination = new URL(roomFile, MAIN_MAP).toString();
      WA.nav.goToRoom(destination);
    });
  }

  onMoveInto("CasaNorte", () => {
    WA.chat.sendChatMessage("Dona Nara: ouvi um barulho de asas vindo da lagoa. Leve uma fruta se for investigar!", { scope: "local", author: "Casa do Bosque" });
  });
  onMoveInto("CasaSul", () => {
    WA.chat.sendChatMessage("Seu Bento: a trilha do sul fica mais bonita quando os vaga-lumes aparecem.", { scope: "local", author: "Casa do Bosque" });
  });
  onMoveInto("ProfessorAurora", () => {
    WA.chat.sendChatMessage("Professor Aurora: encontre as quatro criaturas da vila e registre cada uma no seu Pokédex!", { scope: "local", author: "Professor Aurora" });
  });
  onMoveInto("TreinadorMart", () => {
    WA.chat.sendChatMessage("Lia, treinadora: achei pegadas pequenas perto da ponte. Elas seguem para a lagoa.", { scope: "local", author: "Treinadora Lia" });
  });
  onMoveInto("Pesquisadora", () => {
    WA.chat.sendChatMessage("Pesquisadora: as flores azuis só crescem onde Broto costuma descansar.", { scope: "local", author: "Pesquisadora Bia" });
  });

  for (const [areaName, creature] of Object.entries(creatures)) {
    onMoveInto(areaName, () => {
      if (discovered.has(creature.name)) {
        WA.chat.sendChatMessage(`${creature.name} reconhece você e balança a cauda.`, { scope: "local", author: "Pokédex" });
        return;
      }
      WA.ui.displayActionMessage({
        message: `${creature.name} apareceu — pressione espaço para registrar no Pokédex.`,
        callback: () => {
          discovered.add(creature.name);
          WA.chat.sendChatMessage(`Nova descoberta! ${creature.name}: ${creature.description}.`, { scope: "local", author: "Pokédex" });
          WA.event.broadcast("aurora-creature-found", { name: creature.name });
        },
      });
    });
  }

  onMoveInto("ArenaEventos", () => {
    const questions = [
      "Desafio da praça: qual tipo costuma levar vantagem contra criaturas aquáticas? Responda no chat: ELÉTRICO, FOGO ou PEDRA.",
      "Desafio da praça: qual criatura vive na lagoa? Responda no chat: GOTIM, BROTO ou BRASIN.",
    ];
    WA.chat.sendChatMessage(questions[Math.floor(Math.random() * questions.length)], { scope: "local", author: "Arena de Vila Aurora" });
  });
}).catch((error) => console.error("Erro ao iniciar Vila Aurora:", error));

export {};
