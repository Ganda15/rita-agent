// =============================================================================
// L'ÉCRAN INDICATEURS (refonte 001, tâche 8 ; spécification R2 ; conception § 5).
//
// Relève de C10 : l'écran appelle /donnees/indicateurs, /donnees/indicateurs-risque et, au choix d'une valeur,
// /donnees/cotations. Comparer les valeurs suivies, et lire un indicateur comme un FAIT, jamais comme un conseil.
//
// ⚠️ Era doit pouvoir défendre CHAQUE ligne de ce fichier à l'oral.
//
// Les règles, chacune testée (tests/test_indicateurs_ui.py) :
// - la carte des performances se lit sans la couleur : chiffre signé et flèche dans chaque case ;
// - le RSI s'écrit « RSI 14 : 41, zone neutre de 30 à 70 » (graphiques.js) ; jamais affiché pour une cotation périmée ;
// - le nombre de valeurs vient des données, jamais d'un chiffre écrit à la main ;
// - chaque bloc a sa panne : le tableau reste si le risque ou la courbe échouent ;
// - la courbe d'une valeur choisie avant n'apparaît jamais sous la valeur choisie ensuite.
// La clé et les appels passent par commun.js (RITA.appeler).
// =============================================================================

const ENDPOINT = "/donnees/indicateurs";
// Le lot 3 (volatilité, pire baisse, RSI) vient d'un point de terminaison séparé : chacun garde une responsabilité, et
// les deux appels partent EN PARALLÈLE (Promise.all) plus bas.
const ENDPOINT_RISQUE = "/donnees/indicateurs-risque";
const PERIODES = ["perf_1j_pct", "perf_1s_pct", "perf_1m_pct", "perf_ytd_pct", "perf_1a_pct"];

const elStatut = document.getElementById("statut");
const elConnexion = document.getElementById("connexion");
const elResultat = document.getElementById("resultat");
const elMasquer = document.getElementById("masquer-perimees");
const elRecherche = document.getElementById("recherche");
const elTri = document.getElementById("tri");
const elDetail = document.getElementById("detail");

// Les données chargées, gardées en mémoire : la recherche, le tri et le filtre ne rappellent pas l'API.
let donneesChargees = null;
let risqueParTicker = new Map();   // lot 3 ; reste vide si ce point de terminaison échoue
let cleUtilisee = null;
let choixCourant = 0;              // chaque choix de valeur porte un numéro ; une réponse périmée est ignorée

// --- Mise en forme : null n'est pas 0 -------------------------------------------
function nb(valeur) {
  if (valeur === null || valeur === undefined) return null;
  const n = typeof valeur === "string" ? Number(valeur) : valeur;
  return Number.isFinite(n) ? n : null;
}

function nombre(valeur, decimales = 2) {
  return valeur.toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
}

// Un tiret dit « pas calculable » ; un zéro dirait « aucune variation ». Le signe et la flèche portent l'information,
// jamais la seule couleur (RGAA 3.1).
function variation(v) {
  const n = nb(v);
  if (n === null) return "–";
  if (n === 0) return `${nombre(0)} %`;
  return `${n > 0 ? "▲ +" : "▼ -"}${nombre(Math.abs(n))} %`;
}

function pourcentSigne(v) {
  const n = nb(v);
  return n === null ? "–" : `${n < 0 ? "-" : ""}${nombre(Math.abs(n))} %`;
}

// La volatilité est une amplitude, toujours positive : « +20,50 % » suggérerait une variation.
function pourcentSansSigne(v) {
  const n = nb(v);
  return n === null ? "–" : `${nombre(n)} %`;
}

function dateFr(iso) {
  const t = String(iso ?? "");
  return /^\d{4}-\d{2}-\d{2}/.test(t) ? `${t.slice(8, 10)}/${t.slice(5, 7)}/${t.slice(0, 4)}` : "date inconnue";
}

function afficherStatut(message) {
  elStatut.textContent = message;   // aria-live s'occupe de l'annonce
}

function demanderCle(message) {
  elResultat.hidden = true;
  elConnexion.hidden = false;
  afficherStatut(message || "");
  document.getElementById("cle").focus();
}

// --- L'APPEL À L'API ---------------------------------------------------------
async function chargerIndicateurs(cle) {
  elConnexion.hidden = true;
  afficherStatut("Chargement des indicateurs…");
  let reponse, reponseRisque;
  try {
    // En parallèle : l'attente est celle du plus lent, pas la somme des deux. Le lot 3 peut échouer seul.
    [reponse, reponseRisque] = await Promise.all([
      RITA.appeler(ENDPOINT, { cle }),
      RITA.appeler(ENDPOINT_RISQUE, { cle }).catch(() => null),
    ]);
  } catch (erreurReseau) {
    afficherStatut("Le serveur ne répond pas. Vérifiez que l'API est démarrée.");
    return;
  }
  if (reponse.status === 401 || reponse.status === 403) {
    cleEnEssai = null;   // RITA.appeler a déjà oublié la clé gardée
    demanderCle("Clé d'API refusée. Saisissez-la à nouveau.");
    return;
  }
  if (!reponse.ok) {
    afficherStatut(`Erreur ${reponse.status} : les indicateurs n'ont pas pu être chargés.`);
    return;
  }
  donneesChargees = await reponse.json();
  cleUtilisee = cle;
  // ⚠️ Le lot 1 reste affiché même si le lot 3 échoue : une dépendance secondaire ne fait pas tomber l'écran.
  const risque = reponseRisque && reponseRisque.ok ? await reponseRisque.json() : null;
  // Appariement PAR TICKER, jamais par position : les deux points de terminaison n'ont aucune raison de rendre leurs
  // lignes dans le même ordre.
  risqueParTicker = new Map((risque?.indicateurs ?? []).map((r) => [r.ticker, r]));
  document.getElementById("note-risque").textContent = risque
    ? "" : "Volatilité, pire baisse et RSI indisponibles pour le moment ; les performances restent à jour.";
  afficher();
}

// --- LA CARTE DES PERFORMANCES -----------------------------------------------
function lignesAffichees() {
  const recherche = elRecherche.value.trim().toLowerCase();
  let lignes = donneesChargees.indicateurs.filter((i) => !(elMasquer.checked && i.cotation_perimee));
  if (recherche) {
    lignes = lignes.filter((i) => `${i.ticker} ${i.nom_officiel}`.toLowerCase().includes(recherche));
  }
  const tri = elTri.value;
  if (tri !== "ticker") {
    // De la plus forte hausse à la plus forte baisse ; une valeur absente va à la fin, jamais comme un zéro.
    lignes = [...lignes].sort((a, b) => {
      const va = nb(a[tri]), vb = nb(b[tri]);
      if (va === null) return vb === null ? 0 : 1;
      if (vb === null) return -1;
      return vb - va;
    });
  }
  return lignes;
}

function afficher() {
  const lignes = lignesAffichees();
  const nbPerimees = donneesChargees.indicateurs.filter((i) => i.cotation_perimee).length;
  // Le nombre vient des lignes reçues : jamais un chiffre écrit à la main.
  document.getElementById("nb-valeurs").textContent = `${lignes.length} valeur${lignes.length > 1 ? "s" : ""}`;
  document.getElementById("mention-perimees").textContent = nbPerimees === 0 ? ""
    : ` · ${nbPerimees} cotation${nbPerimees > 1 ? "s" : ""} périmée${nbPerimees > 1 ? "s" : ""}`
      + (elMasquer.checked ? (nbPerimees > 1 ? " masquées" : " masquée") : " dans l'univers suivi");

  const corps = document.getElementById("lignes");
  corps.replaceChildren();   // vide le tableau sans passer par innerHTML
  for (const i of lignes) corps.appendChild(ligneDuTableau(i));

  const date = donneesChargees.indicateurs.find((i) => !i.cotation_perimee)?.date_cours;
  document.getElementById("legende").textContent = date
    ? `Carte des performances : cours du ${dateFr(date)}` : "Carte des performances";
  afficherStatut("");
  elResultat.hidden = false;
}

function ligneDuTableau(i) {
  const tr = document.createElement("tr");
  tr.dataset.ticker = String(i.ticker);
  // L'en-tête de ligne porte le bouton qui ouvre le détail : atteignable et actionnable au clavier.
  const entete = ajouterCellule(tr, "", "th");
  const bouton = document.createElement("button");
  bouton.type = "button";
  bouton.className = "choisir-valeur";
  bouton.textContent = String(i.ticker);
  bouton.setAttribute("aria-label", `Voir le détail de ${i.nom_officiel}`);
  bouton.addEventListener("click", () => choisirValeur(i));
  entete.appendChild(bouton);
  // La péremption est dite EN TEXTE : une pastille colorée ne serait perçue que par ceux qui voient les couleurs.
  ajouterCellule(tr, i.cotation_perimee
    ? `${i.nom_officiel} (cotation périmée : dernière séance le ${dateFr(i.date_cours)})` : String(i.nom_officiel));
  ajouterCellule(tr, nb(i.cours) === null ? "–" : nombre(nb(i.cours)));
  for (const champ of PERIODES) {
    const cellule = ajouterCellule(tr, variation(i[champ]));
    const n = nb(i[champ]);
    cellule.className = `perf ${n === null || n === 0 ? "perf-nulle" : n > 0 ? "perf-hausse" : "perf-baisse"}`;
  }
  const r = risqueParTicker.get(i.ticker);
  ajouterCellule(tr, pourcentSansSigne(r?.volatilite_annualisee_pct));
  ajouterCellule(tr, pourcentSigne(r?.drawdown_max_1a_pct));
  // Le RSI n'a pas de signe : c'est un rapport sur 100. Jamais affiché pour une cotation périmée.
  ajouterCellule(tr, !i.cotation_perimee && nb(r?.rsi_14) !== null ? nombre(nb(r.rsi_14), 1) : "–");
  if (i.cotation_perimee) tr.classList.add("perimee");
  return tr;
}

function ajouterCellule(tr, texte, balise = "td") {
  const cellule = document.createElement(balise);
  if (balise === "th") cellule.setAttribute("scope", "row");   // RGAA 5.7
  // textContent, JAMAIS innerHTML : un nom d'instrument contenant du HTML serait exécuté (OWASP A03).
  cellule.textContent = texte;
  tr.appendChild(cellule);
  return cellule;
}

// --- LE DÉTAIL DE LA VALEUR CHOISIE --------------------------------------------
async function choisirValeur(i) {
  const numero = ++choixCourant;
  const r = risqueParTicker.get(i.ticker);
  document.getElementById("detail-titre").textContent = `${i.ticker} : ${i.nom_officiel}`;

  // Le RSI, un fait : la jauge et sa phrase viennent de graphiques.js. Pas de RSI pour une cotation périmée.
  const rsi = i.cotation_perimee ? null : nb(r?.rsi_14);
  const jauge = GRAPHIQUES.jauge(rsi);
  document.getElementById("detail-rsi").replaceChildren(...[jauge.svg, jauge.alternative].filter(Boolean));

  const liste = document.getElementById("detail-liste");
  liste.replaceChildren();
  const ajouter = (texte) => {
    const li = document.createElement("li");
    li.textContent = texte;
    liste.appendChild(li);
  };
  ajouter(`cours du ${dateFr(i.date_cours)} : ${nb(i.cours) === null ? "–" : nombre(nb(i.cours))} ${String(i.devise ?? "")}`.trim());
  ajouter(`MM20 : ${nb(i.ma20) === null ? "– (moins de 20 séances)" : nombre(nb(i.ma20))}`);
  ajouter(`MM50 : ${nb(i.ma50) === null ? "– (moins de 50 séances)" : nombre(nb(i.ma50))}`);
  ajouter(`échangé par jour (20 séances) : ${nb(i.adtv20) === null ? "–"
    : new Intl.NumberFormat("fr-FR", { notation: "compact", maximumFractionDigits: 1 }).format(nb(i.adtv20))}`);
  ajouter(`écart au plus haut (1 an) : ${pourcentSigne(i.distance_plus_haut_1a_pct)}`);
  ajouter(`volatilité (1 an) : ${pourcentSansSigne(r?.volatilite_annualisee_pct)}`);
  ajouter(`pire baisse (1 an) : ${pourcentSigne(r?.drawdown_max_1a_pct)}`);

  const lien = elDetail.querySelector("a.vers-briefing");
  lien.href = `briefing.html?ticker=${encodeURIComponent(i.ticker)}`;

  const zone = document.getElementById("detail-courbe");
  zone.replaceChildren(Object.assign(document.createElement("p"), { className: "precision",
                                                                     textContent: "Chargement de la courbe…" }));
  elDetail.hidden = false;
  elDetail.focus();   // le clavier et le lecteur d'écran arrivent sur le détail

  let cotations = null;
  try {
    const reponse = await RITA.appeler(`/donnees/cotations?ticker=${encodeURIComponent(i.ticker)}&limite=179`,
                                       { cle: cleUtilisee });
    if (reponse.ok) cotations = (await reponse.json())?.cotations ?? null;
  } catch (erreurReseau) {
    cotations = null;
  }
  if (numero !== choixCourant) return;   // une réponse tardive n'écrit jamais sous une autre valeur
  if (!cotations) {
    zone.replaceChildren(Object.assign(document.createElement("p"), { className: "precision",
                                                                       textContent: "Courbe indisponible pour le moment." }));
    return;
  }
  const dessin = GRAPHIQUES.courbe(cotations);
  zone.replaceChildren(...[dessin.svg, dessin.alternative].filter(Boolean));
}

// --- DÉMARRAGE ---------------------------------------------------------------
let cleEnEssai = null;

document.getElementById("form-cle").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  cleEnEssai = document.getElementById("cle").value.trim();
  chargerIndicateurs(cleEnEssai);
});

for (const reglage of [elMasquer, elTri]) {
  reglage.addEventListener("change", () => { if (donneesChargees) afficher(); });
}
elRecherche.addEventListener("input", () => { if (donneesChargees) afficher(); });

const cleMemorisee = RITA.lireCle();
// Refonte 001 (R7, décision D1) : en simulation, cet écran n'a pas encore de données d'exemple. Il ne démarre pas :
// aucun appel, aucune minuterie ; commun.js affiche « Simulation non disponible pour cet écran ».
if (window.RITA && window.RITA.estSimulation()) {
  window.RITA.suspendreEcran();
} else if (cleMemorisee) {
  chargerIndicateurs(cleMemorisee);
} else {
  demanderCle();
}
