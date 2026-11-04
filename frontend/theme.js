// Le thème de l'interface (refonte 001, décision d'Era du 04/11) : sombre par défaut, clair au choix.
//
// Chargé dans <head>, avant l'affichage : le thème choisi est posé avant que la page soit dessinée, elle ne clignote
// donc pas du sombre au clair à chaque écran. Le choix vit dans sessionStorage (l'onglet courant), comme la clé, et
// jamais dans le stockage permanent du navigateur : RITA n'écrit rien qui survive à la fermeture de l'onglet.
// Sans JavaScript, la page reste sombre et le bouton reste caché (attribut hidden dans le HTML).
(function () {
  "use strict";

  var CLE_THEME = "rita_theme";
  var racine = document.documentElement;

  function lireChoix() {
    try {
      return sessionStorage.getItem(CLE_THEME);
    } catch (erreur) {
      return null;   // stockage refusé par le navigateur : le thème par défaut s'applique
    }
  }

  function appliquer(theme) {
    if (theme === "clair") {
      racine.setAttribute("data-theme", "clair");
    } else {
      racine.removeAttribute("data-theme");
    }
  }

  function estClair() {
    return racine.getAttribute("data-theme") === "clair";
  }

  // aria-pressed dit l'état ; le libellé « Thème clair » ne change pas (motif du bouton bascule, WAI-ARIA).
  function montrerEtat() {
    var bouton = document.getElementById("bascule-theme");
    if (bouton) {
      bouton.setAttribute("aria-pressed", estClair() ? "true" : "false");
    }
  }

  appliquer(lireChoix());

  // Bouton Précédent ou Suivant : le navigateur peut rendre la page depuis son cache d'aller-retour, telle qu'on l'a
  // quittée, sans relancer ce script. Le thème choisi entre-temps sur un autre écran est alors repris ici.
  window.addEventListener("pageshow", function (evenement) {
    if (evenement.persisted) {
      appliquer(lireChoix());
      montrerEtat();
    }
  });

  document.addEventListener("DOMContentLoaded", function () {
    var bouton = document.getElementById("bascule-theme");
    if (!bouton) {
      return;
    }
    montrerEtat();
    bouton.hidden = false;
    bouton.addEventListener("click", function () {
      var theme = estClair() ? "sombre" : "clair";
      appliquer(theme);
      montrerEtat();
      try {
        sessionStorage.setItem(CLE_THEME, theme);
      } catch (erreur) {
        // stockage refusé : le choix vaut pour cette page seulement
      }
    });
  });
})();
