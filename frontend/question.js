// =============================================================================
// L'ÉCRAN DE QUESTION : il parle à l'API RITA, rien d'autre (sprint 3, tâche A6).
//
// Spec CA1.1 (page protégée par la clé), CA1.2 (chaque référence montre titre, source, table, identifiant, date et
// lien), CA1.5 (la fiche s'ouvre depuis la référence), CA2.1 et CA2.4 (un refus et une panne ne se confondent pas).
//
// Même dispositif que `briefing.js` : la clé vit en sessionStorage, est oubliée sur un 403, et tout est rendu par
// textContent. Le texte de la réponse vient d'un modèle ; les titres, sources et liens viennent de flux RSS. Ce sont
// des données, jamais du code (OWASP A03).
// =============================================================================

const ENDPOINT = "/question";
const ENDPOINT_FICHE = "/donnees/articles/";
const CLE_STOCKAGE = "rita_api_key";   // partagée avec les autres écrans

// Les motifs renvoyés par l'API, dits en mots. Une Map et non un objet : un motif inattendu comme « constructor » ne
// doit pas tomber sur une propriété héritée.
const MOTIFS = new Map([
  ["OUT_OF_CORPUS", "aucun article collecté ne traite de cette question"],
  ["INTENTION_INTERDITE", "la question demande un conseil d'achat ou de vente"],
  ["ABSTENTION", "les articles retrouvés ne suffisent pas pour répondre"],
  ["CITATIONS_INVALIDES", "la réponse produite ne citait pas correctement ses sources"],
  ["SORTIE_NON_CONFORME", "la réponse produite a été retenue par le garde-fou AMF"],
  ["FOURNISSEUR_INDISPONIBLE", "le fournisseur du modèle ne répond pas"],
  ["REPONSE_TRONQUEE", "la réponse du modèle était incomplète"],
  ["FORMAT_INVALIDE", "la réponse du modèle n'avait pas le format attendu"],
  ["ERREUR_INTERNE", "erreur interne du service"],
]);

// --- Les éléments ------------------------------------------------------------
const elStatut = document.getElementById("statut");
const elConnexion = document.getElementById("connexion");
const elDemande = document.getElementById("demande");
const elRefus = document.getElementById("refus");
const elErreur = document.getElementById("erreur");
const elResultat = document.getElementById("resultat");
const elFiche = document.getElementById("fiche");

function afficherStatut(message) {
  elStatut.textContent = message;   // aria-live s'occupe de l'annonce
}

function toutMasquer() {
  elRefus.hidden = true;
  elErreur.hidden = true;
  elResultat.hidden = true;
  elFiche.hidden = true;
  document.getElementById("reference-requete").textContent = "";
}

function entetes(cle) {
  return { "X-API-Key": cle };
}

function libelleMotif(motif) {
  const code = String(motif ?? "");
  return MOTIFS.has(code) ? `${MOTIFS.get(code)} (${code})` : code;
}

function dateLisible(valeur) {
  if (!valeur) return "date inconnue";
  const date = new Date(valeur);
  return Number.isNaN(date.getTime())
    ? String(valeur)
    : date.toLocaleString("fr-FR", { dateStyle: "long", timeStyle: "short" });
}

// Seconde barrière, après le filtre de l'API : un lien n'est créé que s'il est http ou https avec un hôte. Une
// adresse relative, un « javascript: » ou un « data: » ne deviennent jamais cliquables.
function lienSur(lien) {
  try {
    const url = new URL(String(lien ?? ""));
    return (url.protocol === "http:" || url.protocol === "https:") && url.hostname !== "" ? url.href : "";
  } catch (erreur) {
    return "";
  }
}

function lienExterne(adresse, texte) {
  const a = document.createElement("a");
  a.href = adresse;
  a.textContent = texte;
  a.target = "_blank";
  a.rel = "noopener noreferrer";   // l'article ouvert n'a aucune prise sur cette page
  return a;
}

function demanderCle(message) {
  toutMasquer();
  elDemande.hidden = true;
  elConnexion.hidden = false;
  afficherStatut(message || "");
  document.getElementById("cle").focus();
}

function ouvrirDemande() {
  elConnexion.hidden = true;
  elDemande.hidden = false;
  afficherStatut("");
  document.getElementById("question").focus();
}

async function lireJson(reponse) {
  try {
    return await reponse.json();
  } catch (erreur) {
    return null;
  }
}

// --- LA QUESTION -------------------------------------------------------------
async function poserQuestion(cle, question) {
  toutMasquer();
  // Recherche puis rédaction : quelques secondes. Sans ce message, l'écran paraît figé.
  afficherStatut("Recherche dans les articles, puis rédaction de la réponse… Comptez quelques secondes.");

  let reponse;
  try {
    reponse = await fetch(ENDPOINT, {
      method: "POST",
      headers: { ...entetes(cle), "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
  } catch (erreurReseau) {
    afficherStatut("Le serveur ne répond pas. Vérifiez que l'API est démarrée.");
    return;
  }

  if (reponse.status === 403) {
    // Une clé refusée n'est pas une panne : on l'oublie et on la redemande.
    sessionStorage.removeItem(CLE_STOCKAGE);
    demanderCle("Clé d'API refusée. Saisissez-la à nouveau.");
    return;
  }
  if (reponse.status === 422) {
    afficherStatut("La question doit compter de 3 à 500 caractères.");
    return;
  }

  const corps = await lireJson(reponse);
  // L'identifiant de requête est le même dans le journal de l'API et dans la trace : à citer pour signaler un
  // problème. Il ne contient rien de la question.
  const requestId = reponse.headers.get("X-Request-ID");
  document.getElementById("reference-requete").textContent = requestId
    ? `Référence de la requête : ${requestId}`
    : "";
  afficherStatut("");

  // 503 : panne du fournisseur ou réponse inexploitable ; 500 : erreur imprévue. Les deux sont des ERREURS, montrées
  // dans leur propre encart, jamais comme un refus.
  if (reponse.status === 503 || !reponse.ok || corps === null) {
    afficherErreur(corps, reponse.status);
    return;
  }

  sessionStorage.setItem(CLE_STOCKAGE, cle);   // la clé n'est gardée qu'après avoir fonctionné
  if (corps.statut === "refus") {
    afficherRefus(corps);
  } else if (corps.statut === "reponse") {
    afficherReponse(corps, cle);
  } else {
    afficherErreur(corps, reponse.status);
  }
}

function afficherRefus(corps) {
  document.getElementById("texte-refus").textContent = String(corps.texte ?? "");
  document.getElementById("motif-refus").textContent = `Motif : ${libelleMotif(corps.motif)}.`;
  elRefus.hidden = false;
}

function afficherErreur(corps, statutHttp) {
  document.getElementById("texte-erreur").textContent =
    String(corps?.texte ?? "Le service n'a pas pu répondre pour le moment. Réessayez plus tard.");
  const motif = corps?.motif ? `Motif : ${libelleMotif(corps.motif)}. ` : "";
  document.getElementById("motif-erreur").textContent = `${motif}Code HTTP ${statutHttp}.`;
  elErreur.hidden = false;
}

function afficherReponse(corps, cle) {
  // Le texte du modèle, en paragraphes, par textContent : un « <script> » reste affiché comme du texte.
  const bloc = document.getElementById("texte-reponse");
  bloc.replaceChildren();
  const paragraphes = String(corps.texte ?? "")
    .split(/\n\s*\n/)
    .map((p) => p.trim())
    .filter((p) => p.length > 0);
  for (const p of paragraphes) {
    const el = document.createElement("p");
    el.textContent = p;
    bloc.appendChild(el);
  }

  // Les références viennent de l'API, donc des données stockées : jamais du texte du modèle (CA1.4).
  const liste = document.getElementById("references");
  liste.replaceChildren();
  for (const reference of corps.references ?? []) {
    const item = document.createElement("li");

    const titre = document.createElement("strong");
    titre.textContent = `[${reference.n}] ${reference.titre}`;
    item.appendChild(titre);

    const details = document.createElement("p");
    details.className = "precision";
    details.textContent = `${reference.source} · table ${reference.table}, identifiant ${reference.id}`
      + ` · publié le ${dateLisible(reference.date)}`;
    item.appendChild(details);

    const adresse = lienSur(reference.lien);
    if (adresse) {
      item.appendChild(lienExterne(adresse, "Lire l'article d'origine"));
    } else {
      const sansLien = document.createElement("span");
      sansLien.textContent = "Lien d'origine non disponible.";
      item.appendChild(sansLien);
    }

    item.appendChild(document.createTextNode(" "));
    const bouton = document.createElement("button");
    bouton.type = "button";
    bouton.textContent = `Voir la fiche de la source ${reference.n}`;
    bouton.addEventListener("click", () => ouvrirFiche(cle, reference.id));
    item.appendChild(bouton);

    liste.appendChild(item);
  }

  // L'index interrogé : son empreinte dit sur quel état du corpus la réponse a été faite.
  const index = corps.index;
  document.getElementById("index-servi").textContent = index
    ? `Index interrogé : ${index.nb_articles} articles, empreinte ${String(index.empreinte ?? "").slice(0, 12)},`
      + ` construit le ${dateLisible(index.construit_le)}.`
    : "";

  elResultat.hidden = false;
}

// --- LA FICHE D'UNE SOURCE (CA1.5) ---------------------------------------------
async function ouvrirFiche(cle, id) {
  elFiche.hidden = true;
  afficherStatut("Ouverture de la fiche…");

  let reponse;
  try {
    reponse = await fetch(`${ENDPOINT_FICHE}${encodeURIComponent(id)}`, { headers: entetes(cle) });
  } catch (erreurReseau) {
    afficherStatut("Le serveur ne répond pas. Vérifiez que l'API est démarrée.");
    return;
  }
  if (reponse.status === 403) {
    sessionStorage.removeItem(CLE_STOCKAGE);
    demanderCle("Clé d'API refusée. Saisissez-la à nouveau.");
    return;
  }
  if (reponse.status === 404) {
    afficherStatut("Cet article n'est pas diffusable ou n'existe plus dans la base.");
    return;
  }
  const fiche = await lireJson(reponse);
  if (!reponse.ok || fiche === null) {
    afficherStatut(`Erreur ${reponse.status} : la fiche n'a pas pu être lue.`);
    return;
  }
  afficherStatut("");
  afficherFiche(fiche);
}

function afficherFiche(fiche) {
  const liste = document.getElementById("fiche-donnees");
  liste.replaceChildren();
  const lignes = [
    ["Table", fiche.table],
    ["Identifiant", fiche.id],
    ["Titre", fiche.titre],
    ["Source", fiche.source],
    ["Publié le", dateLisible(fiche.publie_le)],
    ["Collecté le", dateLisible(fiche.collecte_le)],
  ];
  for (const [terme, valeur] of lignes) {
    const dt = document.createElement("dt");
    dt.textContent = terme;
    const dd = document.createElement("dd");
    dd.textContent = String(valeur ?? "");
    liste.append(dt, dd);
  }
  const dt = document.createElement("dt");
  dt.textContent = "Lien d'origine";
  const dd = document.createElement("dd");
  const adresse = lienSur(fiche.lien);
  dd.appendChild(adresse ? lienExterne(adresse, adresse) : document.createTextNode("non disponible"));
  liste.append(dt, dd);

  document.getElementById("fiche-extrait").textContent = String(fiche.extrait ?? "");
  elFiche.hidden = false;
  elFiche.focus();   // le clavier et le lecteur d'écran arrivent sur la fiche
}

// --- DÉMARRAGE ---------------------------------------------------------------
document.getElementById("form-cle").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  sessionStorage.setItem(CLE_STOCKAGE, document.getElementById("cle").value.trim());
  ouvrirDemande();
});

document.getElementById("form-question").addEventListener("submit", (evenement) => {
  evenement.preventDefault();
  const cle = sessionStorage.getItem(CLE_STOCKAGE);
  if (!cle) {
    demanderCle("Saisissez d'abord votre clé d'API.");
    return;
  }
  poserQuestion(cle, document.getElementById("question").value.trim());
});

if (sessionStorage.getItem(CLE_STOCKAGE)) {
  ouvrirDemande();
} else {
  demanderCle();
}
