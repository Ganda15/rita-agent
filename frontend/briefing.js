// =============================================================================
// LA COUTURE — l'écran briefing parle à l'API RITA. Rien d'autre.
//
// Troisième écran, 03/10/2026. Relève de **C10** : « tous les points de terminaison
// concernés sont intégrés ». Jusqu'ici `/briefing`, le seul point de terminaison qui
// expose le modèle (C9), ne se demandait que par curl, la passerelle MCP ou la
// documentation interactive : le rapport E3 le déclarait comme premier manque de C10.
//
// ⚠️ Era doit pouvoir défendre CHAQUE ligne de ce fichier à l'oral. Le CSS, non.
//
// Même dispositif que `app.js` et `indicateurs.js` : la clé vit en sessionStorage,
// n'est mémorisée qu'APRÈS avoir fonctionné, et disparaît à la fermeture de l'onglet.
// =============================================================================

const ENDPOINT = "/briefing";
// La liste des valeurs suivies remplit la liste déroulante du champ : une commodité,
// pas une barrière. La saisie libre reste possible, et un code inconnu est dit en clair.
const ENDPOINT_VALEURS = "/donnees/valeurs";
const CLE_STOCKAGE = "rita_api_key";   // partagée avec les deux autres écrans

const nombre = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 4 });
const pourcent = new Intl.NumberFormat("fr-FR", {
  minimumFractionDigits: 2, maximumFractionDigits: 2, signDisplay: "always",
});

function nb(valeur) {
  if (valeur === null || valeur === undefined) return null;
  const n = typeof valeur === "string" ? parseFloat(valeur) : valeur;
  return Number.isFinite(n) ? n : null;
}

// --- Les éléments des 4 états ------------------------------------------------
const elStatut = document.getElementById("statut");
const elConnexion = document.getElementById("connexion");
const elDemande = document.getElementById("demande");
const elResultat = document.getElementById("resultat");

function afficherStatut(message) {
  elStatut.textContent = message;   // aria-live s'occupe de l'annonce
}

function demanderCle(message) {
  elResultat.hidden = true;
  elDemande.hidden = true;
  elConnexion.hidden = false;
  afficherStatut(message || "");
  document.getElementById("cle").focus();
}

// --- ÉTAT 2 : la clé est là, on peut demander ----------------------------------
async function ouvrirDemande(cle) {
  elConnexion.hidden = true;
  elDemande.hidden = false;
  afficherStatut("");
  document.getElementById("ticker").focus();
  await remplirUnivers(cle);
}

// La liste déroulante est un COMPLÉMENT : si cet appel échoue, l'écran reste utilisable,
// on tape le code à la main. Une commodité qui casse l'écran serait une erreur de conception.
async function remplirUnivers(cle) {
  let reponse;
  try {
    reponse = await fetch(`${ENDPOINT_VALEURS}?limite=200`, { headers: { "X-API-Key": cle } });
  } catch (erreurReseau) {
    return;
  }
  if (!reponse.ok) return;
  const donnees = await reponse.json();
  const liste = document.getElementById("univers");
  liste.replaceChildren();
  for (const v of donnees.valeurs ?? []) {
    const option = document.createElement("option");
    option.value = v.ticker;
    option.label = v.nom_officiel;   // textContent n'est pas lu pour une option de datalist
    liste.appendChild(option);
  }
}

// --- L'APPEL AU MODÈLE (C9, par l'API) -----------------------------------------
async function demanderBriefing(cle, ticker) {
  elResultat.hidden = true;
  // Un appel au modèle dure 5 à 15 secondes (mesuré le 03/10/2026 : médiane 5,6 s, p95
  // 7,4 s hors recherche documentaire). Sans ce message, l'écran paraît figé.
  afficherStatut(`Rédaction en cours pour ${ticker}… Comptez quelques secondes (de 5 à 15 secondes).`);

  let reponse;
  try {
    // POST, parce que la requête déclenche un travail (une rédaction, payante), pas une
    // lecture. Le ticker passe en paramètre de requête, comme le contrat OpenAPI le décrit.
    reponse = await fetch(`${ENDPOINT}?ticker=${encodeURIComponent(ticker)}`, {
      method: "POST",
      headers: { "X-API-Key": cle },
    });
  } catch (erreurReseau) {
    afficherStatut("Le serveur ne répond pas. Vérifiez que l'API est démarrée.");
    return;
  }

  if (reponse.status === 403) {
    // Une clé refusée n'est pas une panne : on l'oublie et on la redemande.
    sessionStorage.removeItem(CLE_STOCKAGE);
    cleEnEssai = null;
    demanderCle("Clé d'API refusée. Saisissez-la à nouveau.");
    return;
  }

  if (reponse.status === 502) {
    // L'API répond 502 quand le graphe échoue : ticker absent de la base, ou aucun
    // fournisseur de modèle disponible. On distingue les deux par le détail renvoyé.
    const detail = await detailErreur(reponse);
    afficherStatut(detail.includes("absent") || detail.includes("ticker")
      ? `Valeur introuvable : « ${ticker} » n'est pas dans l'univers suivi.`
      : "Aucun fournisseur de modèle ne répond pour le moment. Réessayez plus tard.");
    return;
  }

  if (reponse.status === 422) {
    // Sprint 4 (C1) : une valeur absente du référentiel est refusée en 422, avant tout appel au modèle. Un code trop
    // long n'arrive pas jusqu'ici : le champ le refuse avant l'envoi (attribut `pattern`).
    afficherStatut(`Valeur introuvable : « ${ticker} » n'est pas dans l'univers suivi.`);
    return;
  }

  if (reponse.status === 429) {
    // Sprint 4 (C3) : la limite de débit. FastAPI range le refus poli sous `detail`.
    const refus = await texteDuRefus(reponse);
    afficherStatut(refus || "Trop de demandes en peu de temps. Réessayez dans une minute.");
    return;
  }

  if (!reponse.ok) {
    afficherStatut(`Erreur ${reponse.status} — le serveur n'a pas pu répondre.`);
    return;
  }

  const donnees = await reponse.json();

  // On ne mémorise la clé qu'APRÈS l'avoir vue fonctionner.
  sessionStorage.setItem(CLE_STOCKAGE, cle);
  // L'identifiant de requête est dans l'en-tête de TOUTE réponse (C11) : c'est le même
  // dans le journal de l'API et dans la trace du monitorage. On le montre pour le support.
  afficher(donnees, reponse.headers.get("X-Request-ID"));
}

async function texteDuRefus(reponse) {
  try {
    const corps = await reponse.json();
    return String(corps?.detail?.texte ?? "");
  } catch (erreur) {
    return "";
  }
}

async function detailErreur(reponse) {
  try {
    const corps = await reponse.json();
    return String(corps.detail ?? "");
  } catch (erreur) {
    return "";
  }
}

// --- LE RENDU ----------------------------------------------------------------
function afficher(donnees, requestId) {
  document.getElementById("donnees").textContent =
    `${donnees.ticker} — cours ${nombre.format(nb(donnees.price))} ${donnees.currency},`
    + ` variation sur une séance ${pourcent.format(nb(donnees.change_pct))} %`;

  // Le verdict du garde-fou de sortie est un TEXTE. La couleur ne fait que le répéter
  // (RGAA 3.1) : une personne qui ne voit pas la couleur lit exactement la même chose.
  const verdict = document.getElementById("verdict");
  if (donnees.conforme_amf) {
    verdict.className = "fraicheur fraicheur-vert";
    verdict.textContent = "Texte conforme : aucune recommandation d'achat ou de vente détectée.";
  } else {
    verdict.className = "fraicheur fraicheur-rouge";
    const motifs = (donnees.motifs_amf ?? []).join(", ");
    verdict.textContent = "Texte retenu par le garde-fou de sortie"
      + (motifs ? ` (motifs : ${motifs})` : "")
      + " : le modèle avait produit une recommandation, elle n'est pas diffusée.";
  }

  // Le texte du modèle est rendu en paragraphes, par textContent, JAMAIS innerHTML :
  // un texte venu d'un service extérieur est une donnée, pas du code (OWASP A03).
  // Les marques de mise en forme que le modèle ajoute parfois (** ou #) sont retirées :
  // on affiche des phrases, pas du Markdown brut.
  const bloc = document.getElementById("texte");
  bloc.replaceChildren();
  const paragraphes = String(donnees.briefing ?? "")
    .split(/\n\s*\n/)
    .map((p) => p.replace(/\*\*/g, "").replace(/^#+\s*/, "").trim())
    .filter((p) => p.length > 0);
  for (const p of paragraphes) {
    const el = document.createElement("p");
    el.textContent = p;
    bloc.appendChild(el);
  }

  document.getElementById("reference").textContent = requestId
    ? `Référence de la requête : ${requestId}`
    : "";

  afficherStatut("");
  elResultat.hidden = false;
  elResultat.focus();   // le lecteur d'écran et le clavier arrivent sur le résultat
}

// --- DÉMARRAGE ---------------------------------------------------------------
// #73 (01/11/2026) : la clé saisie reste en mémoire, pas en sessionStorage, tant qu'aucun appel ne l'a acceptée.
// Elle n'est gardée qu'après un appel réussi (`demanderBriefing`), et oubliée sur un 403.
let cleEnEssai = null;

document.getElementById("form-cle").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  cleEnEssai = document.getElementById("cle").value.trim();
  ouvrirDemande(cleEnEssai);
});

document.getElementById("form-briefing").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  const cle = sessionStorage.getItem(CLE_STOCKAGE) || cleEnEssai;
  if (!cle) {
    demanderCle("Saisissez d'abord votre clé d'API.");
    return;
  }
  demanderBriefing(cle, document.getElementById("ticker").value.trim().toUpperCase());
});

const cleMemorisee = sessionStorage.getItem(CLE_STOCKAGE);
// Refonte 001 (R7, décision D1) : en simulation, cet écran n'a pas encore de données d'exemple. Il ne démarre pas :
// aucun appel, aucune minuterie ; commun.js affiche « Simulation non disponible pour cet écran ».
if (window.RITA && window.RITA.estSimulation()) {
  window.RITA.suspendreEcran();
} else if (cleMemorisee) {
  ouvrirDemande(cleMemorisee);
} else {
  demanderCle();
}
