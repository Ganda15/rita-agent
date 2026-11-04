// =============================================================================
// CE QUE LES CINQ ÉCRANS PARTAGENT (refonte 001, tâche 5 ; exigences R5 et R7).
//
// window.RITA porte :
// - la clé d'API : en sessionStorage (l'onglet courant), jamais dans le stockage permanent du navigateur ; gardée
//   seulement après une réponse réussie, oubliée sur un 401 ou un 403 (correctif #73) ;
// - le mode simulation, pour répéter la démonstration : un choix explicite (bouton « Mode simulation » de l'en-tête),
//   le mode réel par défaut ; une mention permanente tant qu'il est actif.
//
// En simulation, rien ne part vers RITA : un écran sans données d'exemple se suspend (décision D1), et ce fichier
// refuse en plus tout appel vers une route de RITA. Changer de mode recharge la page, ce qui efface les résultats
// affichés dans les deux sens (R7, critère 7). Chargé avant le script de chaque écran.
// =============================================================================
(function () {
  "use strict";

  var CLE_STOCKAGE = "rita_api_key";       // partagée avec les écrans d'avant la refonte
  var CLE_SIMULATION = "rita_simulation";
  var MENTION = "Simulation : données d'exemple, aucun modèle appelé";
  var ROUTES_RITA = ["/briefing", "/question", "/donnees", "/sante", "/health", "/audit", "/exercice"];

  function lire(cle) {
    try {
      return sessionStorage.getItem(cle);
    } catch (erreur) {
      return null;   // stockage refusé par le navigateur
    }
  }

  function ecrire(cle, valeur) {
    try {
      if (valeur === null) {
        sessionStorage.removeItem(cle);
      } else {
        sessionStorage.setItem(cle, valeur);
      }
    } catch (erreur) {
      // stockage refusé : la clé ou le mode valent pour cette page seulement
    }
  }

  // --- La clé ----------------------------------------------------------------
  function lireCle() { return lire(CLE_STOCKAGE); }
  function garderCle(cle) { ecrire(CLE_STOCKAGE, cle); }
  function oublierCle() { ecrire(CLE_STOCKAGE, null); }

  // Les clés refusées pendant la vie de la page. Deux appels partent souvent ensemble avec la même clé : si l'un est
  // refusé et que l'autre réussit APRÈS, le succès ne doit pas regarder la clé refusée (trouvé le 04/11).
  var clesRefusees = new Set();

  // Un appel à RITA avec la clé. La clé n'est gardée qu'après une réponse réussie, et oubliée sur 401 ou 403 : une clé
  // refusée ne reste jamais en mémoire, une clé jamais vérifiée n'y entre pas (#73).
  async function appeler(chemin, options) {
    var reglages = options || {};
    var cle = reglages.cle || lireCle();
    var entetes = {};
    if (cle) {
      entetes["X-API-Key"] = cle;
    }
    var reponse = await fetch(chemin, { method: reglages.methode || "GET", headers: entetes });
    if (reponse.status === 401 || reponse.status === 403) {
      if (cle) {
        clesRefusees.add(cle);
      }
      oublierCle();
    } else if (reponse.ok && cle && !clesRefusees.has(cle)) {
      garderCle(cle);
    }
    return reponse;
  }

  // --- Le mode simulation -----------------------------------------------------
  function estSimulation() { return lire(CLE_SIMULATION) === "oui"; }

  function basculerSimulation(actif) {
    ecrire(CLE_SIMULATION, actif ? "oui" : null);
    window.location.reload();
  }

  function estRouteRita(adresse) {
    var url;
    try {
      url = new URL(typeof adresse === "string" ? adresse : adresse.url, window.location.href);
    } catch (erreur) {
      return true;   // une adresse illisible ne part pas
    }
    if (url.origin !== window.location.origin) {
      return true;   // aucun autre site non plus
    }
    return ROUTES_RITA.some(function (route) {
      return url.pathname === route || url.pathname.indexOf(route + "/") === 0;
    });
  }

  // Deuxième barrière, posée avant le script de l'écran : même un appel oublié ne part pas vers RITA en simulation.
  if (estSimulation()) {
    var fetchDuNavigateur = window.fetch.bind(window);
    window.fetch = function (adresse, options) {
      if (estRouteRita(adresse)) {
        return Promise.reject(new Error("Simulation : aucun appel à RITA."));
      }
      return fetchDuNavigateur(adresse, options);
    };
  }

  // Bouton Précédent ou Suivant (04/11/2026, revue de la PR #180) : le navigateur peut rendre la page depuis son cache
  // d'aller-retour sans relancer ce script, et la barrière ci-dessus resterait celle du chargement. Si le mode a changé
  // entre-temps sur un autre écran, la page est rechargée une fois, dans le bon mode ; sinon, elle est gardée telle quelle.
  // Pas de boucle : après ce rechargement, le mode du chargement est celui de la session.
  var simulationAuChargement = estSimulation();
  window.addEventListener("pageshow", function (evenement) {
    if (evenement.persisted && estSimulation() !== simulationAuChargement) {
      window.location.reload();
    }
  });

  function afficherMentionSimulation() {
    if (!estSimulation() || document.getElementById("mention-simulation")) {
      return;
    }
    var entete = document.querySelector("header.entete");
    if (!entete) {
      return;
    }
    var mention = document.createElement("p");
    mention.id = "mention-simulation";
    mention.className = "mention-simulation";
    mention.textContent = MENTION;
    entete.appendChild(mention);
  }

  // Un écran sans données d'exemple (décision D1) : rien de réel sous la mention « Simulation ». Son contenu est masqué
  // (le titre reste), un bloc dit pourquoi et propose d'en sortir, et aucun formulaire ne s'envoie, clavier compris.
  function suspendreEcran() {
    var principal = document.querySelector("main");
    if (!principal || document.getElementById("suspension")) {
      return;
    }
    var bloc = document.createElement("section");
    bloc.id = "suspension";
    bloc.className = "suspension";
    bloc.setAttribute("aria-labelledby", "suspension-titre");
    var titre = document.createElement("h2");
    titre.id = "suspension-titre";
    titre.textContent = "Simulation non disponible pour cet écran";
    var texte = document.createElement("p");
    texte.textContent = "Cet écran n'a pas de données d'exemple. Tant que la simulation est active, il n'appelle pas "
      + "RITA et n'affiche aucune donnée réelle.";
    var bouton = document.createElement("button");
    bouton.type = "button";
    bouton.id = "quitter-simulation";
    bouton.textContent = "Quitter la simulation";
    bouton.addEventListener("click", function () { basculerSimulation(false); });
    bloc.append(titre, texte, bouton);
    principal.appendChild(bloc);
    principal.classList.add("simulation-suspendue");
    // La phase de capture passe avant les gestionnaires de l'écran : l'envoi est arrêté avant eux.
    document.addEventListener("submit", function (evenement) {
      evenement.preventDefault();
      evenement.stopImmediatePropagation();
    }, true);
  }

  function preparerEntete() {
    var bouton = document.getElementById("bascule-simulation");
    if (bouton) {
      bouton.setAttribute("aria-pressed", estSimulation() ? "true" : "false");
      bouton.hidden = false;
      bouton.addEventListener("click", function () { basculerSimulation(!estSimulation()); });
    }
    afficherMentionSimulation();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", preparerEntete);
  } else {
    preparerEntete();
  }

  window.RITA = {
    lireCle: lireCle,
    garderCle: garderCle,
    oublierCle: oublierCle,
    appeler: appeler,
    estSimulation: estSimulation,
    basculerSimulation: basculerSimulation,
    afficherMentionSimulation: afficherMentionSimulation,
    suspendreEcran: suspendreEcran,
  };
})();
