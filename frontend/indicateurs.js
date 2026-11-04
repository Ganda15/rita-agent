// =============================================================================
// LA COUTURE — l'écran indicateurs parle à l'API RITA. Rien d'autre.
//
// Relève de **C10** : « les étapes d'authentification sont intégrées correctement »,
// « tous les points de terminaison concernés sont intégrés ».
//
// ⚠️ Era doit pouvoir défendre CHAQUE ligne de ce fichier à l'oral. Le CSS, non.
//
// Même dispositif d'authentification que `app.js` : la clé vit en sessionStorage,
// n'est mémorisée qu'APRÈS avoir fonctionné, et disparaît à la fermeture de l'onglet.
// =============================================================================

const ENDPOINT = "/donnees/indicateurs";
// Lot 3 : volatilité, drawdown, RSI — un point de terminaison séparé, comme le
// lot 2 sur l'écran portefeuille. Même raison : chacun garde une responsabilité,
// et les deux appels partent EN PARALLÈLE (Promise.all) plus bas.
const ENDPOINT_RISQUE = "/donnees/indicateurs-risque";
const CLE_STOCKAGE = "rita_api_key";   // partagée avec l'écran portefeuille

// --- Formatage : natif au navigateur, zéro octet téléchargé (éco-conception C17)
const nombre = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2, maximumFractionDigits: 2,
});
const pourcent = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2, maximumFractionDigits: 2, signDisplay: "always",
});
const compact = new Intl.NumberFormat("fr-FR", {
  notation: "compact", maximumFractionDigits: 1,
});

// PostgreSQL renvoie du NUMERIC ; l'API le convertit déjà en float. On normalise
// tout de même ici : une valeur absente doit rester absente, jamais devenir 0.
function nb(valeur) {
  if (valeur === null || valeur === undefined) return null;
  const n = typeof valeur === "string" ? parseFloat(valeur) : valeur;
  return Number.isFinite(n) ? n : null;
}

const elStatut = document.getElementById("statut");
const elConnexion = document.getElementById("connexion");
const elResultat = document.getElementById("resultat");
const elMasquer = document.getElementById("masquer-perimees");

// Les données chargées, gardées en mémoire : le filtre ne rappelle pas l'API.
let donneesChargees = null;
let donneesRisque = null;   // lot 3 — peut rester null si ce point de terminaison échoue

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

  const entetes = { headers: { "X-API-Key": cle } };
  let reponse, reponseRisque;
  try {
    // En parallèle : l'attente est celle du plus lent, pas la somme des deux.
    [reponse, reponseRisque] = await Promise.all([
      fetch(ENDPOINT, entetes),
      fetch(ENDPOINT_RISQUE, entetes),
    ]);
  } catch (erreurReseau) {
    // Le serveur n'a pas répondu DU TOUT : aucun statut HTTP à lire.
    // Cas distinct d'une réponse en erreur — d'où le try/catch.
    afficherStatut("Le serveur ne répond pas. Vérifiez que l'API est démarrée.");
    return;
  }

  if (reponse.status === 403) {
    sessionStorage.removeItem(CLE_STOCKAGE);
    demanderCle("Clé d'API refusée. Saisissez-la à nouveau.");
    return;
  }

  if (!reponse.ok) {
    afficherStatut(`Erreur ${reponse.status} — le serveur n'a pas pu répondre.`);
    return;
  }

  donneesChargees = await reponse.json();

  // ⚠️ Le lot 1 reste affiché même si le lot 3 échoue — même règle que sur
  // l'écran portefeuille : une dépendance secondaire ne doit pas faire tomber
  // l'écran principal.
  donneesRisque = reponseRisque.ok ? await reponseRisque.json() : null;

  sessionStorage.setItem(CLE_STOCKAGE, cle);   // mémorisée seulement après succès
  afficher();
}

// --- LE RENDU ----------------------------------------------------------------
function afficher() {
  const masquer = elMasquer.checked;
  const lignes = masquer
    ? donneesChargees.indicateurs.filter((i) => !i.cotation_perimee)
    : donneesChargees.indicateurs;

  const nbPerimees = donneesChargees.indicateurs.filter((i) => i.cotation_perimee).length;

  // Appariement PAR TICKER, pas par position : les deux points de terminaison
  // n'ont aucune raison de renvoyer leurs lignes dans le même ordre — vérifié
  // sur l'écran portefeuille le 19/08, où c'était effectivement le cas.
  const risqueParTicker = new Map(
    (donneesRisque?.indicateurs ?? []).map((r) => [r.ticker, r]),
  );

  document.getElementById("nb-valeurs").textContent =
    `${lignes.length} valeur${lignes.length > 1 ? "s" : ""}`;

  // La mention est du TEXTE, pas une couleur : elle reste lisible pour tout le monde.
  document.getElementById("mention-perimees").textContent =
    nbPerimees === 0 ? ""
      : masquer ? ` · ${nbPerimees} cotation${nbPerimees > 1 ? "s" : ""} périmée${nbPerimees > 1 ? "s" : ""} masquée${nbPerimees > 1 ? "s" : ""}`
                : ` · dont ${nbPerimees} cotation${nbPerimees > 1 ? "s" : ""} périmée${nbPerimees > 1 ? "s" : ""}`;

  const corps = document.getElementById("lignes");
  corps.replaceChildren();   // vide le tableau sans passer par innerHTML

  for (const i of lignes) {
    const tr = document.createElement("tr");

    ajouterCellule(tr, i.ticker, "th");

    // Le nom porte la mention de péremption EN TEXTE. Un lecteur d'écran la lit ;
    // une pastille colorée ne serait perçue que par ceux qui voient les couleurs.
    ajouterCellule(tr, i.cotation_perimee
      ? `${i.nom_officiel} (cotation périmée — dernière séance le ${i.date_cours})`
      : i.nom_officiel);

    ajouterCellule(tr, formatNombre(i.cours));
    for (const champ of ["perf_1j_pct", "perf_1s_pct", "perf_1m_pct",
                         "perf_ytd_pct", "perf_1a_pct"]) {
      ajouterCellule(tr, formatPourcent(i[champ]));
    }
    ajouterCellule(tr, formatNombre(i.ma20));
    ajouterCellule(tr, formatNombre(i.ma50));
    ajouterCellule(tr, formatCompact(i.adtv20));
    ajouterCellule(tr, formatPourcent(i.distance_plus_haut_1a_pct));

    // Lot 3 : absent si le point de terminaison a échoué, ou si la valeur n'a
    // pas de ligne récente (radiée — voir indicateurs/risque.py, lire_rsi).
    const r = risqueParTicker.get(i.ticker);
    ajouterCellule(tr, formatPourcentSansSigne(r?.volatilite_annualisee_pct));
    ajouterCellule(tr, formatPourcent(r?.drawdown_max_1a_pct));
    // Le RSI n'a pas de signe : c'est un rapport 0-100, pas une variation.
    ajouterCellule(tr, r?.rsi_14 != null ? nombre.format(r.rsi_14) : "—");

    if (i.cotation_perimee) tr.classList.add("perimee");
    corps.appendChild(tr);
  }

  const date = donneesChargees.indicateurs[0]?.date_cours;
  document.getElementById("legende").textContent = date
    ? `Indicateurs de marché — cours du ${date}`
    : "Indicateurs de marché";

  afficherStatut("");
  elResultat.hidden = false;
}

// --- Formatage : null ≠ 0 ----------------------------------------------------
// Un tiret dit « pas calculable ». Un 0 dirait « aucune variation ». Confondre
// les deux ferait lire une performance nulle là où il n'y en a simplement pas.
function formatNombre(v) {
  const n = nb(v);
  return n === null ? "—" : nombre.format(n);
}

function formatPourcent(v) {
  const n = nb(v);
  // Le SIGNE porte l'information, jamais la seule couleur (RGAA 3.1).
  return n === null ? "—" : `${pourcent.format(n)} %`;
}

function formatCompact(v) {
  const n = nb(v);
  return n === null ? "—" : compact.format(n);
}

// La volatilité est toujours ≥ 0 : "+20,50 %" suggérerait une variation,
// alors que c'est une amplitude. Même raisonnement que le poids du lot 2.
function formatPourcentSansSigne(v) {
  const n = nb(v);
  return n === null ? "—" : `${nombre.format(n)} %`;
}

function ajouterCellule(tr, texte, balise = "td") {
  const cellule = document.createElement(balise);
  if (balise === "th") cellule.setAttribute("scope", "row");   // RGAA 5.7
  // textContent, JAMAIS innerHTML : un nom d'instrument contenant du HTML serait
  // exécuté. C'est OWASP A03 — injection.
  cellule.textContent = texte;
  tr.appendChild(cellule);
}

// --- DÉMARRAGE ---------------------------------------------------------------
document.getElementById("form-cle").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  chargerIndicateurs(document.getElementById("cle").value.trim());
});

// Le filtre agit sur les données déjà chargées : aucun appel réseau, donc aucune
// attente. Redemander à l'API la même chose, filtrée, coûterait un aller-retour
// pour un travail que le navigateur fait instantanément.
elMasquer.addEventListener("change", () => {
  if (donneesChargees) afficher();
});

const cleMemorisee = sessionStorage.getItem(CLE_STOCKAGE);
// Refonte 001 (R7, décision D1) : en simulation, cet écran n'a pas encore de données d'exemple. Il ne démarre pas :
// aucun appel, aucune minuterie ; commun.js affiche « Simulation non disponible pour cet écran ».
if (window.RITA && window.RITA.estSimulation()) {
  window.RITA.suspendreEcran();
} else if (cleMemorisee) {
  chargerIndicateurs(cleMemorisee);
} else {
  demanderCle();
}
