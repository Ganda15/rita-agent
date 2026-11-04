// =============================================================================
// LA COUTURE — l'écran parle à l'API RITA. Rien d'autre.
//
// C'est le seul fichier du front qui relève de **C10** :
//   « les étapes d'authentification sont intégrées correctement »
//   « tous les points de terminaison concernés sont intégrés »
//
// ⚠️ Era doit pouvoir défendre CHAQUE ligne de ce fichier à l'oral.
//    Le CSS, non. Celui-ci, oui.
// =============================================================================

const ENDPOINT = "/donnees/portefeuille";
// Lot 2 des indicateurs : poids par ligne et exposition par devise.
//
// Deux points de terminaison plutôt qu'un seul élargi : chacun garde une
// responsabilité. `/portefeuille` valorise, `/indicateurs-portefeuille` répartit.
// Les deux appels partent EN PARALLÈLE (`Promise.all`) — le temps d'attente est
// celui du plus lent, pas la somme des deux.
const ENDPOINT_INDICATEURS = "/donnees/indicateurs-portefeuille";
// Fraîcheur du jeu de données (C20) : répond à « ces chiffres datent de quand ? »
// sans que l'utilisateur ait à le demander, et sans relancer quoi que ce soit.
const ENDPOINT_FRAICHEUR = "/donnees/fraicheur";
const CLE_STOCKAGE = "rita_api_key";

// --- Formatage : une seule source de vérité pour les nombres -----------------
// Intl.NumberFormat est natif au navigateur : zéro dépendance à installer,
// zéro octet à télécharger. C'est un choix d'éco-conception (C17).
const euro = new Intl.NumberFormat("fr-FR", {
  style: "currency", currency: "EUR", minimumFractionDigits: 2,
});
const pourcent = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2, maximumFractionDigits: 2, signDisplay: "always",
});
// Un poids n'a pas de signe : il est toujours positif. Afficher « +34,83 % »
// suggérerait une variation, alors que c'est une part.
const pourcentSansSigne = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2, maximumFractionDigits: 2,
});
const nombre = new Intl.NumberFormat("fr-FR", { maximumFractionDigits: 4 });

// PostgreSQL renvoie du NUMERIC. Selon l'encodeur JSON, on reçoit un nombre ou
// une chaîne. On normalise UNE fois, ici, plutôt que de s'en méfier partout.
function nb(valeur) {
  const n = typeof valeur === "string" ? parseFloat(valeur) : valeur;
  return Number.isFinite(n) ? n : null;
}

// --- Les éléments des 4 états ------------------------------------------------
const elStatut = document.getElementById("statut");
const elConnexion = document.getElementById("connexion");
const elResultat = document.getElementById("resultat");

function afficherStatut(message) {
  elStatut.textContent = message;   // aria-live s'occupe de l'annonce
}

function demanderCle(message) {
  elResultat.hidden = true;
  elConnexion.hidden = false;
  afficherStatut(message || "");
  document.getElementById("cle").focus();   // le clavier arrive au bon endroit
}

// --- L'APPEL À L'API ---------------------------------------------------------
async function chargerPortefeuille(cle) {
  elConnexion.hidden = true;
  afficherStatut("Chargement du portefeuille…");

  const entetes = { headers: { "X-API-Key": cle } };

  let reponse, reponseIndicateurs, reponseFraicheur;
  try {
    // Les trois appels partent ensemble : l'attente est celle du plus lent, pas
    // la somme des trois. Les enchaîner triplerait le temps perçu pour rien.
    [reponse, reponseIndicateurs, reponseFraicheur] = await Promise.all([
      fetch(ENDPOINT, entetes),
      fetch(ENDPOINT_INDICATEURS, entetes),
      fetch(ENDPOINT_FRAICHEUR, entetes),
    ]);
  } catch (erreurReseau) {
    // Le serveur n'a pas répondu DU TOUT : il n'y a aucun statut HTTP à lire.
    // C'est un cas différent d'une réponse en erreur — d'où le try/catch.
    afficherStatut("Le serveur ne répond pas. Vérifiez que l'API est démarrée.");
    return;
  }

  if (reponse.status === 403) {
    // Une clé refusée n'est pas une panne : on l'oublie et on la redemande.
    sessionStorage.removeItem(CLE_STOCKAGE);
    demanderCle("Clé d'API refusée. Saisissez-la à nouveau.");
    return;
  }

  if (!reponse.ok) {
    afficherStatut(`Erreur ${reponse.status} — le serveur n'a pas pu répondre.`);
    return;
  }

  const donnees = await reponse.json();

  // ⚠️ Le portefeuille reste affiché même si les indicateurs échouent.
  // Les poids sont un COMPLÉMENT : perdre la répartition ne doit pas priver
  // l'utilisateur de ses positions et de leur valorisation. Une dépendance
  // secondaire qui fait tomber l'écran principal est une erreur de conception.
  const indicateurs = reponseIndicateurs.ok
    ? await reponseIndicateurs.json()
    : null;

  // Même raisonnement pour la fraîcheur, et il compte double ici : une jauge de
  // santé qui casse l'écran qu'elle surveille serait un comble. Si l'appel
  // échoue, le bandeau ne s'affiche pas — le portefeuille, si.
  const fraicheur = reponseFraicheur.ok
    ? await reponseFraicheur.json()
    : null;

  // On ne mémorise la clé qu'APRÈS l'avoir vue fonctionner.
  sessionStorage.setItem(CLE_STOCKAGE, cle);
  afficherFraicheur(fraicheur);
  afficher(donnees, indicateurs);
}

// --- LE BANDEAU DE FRAÎCHEUR (C20) -------------------------------------------
// Trois statuts et trois seulement. `statut` vient de l'API : on ne le colle pas
// tel quel dans un nom de classe sans le vérifier. Une liste blanche coûte une
// ligne et ferme la question — le jour où l'API rendrait autre chose, on affiche
// le message sans couleur plutôt que de fabriquer une classe inconnue.
const STATUTS_FRAICHEUR = ["vert", "orange", "rouge"];

function afficherFraicheur(fraicheur) {
  const bloc = document.getElementById("fraicheur");

  if (!fraicheur || !fraicheur.message) {
    bloc.hidden = true;
    return;
  }

  // textContent = "" vide le bloc sans innerHTML. Tout le front s'interdit
  // innerHTML : c'est la mesure prise contre A03 (injection) de l'OWASP Top 10.
  bloc.textContent = "";

  const statut = STATUTS_FRAICHEUR.includes(fraicheur.statut) ? fraicheur.statut : "";
  bloc.className = statut ? `fraicheur fraicheur-${statut}` : "fraicheur";

  // La pastille est décorative : aria-hidden la retire de l'arbre d'accessibilité.
  // Un lecteur d'écran lit le message, pas « puce ». L'information est dans le
  // texte — la couleur ne fait que la répéter pour ceux qui la voient.
  const pastille = document.createElement("span");
  pastille.className = "pastille";
  pastille.setAttribute("aria-hidden", "true");
  bloc.appendChild(pastille);

  bloc.appendChild(document.createTextNode(fraicheur.message));
  bloc.hidden = false;
}

// --- LE RENDU ----------------------------------------------------------------
function afficher(donnees, indicateurs) {
  // Plan 65 (03/10/2026, cas D06) : un total inconnu s'écrit « indisponible », jamais 0,00 €.
  const sansTaux = nb(donnees.positions_sans_taux) ?? 0;
  document.getElementById("total").textContent = donnees.total_eur === null || donnees.total_eur === undefined
    ? `indisponible (${sansTaux} position${sansTaux > 1 ? "s" : ""} sans taux de change)`
    : euro.format(nb(donnees.total_eur));
  document.getElementById("nb-lignes").textContent =
    ` · ${donnees.nb} ligne${donnees.nb > 1 ? "s" : ""}`;

  // Le poids est indexé par ticker : les deux points de terminaison n'ont aucune
  // raison de renvoyer leurs lignes dans le même ordre, et se fier à l'ordre
  // serait un défaut invisible tant que l'ordre coïncide par hasard.
  const poidsParTicker = new Map(
    (indicateurs?.lignes ?? []).map((l) => [l.ticker, nb(l.poids_pct)]),
  );

  const corps = document.getElementById("lignes");
  corps.replaceChildren();   // vide le tableau sans passer par innerHTML

  for (const p of donnees.positions) {
    const tr = document.createElement("tr");
    const perf = nb(p.performance_pct);

    // A3 (RGAA 3.1) : le SIGNE porte l'information, pas la couleur.
    // Un daltonien lit « -11,10 % » aussi bien que n'importe qui.
    const textePerf = perf === null ? "—" : `${pourcent.format(perf)} %`;

    ajouterCellule(tr, p.ticker, "th");
    ajouterCellule(tr, p.statut_qualite === "OK"
      ? p.nom_officiel
      : `${p.nom_officiel} (donnée douteuse)`);
    ajouterCellule(tr, nombre.format(nb(p.quantite)));
    ajouterCellule(tr, nombre.format(nb(p.pru)));
    ajouterCellule(tr, nombre.format(nb(p.cours)));
    // Un montant sans taux de change est « indisponible », avec la raison au survol ;
    // « 0,00 € » se lirait comme un montant nul, et absent n'est pas nul.
    const raisonTaux = p.taux_manquant ? `taux de change manquant pour ${p.devise}` : "";
    ajouterCellule(tr, p.taux_manquant ? "indisponible" : euro.format(nb(p.investi_eur)), "td", raisonTaux);
    ajouterCellule(tr, p.taux_manquant ? "indisponible" : euro.format(nb(p.valorisation_eur)), "td", raisonTaux);
    ajouterCellule(tr, textePerf);

    // Un tiret si le poids manque — jamais « 0,00 % », qui se lirait comme une
    // ligne de valeur nulle. Absent et nul ne sont pas la même chose.
    const poids = poidsParTicker.get(p.ticker);
    ajouterCellule(tr, poids === undefined || poids === null
      ? "—"
      : `${pourcentSansSigne.format(poids)} %`);

    corps.appendChild(tr);
  }

  afficherExposition(indicateurs?.exposition);

  const date = donnees.positions[0]?.date_cours;
  if (date) {
    document.getElementById("legende").textContent =
      `Portefeuille valorisé — cours du ${date}`;
  }

  afficherStatut("");
  elResultat.hidden = false;
}

// --- Exposition par devise (lot 2) -------------------------------------------
function afficherExposition(expositions) {
  const bloc = document.getElementById("bloc-exposition");

  // Si les indicateurs n'ont pas répondu, on masque le bloc plutôt que d'afficher
  // une section vide : une rubrique sans contenu se lit comme une panne.
  if (!expositions || expositions.length === 0) {
    bloc.hidden = true;
    return;
  }

  const liste = document.getElementById("exposition");
  liste.replaceChildren();

  for (const e of expositions) {
    const dt = document.createElement("dt");
    dt.textContent = e.devise;

    const dd = document.createElement("dd");
    const part = nb(e.exposition_pct);
    // Le nombre de lignes est donné en toutes lettres : « 7 lignes » se comprend
    // sans en-tête de colonne, contrairement à un « 7 » isolé.
    dd.textContent =
      `${part === null ? "—" : pourcentSansSigne.format(part)} %`
      + ` — ${e.nb_lignes} ligne${e.nb_lignes > 1 ? "s" : ""},`
      + ` ${nb(e.valorisation_eur) === null ? "indisponible" : euro.format(nb(e.valorisation_eur))}`;

    liste.append(dt, dd);
  }

  bloc.hidden = false;
}

function ajouterCellule(tr, texte, balise = "td", titre = "") {
  const cellule = document.createElement(balise);
  if (balise === "th") cellule.setAttribute("scope", "row");   // RGAA 5.7
  if (titre) cellule.title = titre;   // la raison d'un « indisponible », au survol
  // textContent, JAMAIS innerHTML : un nom d'instrument contenant du HTML
  // serait exécuté. C'est OWASP A03 — injection.
  cellule.textContent = texte;
  tr.appendChild(cellule);
}

// --- DÉMARRAGE ---------------------------------------------------------------
document.getElementById("form-cle").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  chargerPortefeuille(document.getElementById("cle").value.trim());
});

// sessionStorage (et non localStorage) : la clé disparaît à la fermeture
// de l'onglet. Elle n'est jamais écrite dans le code, donc jamais dans Git.
const cleMemorisee = sessionStorage.getItem(CLE_STOCKAGE);
// Refonte 001 (R7, décision D1) : en simulation, cet écran n'a pas encore de données d'exemple. Il ne démarre pas :
// aucun appel, aucune minuterie ; commun.js affiche « Simulation non disponible pour cet écran ».
if (window.RITA && window.RITA.estSimulation()) {
  window.RITA.suspendreEcran();
} else if (cleMemorisee) {
  chargerPortefeuille(cleMemorisee);
} else {
  demanderCle();
}
