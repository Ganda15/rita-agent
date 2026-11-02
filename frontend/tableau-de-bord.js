// =============================================================================
// LE TABLEAU DE BORD : l'état du service, en mots simples (sprint 5, étape 5 ; grille de l'atelier 5, critère 2).
//
// Une carte de disponibilité (/health), puis une carte par signal de supervision (/sante). Chaque carte dit son état
// en toutes lettres (SAIN, ATTENTION, PROBLÈME, INCONNU), sa valeur en mots, et « Que faire » quand il faut agir.
// Un état « inconnu » a sa propre explication, jamais présenté comme sain.
//
// Même dispositif que les autres écrans : la clé vit en sessionStorage, n'est gardée qu'après avoir fonctionné, est
// oubliée sur un 401 ou un 403 ; tout est rendu par textContent (OWASP A03). Propre à cet écran : un appel ne reste
// jamais pendu (5 secondes au plus), une actualisation ne se lance jamais deux fois en même temps, et une réponse mal
// formée rend une carte « inconnu » au lieu de casser la page. Seul le résumé est annoncé aux lecteurs d'écran.
// =============================================================================

const CLE_STOCKAGE = "rita_api_key";   // partagée avec les autres écrans
const DELAI_MS = 5000;
const INTERVALLE_MS = 30000;

const ETATS = new Map([["sain", "SAIN"], ["attention", "ATTENTION"], ["probleme", "PROBLÈME"], ["inconnu", "INCONNU"]]);

// La consigne du service : dans le script, car la carte doit rester lisible quand /sante ne répond plus. Un test
// (tests/test_tableau_de_bord.py) vérifie qu'elle reste celle de monitorage/seuils.json.
const CONSIGNE_SERVICE = "Suivre « Diagnostiquer une panne » dans la documentation d'exploitation : vérifier que la copie tourne, puis lire son journal.";

// Les cartes, dans l'ordre d'affichage. Le titre de secours sert quand /sante ne donne pas le sien.
const CARTES = [
  { id: "service", titre: "Le service répond" },
  { id: "erreurs_techniques", titre: "Réponses en erreur" },
  { id: "refus_securite", titre: "Refus de sécurité" },
  { id: "latence_p95_ms", titre: "Temps de réponse" },
  { id: "cout_24h", titre: "Coût estimé" },
  { id: "fraicheur", titre: "Fraîcheur des cours" },
  { id: "rejets_15_min", titre: "Appels rejetés" },
];

const elResume = document.getElementById("resume");
const elConnexion = document.getElementById("connexion");
const elTableau = document.getElementById("tableau");
const elCartes = document.getElementById("cartes");
const elHorodatages = document.getElementById("horodatages");
const elAPropos = document.getElementById("a-propos");
const elBouton = document.getElementById("actualiser");
const elBandeau = document.getElementById("bandeau-exercice");
const elSuspendre = document.getElementById("suspendre");
const elEtatActualisation = document.getElementById("etat-actualisation");

let enCours = false;
let cleEnEssai = null;
let minuterie = null;
let suspendu = false;   // 02/11/2026, WCAG 2.2.2 : l'exploitant peut arrêter l'actualisation automatique

// --- Les mots ----------------------------------------------------------------
function nombre(valeur, decimales) {
  return Number(valeur).toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
}

function heure(iso, avecSecondes) {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "heure inconnue";
  return date.toLocaleTimeString("fr-FR", avecSecondes ? {} : { hour: "2-digit", minute: "2-digit" });
}

function dateFr(jour) {
  const date = new Date(`${jour}T00:00:00`);
  return Number.isNaN(date.getTime()) ? "date inconnue" : date.toLocaleDateString("fr-FR");
}

function estObjet(valeur) {
  return valeur !== null && typeof valeur === "object" && !Array.isArray(valeur);
}

// La valeur d'une carte, en une phrase, et son détail (période, effectif).
function decrire(id, verdict, etat) {
  const v = verdict.valeur;
  if (id === "erreurs_techniques" || id === "refus_securite") {
    if (v === null || v === undefined) return { valeur: "Aucune question sur la période.", detail: `${verdict.fenetre_min} dernières minutes` };
    const quoi = id === "refus_securite" ? "questions refusées pour sécurité" : "réponses en erreur";
    return { valeur: `${verdict.numerateur} sur ${verdict.effectif} ${quoi} (${nombre(v * 100, 0)} %)`,
             detail: `sur les ${verdict.fenetre_min} dernières minutes` };
  }
  if (id === "latence_p95_ms") {
    if (v === null || v === undefined) return { valeur: "Aucune réponse sur la période.", detail: `${verdict.fenetre_min} dernières minutes` };
    return { valeur: `95 % des réponses en moins de ${nombre(v / 1000, 1)} s`,
             detail: `sur ${verdict.effectif} réponses, ${verdict.fenetre_min} dernières minutes` };
  }
  if (id === "cout_24h") {
    const cout = estObjet(etat.cout_24h) ? etat.cout_24h : {};
    if (v === null || v === undefined) return { valeur: "Coût inconnu : le prix n'est pas relevé.", detail: "" };
    return { valeur: Number(v).toLocaleString("fr-FR", { style: "currency", currency: cout.devise || "EUR" }),
             detail: `Coût cumulé depuis ${heure(cout.depuis, false)}, estimé au prix public du ${dateFr(cout.prix_du)}` };
  }
  if (id === "fraicheur") {
    const retards = Array.isArray(verdict.en_retard) ? verdict.en_retard : [];
    if (retards.length === 0) return { valeur: "Toutes les valeurs suivies sont à jour.", detail: "cours de bourse, par valeur" };
    const lignes = retards.slice(0, 3).map((e) => e.retard_jours_ouvres === null
      ? `${e.ticker} : aucune cotation` : `${e.ticker} : ${e.retard_jours_ouvres} jours ouvrés sans cours`);
    const reste = retards.length > 3 ? `, et ${retards.length - 3} autres` : "";
    return { valeur: lignes.join(" ; ") + reste, detail: "cours de bourse, par valeur" };
  }
  return { valeur: `${v} appels rejetés en 15 minutes`, detail: "clé refusée, saisie invalide ou trop de demandes" };
}

// Pourquoi « inconnu » : l'absence de données a sa propre phrase, jamais une consigne d'action.
function pourquoiInconnu(id, verdict) {
  if (id === "fraicheur") return "La base des cours n'a pas pu être lue.";
  if (id === "cout_24h") return "Le coût ne peut pas être estimé.";
  if (Number.isInteger(verdict.effectif) && Number.isInteger(verdict.minimum_requetes)) {
    return `Pas assez de questions pour juger (${verdict.effectif} sur ${verdict.minimum_requetes} nécessaires).`;
  }
  return "Mesure indisponible.";
}

// --- Une carte ---------------------------------------------------------------
function paragraphe(classe, texte) {
  const p = document.createElement("p");
  p.className = classe;
  p.textContent = texte;
  return p;
}

function carte(id, titre, etatCarte, lignes, consigne) {
  const article = document.createElement("article");
  article.className = `carte carte-${etatCarte}`;
  article.dataset.signal = id;
  const h3 = document.createElement("h3");
  h3.textContent = titre;
  article.append(h3, paragraphe(`etat etat-${etatCarte}`, ETATS.get(etatCarte)));
  for (const [classe, texte] of lignes) {
    if (texte) article.append(paragraphe(classe, texte));
  }
  if (consigne && (etatCarte === "attention" || etatCarte === "probleme")) {
    article.append(paragraphe("que-faire", `Que faire : ${consigne}`));
  }
  return article;
}

function carteService(serviceOk) {
  return serviceOk
    ? carte("service", "Le service répond", "sain", [["valeur", "Le service répond."]], null)
    : carte("service", "Le service répond", "probleme", [["valeur", "Le service ne répond pas."]], CONSIGNE_SERVICE);
}

function carteSignal(definition, etat) {
  const verdicts = estObjet(etat) && estObjet(etat.verdicts) ? etat.verdicts : {};
  const verdict = verdicts[definition.id];
  try {
    if (!estObjet(verdict) || !ETATS.has(verdict.etat)) throw new Error("verdict absent ou illisible");
    const titre = typeof verdict.libelle === "string" && verdict.libelle ? verdict.libelle : definition.titre;
    if (verdict.etat === "inconnu") {
      return carte(definition.id, titre, "inconnu", [["valeur", pourquoiInconnu(definition.id, verdict)]], null);
    }
    const { valeur, detail } = decrire(definition.id, verdict, etat);
    return carte(definition.id, titre, verdict.etat, [["valeur", valeur], ["detail", detail]], verdict.que_faire);
  } catch (erreur) {
    return carte(definition.id, definition.titre, "inconnu", [["valeur", "Mesure illisible."]], null);
  }
}

// --- Le rendu ----------------------------------------------------------------
function rendre(serviceOk, etat, erreurLecture) {
  while (elCartes.firstChild) elCartes.removeChild(elCartes.firstChild);
  const cartes = [carteService(serviceOk), ...CARTES.slice(1).map((d) => carteSignal(d, erreurLecture ? null : etat))];
  cartes.forEach((c) => elCartes.append(c));

  const actions = cartes.filter((c) => c.classList.contains("carte-probleme") || c.classList.contains("carte-attention")).length;
  if (erreurLecture) {
    elResume.textContent = `Le tableau de bord n'a pas pu lire les mesures (${erreurLecture}).`;
  } else if (actions > 0) {
    elResume.textContent = actions === 1 ? "1 signal demande une action." : `${actions} signaux demandent une action.`;
  } else if (cartes.some((c) => c.classList.contains("carte-inconnu"))) {
    elResume.textContent = "Mesures incomplètes : certains signaux n'ont pas assez de données pour être jugés.";
  } else {
    elResume.textContent = "Tout va bien.";
  }

  // Étape 6 : une panne simulée se dit en tête, avec qui l'a posée et pourquoi.
  const exercice = !erreurLecture && estObjet(etat) && estObjet(etat.exercice) ? etat.exercice : null;
  elBandeau.hidden = !exercice;
  elBandeau.textContent = exercice
    ? `Exercice de panne en cours depuis ${heure(exercice.depuis, false)} (${exercice.nom} : ${exercice.motif}), `
      + `fin au plus tard à ${heure(exercice.fin_au_plus_tard, false)}. Les erreurs affichées sont simulées.`
    : "";

  const morceaux = [`Tableau actualisé à ${new Date().toLocaleTimeString("fr-FR")}`];
  if (!erreurLecture && estObjet(etat) && etat.calcule_a) morceaux.push(`Mesures calculées à ${heure(etat.calcule_a, true)}`);
  if (!erreurLecture && estObjet(etat) && etat.mesures_depuis) morceaux.push(`mesures depuis ${heure(etat.mesures_depuis, false)}`);
  elHorodatages.textContent = morceaux.join(" · ");
  elAPropos.textContent = "Les taux portent sur les 15 dernières minutes ; le coût est une estimation majorée au prix public "
    + "Azure ; les seuils sont provisoires, écrits avant toute mesure du trafic réel. Les mesures repartent à zéro au "
    + "redémarrage du service.";
}

// --- Les appels --------------------------------------------------------------
async function lire(url, cle) {
  const controle = new AbortController();
  const minuteur = setTimeout(() => controle.abort(), DELAI_MS);
  try {
    return await fetch(url, { headers: cle ? { "X-API-Key": cle } : {}, signal: controle.signal });
  } finally {
    clearTimeout(minuteur);
  }
}

function montrerConnexion(message) {
  elTableau.hidden = true;
  elConnexion.hidden = false;
  elResume.textContent = message;
  document.getElementById("cle").focus();   // le clavier arrive au bon endroit, comme sur les quatre autres écrans
  if (minuterie) clearInterval(minuterie);
  minuterie = null;
}

async function actualiser() {
  if (enCours) return;
  enCours = true;
  elBouton.disabled = true;
  elBouton.textContent = "Actualisation…";
  document.body.dataset.etat = "chargement";
  try {
    const cle = cleEnEssai || sessionStorage.getItem(CLE_STOCKAGE);
    const [health, sante] = await Promise.allSettled([lire("/health", null), lire("/sante", cle)]);
    const serviceOk = health.status === "fulfilled" && health.value.ok;
    if (sante.status === "fulfilled" && (sante.value.status === 401 || sante.value.status === 403)) {
      sessionStorage.removeItem(CLE_STOCKAGE);
      cleEnEssai = null;
      montrerConnexion("Clé refusée : saisissez-la de nouveau.");
      return;
    }
    let etat = null;
    let erreurLecture = "";
    if (sante.status === "fulfilled" && sante.value.ok) {
      try {
        etat = await sante.value.json();
      } catch (erreur) {
        erreurLecture = "réponse illisible";
      }
    } else {
      erreurLecture = sante.status === "rejected"
        ? "pas de réponse en 5 secondes, ou service arrêté" : `HTTP ${sante.value.status}`;
    }
    if (cleEnEssai) {
      sessionStorage.setItem(CLE_STOCKAGE, cleEnEssai);   // la clé n'est gardée qu'après avoir fonctionné
      cleEnEssai = null;
    }
    elConnexion.hidden = true;
    elTableau.hidden = false;
    rendre(serviceOk, etat, erreurLecture);
    if (!minuterie && !suspendu) minuterie = setInterval(actualiser, INTERVALLE_MS);
  } finally {
    enCours = false;
    elBouton.disabled = false;
    elBouton.textContent = "Actualiser";
    document.body.dataset.etat = "pret";
  }
}

document.getElementById("form-cle").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  cleEnEssai = document.getElementById("cle").value.trim();
  actualiser();
});
elBouton.addEventListener("click", actualiser);

// Suspendre arrête l'actualisation automatique ; « Actualiser » reste possible à la main, sans la relancer. Reprendre
// relance une lecture aussitôt, puis toutes les 30 secondes.
elSuspendre.addEventListener("click", () => {
  suspendu = !suspendu;
  elSuspendre.setAttribute("aria-pressed", String(suspendu));
  if (suspendu) {
    if (minuterie) clearInterval(minuterie);
    minuterie = null;
    elEtatActualisation.textContent = "Actualisation automatique suspendue.";
  } else {
    elEtatActualisation.textContent = "Actualisation automatique toutes les 30 secondes.";
    if (!minuterie) minuterie = setInterval(actualiser, INTERVALLE_MS);
    actualiser();
  }
});

if (sessionStorage.getItem(CLE_STOCKAGE)) {
  actualiser();
} else {
  montrerConnexion("Saisissez la clé d'API pour voir le tableau de bord.");
  document.body.dataset.etat = "pret";
}
