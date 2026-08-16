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

  let reponse;
  try {
    reponse = await fetch(ENDPOINT, { headers: { "X-API-Key": cle } });
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
  // On ne mémorise la clé qu'APRÈS l'avoir vue fonctionner.
  sessionStorage.setItem(CLE_STOCKAGE, cle);
  afficher(donnees);
}

// --- LE RENDU ----------------------------------------------------------------
function afficher(donnees) {
  document.getElementById("total").textContent = euro.format(nb(donnees.total_eur));
  document.getElementById("nb-lignes").textContent =
    ` · ${donnees.nb} ligne${donnees.nb > 1 ? "s" : ""}`;

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
    ajouterCellule(tr, euro.format(nb(p.investi_eur)));
    ajouterCellule(tr, euro.format(nb(p.valorisation_eur)));
    ajouterCellule(tr, textePerf);

    corps.appendChild(tr);
  }

  const date = donnees.positions[0]?.date_cours;
  if (date) {
    document.getElementById("legende").textContent =
      `Portefeuille valorisé — cours du ${date}`;
  }

  afficherStatut("");
  elResultat.hidden = false;
}

function ajouterCellule(tr, texte, balise = "td") {
  const cellule = document.createElement(balise);
  if (balise === "th") cellule.setAttribute("scope", "row");   // RGAA 5.7
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
if (cleMemorisee) {
  chargerPortefeuille(cleMemorisee);
} else {
  demanderCle();
}
