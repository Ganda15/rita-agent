// =============================================================================
// L'ÉCRAN BRIEFING (refonte 001, tâche 7 ; spécification R3 ; conception § 5 à § 8).
//
// Relève de C10 : l'écran appelle `POST /briefing`, le seul point de terminaison qui expose le modèle (C9). Il lit le
// résultat dans l'ordre où RITA travaille : chiffres clés, courbe, texte, « Comprendre ce résultat », sources.
//
// ⚠️ Era doit pouvoir défendre CHAQUE ligne de ce fichier à l'oral.
//
// Les règles, chacune testée (tests/test_briefing_ui.py, tests/test_parcours_briefing_api_reelle.py) :
// - un clic donne UN SEUL envoi ; le bouton est inactif pendant la rédaction ; rien n'est relancé tout seul ;
// - un texte retenu par le garde-fou n'est JAMAIS affiché, même si la réponse le portait encore ;
// - chaque panne a son message, et une panne n'efface jamais ce qui fonctionne (trois blocs indépendants) ;
// - une réponse arrivée après une nouvelle demande est ignorée ;
// - tout texte venu de l'API passe par textContent, et un lien n'est cliquable que s'il est http(s).
// La clé et l'appel passent par commun.js (RITA.appeler) : gardée après un succès, oubliée sur 401 ou 403 (#73).
// =============================================================================

const ENDPOINT = "/briefing";
const ENDPOINT_VALEURS = "/donnees/valeurs";
const VERDICT_CONFORME = "Aucune recommandation d'achat ou de vente détectée";
const TEXTE_RETENU = "Texte retenu par le garde-fou de sortie : le modèle avait produit une formulation assimilable "
  + "à une recommandation d'achat ou de vente ; elle n'est pas diffusée.";
const NOMS_FOURNISSEURS = new Map([["foundry", "Azure AI Foundry"], ["anthropic", "Anthropic"], ["openrouter", "OpenRouter"]]);

const elStatut = document.getElementById("statut");
const elConnexion = document.getElementById("connexion");
const elDemande = document.getElementById("demande");
const elResultat = document.getElementById("resultat");
const elBouton = document.querySelector("#form-briefing button[type=submit]");

// --- Petits outils de mise en forme ------------------------------------------
function fini(valeur) {
  return typeof valeur === "number" && Number.isFinite(valeur);
}

function nombre(valeur, decimales) {
  return valeur.toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
}

// Une variation dite par le signe, la flèche ET le chiffre : jamais par la couleur seule.
function variation(valeur) {
  if (!fini(valeur)) return "indisponible";
  if (valeur === 0) return `${nombre(0, 2)} %`;
  return `${valeur > 0 ? "▲ +" : "▼ -"}${nombre(Math.abs(valeur), 2)} %`;
}

function dateFr(iso) {
  const texte = String(iso ?? "");
  return /^\d{4}-\d{2}-\d{2}/.test(texte) ? `${texte.slice(8, 10)}/${texte.slice(5, 7)}/${texte.slice(0, 4)}` : "date inconnue";
}

function pluriel(n, singulier, plurielTexte) {
  return `${n} ${n > 1 ? plurielTexte : singulier}`;
}

function lienSur(adresse) {
  try {
    const url = new URL(String(adresse));
    return url.protocol === "http:" || url.protocol === "https:" ? String(adresse) : null;
  } catch (erreur) {
    return null;
  }
}

function element(balise, texte, classe) {
  const e = document.createElement(balise);
  if (texte !== undefined) e.textContent = texte;
  if (classe) e.className = classe;
  return e;
}

// --- Les états ----------------------------------------------------------------
function afficherStatut(message, avecFocus) {
  elStatut.textContent = message;   // aria-live s'occupe de l'annonce
  if (avecFocus && message) elStatut.focus();
}

function demanderCle(message) {
  elResultat.hidden = true;
  elDemande.hidden = true;
  elConnexion.hidden = false;
  afficherStatut(message || "");
  document.getElementById("cle").focus();
}

// Venue de l'écran Indicateurs (« Demander le briefing de cette valeur ») : le code est prérempli, RIEN n'est envoyé.
// Un appel payant attend toujours un clic.
const tickerDemande = new URLSearchParams(window.location.search).get("ticker");

async function ouvrirDemande(cle) {
  elConnexion.hidden = true;
  elDemande.hidden = false;
  afficherStatut("");
  const champ = document.getElementById("ticker");
  if (tickerDemande && !champ.value && /^[A-Za-z0-9.\-]{1,16}$/.test(tickerDemande)) {
    champ.value = tickerDemande.toUpperCase();
  }
  champ.focus();
  await remplirUnivers(cle);
}

// La liste déroulante est un COMPLÉMENT : si cet appel échoue, l'écran reste utilisable. Elle ne passe pas par
// RITA.appeler : remplir une liste ne doit pas valider une clé que personne n'a encore utilisée pour un briefing.
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

// --- Une demande : trois blocs indépendants -------------------------------------
// Chaque envoi porte un numéro ; une réponse dont le numéro n'est plus le dernier est ignorée.
let demandeCourante = 0;
let enCours = false;

function viderResultat(ticker) {
  document.getElementById("valeur-resultat").textContent = ticker;
  for (const id of ["chiffre-cours", "chiffre-seance", "chiffre-mois", "verdict"]) {
    document.getElementById(id).textContent = "–";
  }
  document.getElementById("courbe").replaceChildren(element("p", "Chargement de la courbe…", "precision"));
  document.getElementById("texte").replaceChildren();
  document.getElementById("etapes").replaceChildren();
  document.getElementById("reference").textContent = "";
  document.getElementById("liste-sources").replaceChildren();
  document.getElementById("bloc-texte").hidden = true;
  document.getElementById("comprendre").hidden = true;
  document.getElementById("sources").hidden = true;
  elResultat.hidden = true;
}

async function demanderBriefing(cle, ticker) {
  if (enCours) return;   // un clic, un envoi : un second envoi pendant la rédaction est ignoré
  enCours = true;
  elBouton.disabled = true;
  const numero = ++demandeCourante;
  viderResultat(ticker);
  // Un appel au modèle dure de 5 à 15 secondes (mesuré le 03/10/2026) : le dire, sinon l'écran paraît figé.
  afficherStatut(`Rédaction en cours pour ${ticker}… Comptez quelques secondes (de 5 à 15 secondes).`);

  // La courbe et le chiffre du mois se lisent en même temps que la rédaction : ils ne dépendent pas d'elle.
  const courbe = chargerCourbe(cle, ticker, numero);
  const mois = chargerMois(cle, ticker, numero);
  try {
    await rediger(cle, ticker, numero);
  } finally {
    enCours = false;
    elBouton.disabled = false;
  }
  await Promise.allSettled([courbe, mois]);
}

async function rediger(cle, ticker, numero) {
  let reponse;
  try {
    // POST : la requête déclenche un travail (une rédaction, payante), pas une lecture.
    reponse = await RITA.appeler(`${ENDPOINT}?ticker=${encodeURIComponent(ticker)}`, { methode: "POST", cle });
  } catch (erreurReseau) {
    if (numero === demandeCourante) afficherStatut("Le serveur ne répond pas. Vérifiez que l'API est démarrée.", true);
    return;
  }
  if (numero !== demandeCourante) return;
  const reference = reponse.headers.get("X-Request-ID") || "";

  if (reponse.status === 401 || reponse.status === 403) {
    cleEnEssai = null;   // RITA.appeler a déjà oublié la clé gardée
    demanderCle("Clé d'API refusée. Saisissez-la à nouveau.");
    return;
  }
  if (reponse.status === 422) {
    // 422 : valeur absente du référentiel, refusée avant tout appel au modèle.
    elResultat.hidden = true;
    afficherStatut(`Valeur introuvable : « ${ticker} » n'est pas dans l'univers suivi.`, true);
    return;
  }
  if (reponse.status === 502) {
    // 502 : la valeur est suivie, mais aucun cours n'a été trouvé pour elle (agents/scout.py) ; le rédacteur n'est pas
    // appelé. Message distinct du 422 depuis la revue du 05/11 : « introuvable » aurait faussement accusé la saisie.
    elResultat.hidden = true;
    afficherStatut(`Données indisponibles pour « ${ticker} » : aucun cours n'a été trouvé, le briefing n'a pas été rédigé.`, true);
    return;
  }
  if (reponse.status === 503) {
    afficherStatut("Aucun fournisseur de modèle n'a répondu. Réessayez plus tard.", true);
    return;
  }
  if (reponse.status === 429) {
    const refus = await lireJson(reponse);
    afficherStatut(String(refus?.detail?.texte ?? "") || "Trop de demandes en peu de temps. Réessayez dans une minute.", true);
    return;
  }
  if (!reponse.ok) {
    afficherStatut(`Le briefing n'a pas pu être produit (erreur ${reponse.status}).`
      + (reference ? ` Référence de la requête : ${reference}.` : ""), true);
    return;
  }
  const donnees = await lireJson(reponse);
  if (!donnees) {
    afficherStatut("Le briefing n'a pas pu être produit : la réponse est illisible.", true);
    return;
  }
  afficherBriefing(donnees, reference);
  afficherStatut("");
  elResultat.hidden = false;
  elResultat.focus();   // le clavier et le lecteur d'écran arrivent sur le résultat
}

async function lireJson(reponse) {
  try {
    return await reponse.json();
  } catch (erreur) {
    return null;
  }
}

// --- Le briefing : chiffres, texte, comprendre, sources ---------------------------
function afficherBriefing(donnees, reference) {
  document.getElementById("chiffre-cours").textContent = fini(donnees.price)
    ? `${nombre(donnees.price, 2)} ${String(donnees.currency ?? "")}`.trim() : "indisponible";
  document.getElementById("chiffre-seance").textContent = variation(donnees.change_pct);

  const conforme = donnees.conforme_amf === true;
  const motifs = (donnees.motifs_amf ?? []).map(String).join(", ");
  document.getElementById("verdict").textContent = conforme
    ? VERDICT_CONFORME : `Texte retenu par le garde-fou${motifs ? ` (motifs : ${motifs})` : ""}`;

  // Le texte retenu n'est jamais affiché : si le garde-fou a refusé, on n'écrit rien de ce que la réponse contient.
  const bloc = document.getElementById("texte");
  if (conforme) {
    const paragraphes = String(donnees.briefing ?? "")
      .split(/\n\s*\n/)
      .map((p) => p.replace(/\*\*/g, "").replace(/^#+\s*/, "").trim())
      .filter((p) => p.length > 0);
    for (const p of paragraphes) {
      const el = document.createElement("p");
      el.textContent = p;
      bloc.appendChild(el);
    }
  } else {
    bloc.appendChild(element("p", TEXTE_RETENU, "texte-retenu"));
  }
  document.getElementById("bloc-texte").hidden = false;

  afficherComprendre(donnees, reference, conforme, motifs);
  afficherSources(donnees.diagnostic?.sources);
}

function afficherComprendre(donnees, reference, conforme, motifs) {
  const etapes = document.getElementById("etapes");
  const diagnostic = donnees.diagnostic;
  const ajouter = (titre, texte) => {
    const li = element("li");
    li.append(element("strong", `${titre} : `), document.createTextNode(texte));
    etapes.appendChild(li);
  };
  if (!diagnostic) {
    ajouter("Détails", "indisponibles : la réponse ne contient pas le diagnostic.");
  } else {
    ajouter("Données", decrireCours(diagnostic));
    const n = Array.isArray(diagnostic.sources) ? diagnostic.sources.length : 0;
    ajouter("Articles", n === 0 ? "aucune source fournie au modèle"
      : `${pluriel(n, "source fournie", "sources fournies")} au modèle`);
    ajouter("Modèle", decrireModele(diagnostic));
    ajouter("Garde-fou", conforme ? VERDICT_CONFORME : `texte retenu${motifs ? ` (motifs : ${motifs})` : ""}`);
    if (fini(diagnostic.duree_ms)) ajouter("Votre texte", `${nombre(diagnostic.duree_ms / 1000, 1)} s au total`);
  }
  document.getElementById("reference").textContent = reference ? `Référence de la requête : ${reference}` : "";
  document.getElementById("comprendre").hidden = false;
}

function decrireCours(diagnostic) {
  if (!diagnostic.date_cours) return "date du cours indisponible";
  const morceaux = [`cours du ${dateFr(diagnostic.date_cours)}`];
  if (fini(diagnostic.age_calendaire_jours)) {
    morceaux.push(pluriel(diagnostic.age_calendaire_jours, "jour calendaire", "jours calendaires"));
  }
  if (fini(diagnostic.jours_bourse_ecoules) && diagnostic.calendrier) {
    morceaux.push(`${pluriel(diagnostic.jours_bourse_ecoules, "jour de bourse écoulé", "jours de bourse écoulés")}`
      + ` depuis (calendrier ${diagnostic.calendrier})`);
  } else {
    morceaux.push("séances non comptées (place hors Euronext)");
  }
  return morceaux.join(" ; ");
}

function decrireModele(diagnostic) {
  const nom = (code) => NOMS_FOURNISSEURS.get(code) || String(code ?? "fournisseur inconnu");
  const modele = diagnostic.modele ? String(diagnostic.modele) : "modèle non communiqué par le fournisseur";
  const tentatives = Array.isArray(diagnostic.tentatives) ? diagnostic.tentatives : [];
  const essais = tentatives.length === 1 && tentatives[0].reussi
    ? "1er essai réussi"
    : `essais : ${tentatives.map((t) => `${nom(t.fournisseur)} : ${t.reussi ? "réussi" : "échec"}`).join(" ; ")}`;
  return `${nom(diagnostic.fournisseur)}, ${modele} (${essais})`;
}

function afficherSources(sources) {
  const liste = document.getElementById("liste-sources");
  const toutes = Array.isArray(sources) ? sources : [];
  if (toutes.length === 0) {
    liste.appendChild(element("li", "Aucune source : le texte s'appuie seulement sur les chiffres."));
  }
  for (const source of toutes) {
    const li = element("li");
    const adresse = lienSur(source.lien);
    if (adresse) {
      const a = element("a", String(source.titre ?? "Article"));
      a.href = adresse;
      a.target = "_blank";
      a.rel = "noopener noreferrer";
      li.appendChild(a);
    } else {
      li.append(element("span", String(source.titre ?? "Article")), document.createTextNode(" (lien non disponible)"));
    }
    li.appendChild(document.createTextNode(` · ${String(source.source ?? "source inconnue")} · ${dateFr(source.publie_le)}`));
    liste.appendChild(li);
  }
  document.getElementById("sources").hidden = false;
}

// --- La courbe et le chiffre du mois : chacun son bloc, chacun sa panne -------------
async function chargerCourbe(cle, ticker, numero) {
  const zone = document.getElementById("courbe");
  let cotations = null;
  try {
    const reponse = await RITA.appeler(`/donnees/cotations?ticker=${encodeURIComponent(ticker)}&limite=179`, { cle });
    if (reponse.ok) cotations = (await lireJson(reponse))?.cotations ?? null;
  } catch (erreurReseau) {
    cotations = null;
  }
  if (numero !== demandeCourante) return;   // une réponse tardive n'écrit jamais sous une autre valeur
  if (!cotations) {
    zone.replaceChildren(element("p", "Courbe indisponible pour le moment.", "precision"));
  } else {
    const dessin = GRAPHIQUES.courbe(cotations);
    zone.replaceChildren(...[dessin.svg, dessin.alternative].filter(Boolean));
  }
  elResultat.hidden = false;
}

async function chargerMois(cle, ticker, numero) {
  let valeur = null;
  try {
    const reponse = await RITA.appeler(`/donnees/indicateurs?ticker=${encodeURIComponent(ticker)}`, { cle });
    if (reponse.ok) valeur = (await lireJson(reponse))?.indicateurs?.[0]?.perf_1m_pct ?? null;
  } catch (erreurReseau) {
    valeur = null;
  }
  if (numero !== demandeCourante) return;
  document.getElementById("chiffre-mois").textContent = variation(valeur);
}

// --- DÉMARRAGE ---------------------------------------------------------------
// #73 (01/11/2026) : la clé saisie reste en mémoire, pas en sessionStorage, tant qu'aucun appel ne l'a acceptée.
let cleEnEssai = null;

document.getElementById("form-cle").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  cleEnEssai = document.getElementById("cle").value.trim();
  ouvrirDemande(cleEnEssai);
});

document.getElementById("form-briefing").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  const cle = RITA.lireCle() || cleEnEssai;
  if (!cle) {
    demanderCle("Saisissez d'abord votre clé d'API.");
    return;
  }
  demanderBriefing(cle, document.getElementById("ticker").value.trim().toUpperCase());
});

const cleMemorisee = RITA.lireCle();
// Refonte 001 (R7, décision D1) : en simulation, cet écran n'a pas encore de données d'exemple. Il ne démarre pas :
// aucun appel, aucune minuterie ; commun.js affiche « Simulation non disponible pour cet écran ».
if (window.RITA && window.RITA.estSimulation()) {
  window.RITA.suspendreEcran();
} else if (cleMemorisee) {
  ouvrirDemande(cleMemorisee);
} else {
  demanderCle();
}
