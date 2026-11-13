// =============================================================================
// GRAPHIQUES : des fonctions pures qui dessinent en SVG (refonte 001, tâche 6 ; R1, R2, R3).
//
// Chaque fonction reçoit des données et rend { svg, alternative } : le dessin (null s'il n'y a rien à dessiner) et
// une alternative en texte qui porte les mêmes chiffres, pour qui ne voit pas le dessin (WCAG, images complexes).
// Aucun appel réseau, aucune bibliothèque, aucun HTML inséré : les éléments sont créés un à un
// (document.createElementNS) et tout texte passe par textContent ; un nombre n'est écrit que s'il est fini.
//
// Le seul calcul fait par l'écran (spécification § 5) : les séries des moyennes mobiles 20 et 50 séances, pour tracer
// leurs courbes. Même règle que la base (db/indicateurs.sql) : la fenêtre inclut la séance du jour, et la moyenne
// n'existe qu'avec exactement 20 (ou 50) séances. RSI, poids et performances viennent du serveur, jamais d'ici.
// =============================================================================
(function () {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";
  var SEANCES_AFFICHEES = 130;   // 179 lues : les 130 dernières ont une moyenne 50 séances complète

  // --- Petits outils ---------------------------------------------------------
  function fini(valeur) {
    return typeof valeur === "number" && isFinite(valeur);
  }

  // Un cours lu dans l'API. /donnees/cotations rend `cloture` en texte (« 401.5000 », le NUMERIC de PostgreSQL, mesuré
  // le 04/11) : un décimal écrit ainsi devient un nombre ; tout autre texte (« illisible », « 4e2 », espaces) vaut null.
  function lireNombre(valeur) {
    if (fini(valeur)) {
      return valeur;
    }
    if (typeof valeur === "string" && /^-?\d+(\.\d+)?$/.test(valeur)) {
      return Number(valeur);
    }
    return null;
  }

  function element(nom, attributs) {
    var e = document.createElementNS(NS, nom);
    Object.keys(attributs || {}).forEach(function (cle) {
      var valeur = attributs[cle];
      if (typeof valeur === "number" && !isFinite(valeur)) {
        return;   // un attribut numérique n'est écrit que s'il est fini
      }
      e.setAttribute(cle, String(valeur));
    });
    return e;
  }

  function texteSvg(x, y, contenu, attributs) {
    var t = element("text", Object.assign({ x: arrondi(x), y: arrondi(y) }, attributs || {}));
    t.textContent = contenu;
    return t;
  }

  function arrondi(v) {
    return Math.round(v * 10) / 10;
  }

  function nombre(valeur, decimales) {
    return valeur.toLocaleString("fr-FR", { minimumFractionDigits: decimales, maximumFractionDigits: decimales });
  }

  function signe(valeur, decimales) {
    if (valeur === 0) {
      return nombre(0, decimales) + " %";
    }
    return (valeur > 0 ? "+" : "-") + nombre(Math.abs(valeur), decimales) + " %";
  }

  function dateFr(iso) {
    return iso.slice(8, 10) + "/" + iso.slice(5, 7) + "/" + iso.slice(0, 4);
  }

  function alternative(lignes) {
    var bloc = document.createElement("div");
    bloc.className = "alternative-graphique";
    lignes.forEach(function (ligne) {
      var p = document.createElement("p");
      p.textContent = ligne;
      bloc.appendChild(p);
    });
    return bloc;
  }

  // `type` donne la classe de taille (graphique-courbe, -anneau, -barres, -jauge) : un anneau de 160 unités ne doit pas
  // s'étirer sur toute la largeur d'une carte.
  function cadre(largeur, hauteur, resume, type) {
    return element("svg", { viewBox: "0 0 " + largeur + " " + hauteur, class: "graphique graphique-" + type, role: "img",
                            "aria-label": resume });
  }

  // --- La moyenne mobile, règle de la base ------------------------------------
  function moyenneMobile(valeurs, n) {
    return valeurs.map(function (_valeur, i) {
      if (i < n - 1) {
        return null;
      }
      var fenetre = valeurs.slice(i - n + 1, i + 1);
      if (!fenetre.every(fini)) {
        return null;
      }
      return fenetre.reduce(function (somme, v) { return somme + v; }, 0) / n;
    });
  }

  // --- L'échelle des prix : des valeurs rondes à pas régulier -------------------
  // Oral blanc du 13/11 : « des graphiques sans axes ni échelle ». Le pas vaut 1, 2, 2,5 ou 5 fois une puissance de 10,
  // pour environ quatre intervalles ; l'échelle est élargie aux graduations qui encadrent les données, si bien que le
  // plus bas et le plus haut du dessin sont écrits.
  function graduations(bas, haut) {
    var brut = (haut - bas) / 4;
    var puissance = Math.pow(10, Math.floor(Math.log10(brut)));
    var r = brut / puissance;
    var pas = (r <= 1 ? 1 : r <= 2 ? 2 : r <= 2.5 ? 2.5 : r <= 5 ? 5 : 10) * puissance;
    var premier = Math.floor(bas / pas + 1e-9), dernier = Math.ceil(haut / pas - 1e-9);
    var decimales = 0;
    while (decimales < 4 && Math.abs(Math.round(pas * Math.pow(10, decimales)) - pas * Math.pow(10, decimales)) > 1e-6) {
      decimales += 1;
    }
    var valeurs = [];
    for (var k = premier; k <= dernier; k += 1) {
      valeurs.push(Math.round(k * pas * 1e6) / 1e6);
    }
    return { valeurs: valeurs, decimales: decimales };
  }

  // Les séances datées sur l'axe : la première, la dernière et jusqu'à trois intermédiaires, également réparties.
  function indicesDates(n) {
    var cible = Math.min(5, n), indices = [];
    for (var k = 0; k < cible; k += 1) {
      var i = cible === 1 ? 0 : Math.round(k * (n - 1) / (cible - 1));
      if (indices.indexOf(i) === -1) {
        indices.push(i);
      }
    }
    return indices;
  }

  // Sur un écran étroit, une graduation sur deux s'efface ; la première et la dernière restent toujours.
  function classeGraduation(k, total, sorte) {
    var secondaire = k !== 0 && k !== total - 1 && k % 2 === 1;
    return "etiquette graduation graduation-" + sorte + (secondaire ? " secondaire" : "");
  }

  // --- La courbe du cours, avec ses moyennes 20 et 50 séances -----------------
  // `options.devise` : le code ISO lu dans les données par l'écran (/donnees/cotations ne la rend pas) ; jamais devinée.
  function courbe(cotations, options) {
    var devise = options && /^[A-Z]{3}$/.test(String(options.devise)) ? String(options.devise) : null;
    var ecartees = 0;
    var valides = [];
    (cotations || []).forEach(function (c) {
      var cloture = c ? lireNombre(c.cloture) : null;
      if (cloture !== null && /^\d{4}-\d{2}-\d{2}$/.test(String(c.date_seance))) {
        valides.push({ date: String(c.date_seance), cloture: cloture });
      } else {
        ecartees += 1;
      }
    });
    // L'API rend la séance la plus récente d'abord : on remet les dates dans l'ordre avant tout calcul.
    valides.sort(function (a, b) { return a.date < b.date ? -1 : (a.date > b.date ? 1 : 0); });
    var noteEcartees = ecartees ? [ecartees + (ecartees > 1 ? " séances écartées" : " séance écartée")
                                   + " (cours absent ou illisible)."] : [];
    if (valides.length === 0) {
      return { svg: null, alternative: alternative(["Aucun historique de cotation disponible."].concat(noteEcartees)) };
    }

    var clotures = valides.map(function (s) { return s.cloture; });
    var mm20 = moyenneMobile(clotures, 20);
    var mm50 = moyenneMobile(clotures, 50);
    var debut = Math.max(0, valides.length - SEANCES_AFFICHEES);
    var visibles = valides.slice(debut);
    var vmm20 = mm20.slice(debut);
    var vmm50 = mm50.slice(debut);

    var coursVisibles = visibles.map(function (s) { return s.cloture; });
    var plusBas = Math.min.apply(null, coursVisibles);
    var plusHaut = Math.max.apply(null, coursVisibles);
    var echelle = coursVisibles.concat(vmm20.filter(fini), vmm50.filter(fini));
    var bas = Math.min.apply(null, echelle);
    var haut = Math.max.apply(null, echelle);
    if (bas === haut) {   // un cours constant : une ligne plate au milieu, jamais une division par zéro
      bas -= 1;
      haut += 1;
    }
    var echelleDesPrix = graduations(bas, haut);
    bas = echelleDesPrix.valeurs[0];
    haut = echelleDesPrix.valeurs[echelleDesPrix.valeurs.length - 1];

    // `dessus` laisse la place à la légende et à l'unité, agrandies sur un écran étroit, au-dessus de la plus haute
    // graduation (rendu vérifié à 412 px le 13/11).
    var L = 640, H = 240, gauche = 12, droite = 84, dessus = 38, dessous = 34;
    var largeurUtile = L - gauche - droite, hauteurUtile = H - dessus - dessous;
    function x(i) {
      return visibles.length === 1 ? gauche + largeurUtile / 2 : gauche + i * largeurUtile / (visibles.length - 1);
    }
    function y(v) {
      return dessus + (haut - v) * hauteurUtile / (haut - bas);
    }

    var premiere = dateFr(visibles[0].date), derniere = dateFr(visibles[visibles.length - 1].date);
    var svg = cadre(L, H, "Cours du " + premiere + " au " + derniere + ", " + visibles.length + " séances", "courbe");

    function trace(valeurs, serie, classe) {
      var points = [];
      valeurs.forEach(function (v, i) {
        if (fini(v)) {
          points.push(arrondi(x(i)) + "," + arrondi(y(v)));
        }
      });
      if (points.length === 0) {
        return false;
      }
      if (points.length === 1) {
        var xy = points[0].split(",");
        svg.appendChild(element("circle", { cx: xy[0], cy: xy[1], r: 3, class: classe, "data-serie": serie }));
      } else {
        svg.appendChild(element("polyline", { points: points.join(" "), class: classe, "data-serie": serie }));
      }
      return true;
    }

    // Les axes d'abord, sous les courbes : une ligne de grille par graduation de prix, l'axe des prix à droite (comme
    // sur un graphique boursier), l'axe des dates en bas.
    var basZone = H - dessous, axePrix = L - droite;
    var textesPrix = echelleDesPrix.valeurs.map(function (v) { return nombre(v, echelleDesPrix.decimales); });
    echelleDesPrix.valeurs.forEach(function (v, k) {
      svg.appendChild(element("line", { x1: gauche, y1: arrondi(y(v)), x2: axePrix, y2: arrondi(y(v)), class: "grille" }));
      svg.appendChild(element("line", { x1: axePrix, y1: arrondi(y(v)), x2: axePrix + 4, y2: arrondi(y(v)), class: "axe" }));
      svg.appendChild(texteSvg(axePrix + 8, y(v) + 4, textesPrix[k],
                               { class: classeGraduation(k, textesPrix.length, "prix") }));
    });
    svg.appendChild(element("line", { x1: axePrix, y1: dessus, x2: axePrix, y2: basZone, class: "axe axe-y" }));
    svg.appendChild(element("line", { x1: gauche, y1: basZone, x2: axePrix, y2: basZone, class: "axe axe-x" }));
    var indices = indicesDates(visibles.length);
    var textesDates = indices.map(function (i) { return dateFr(visibles[i].date); });
    indices.forEach(function (i, k) {
      var ancrage = indices.length === 1 ? "middle" : (k === 0 ? "start" : (k === indices.length - 1 ? "end" : "middle"));
      svg.appendChild(element("line", { x1: arrondi(x(i)), y1: basZone, x2: arrondi(x(i)), y2: basZone + 4, class: "axe" }));
      svg.appendChild(texteSvg(x(i), H - 12, textesDates[k],
                               { class: classeGraduation(k, indices.length, "date"), "text-anchor": ancrage }));
    });

    trace(coursVisibles, "cours", "trace-cours");
    var avec20 = trace(vmm20, "mm20", "trace-mm20");
    var avec50 = trace(vmm50, "mm50", "trace-mm50");

    // La légende, toujours lisible (agrandie sur un écran étroit), et l'unité des prix quand l'écran la connaît.
    var legende = [["Cours", "trace-cours"]];
    if (avec20) { legende.push(["MM20", "trace-mm20"]); }
    if (avec50) { legende.push(["MM50", "trace-mm50"]); }
    legende.forEach(function (entree, k) {
      var x0 = gauche + k * 120;
      svg.appendChild(element("line", { x1: x0, y1: 12, x2: x0 + 22, y2: 12, class: entree[1] }));
      svg.appendChild(texteSvg(x0 + 28, 16, entree[0], { class: "etiquette legende" }));
    });
    if (devise) {
      svg.appendChild(texteSvg(L - 4, 16, "Prix en " + devise, { class: "etiquette legende unite", "text-anchor": "end" }));
    }

    var lignes = ["Du " + premiere + " au " + derniere + " : " + visibles.length + " séances affichées"
                  + (valides.length > visibles.length ? " sur " + valides.length + " lues." : "."),
                  "Dernier cours : " + nombre(coursVisibles[coursVisibles.length - 1], 2)
                  + " ; plus bas : " + nombre(plusBas, 2) + " ; plus haut : " + nombre(plusHaut, 2) + "."];
    var dernier20 = mm20[mm20.length - 1], dernier50 = mm50[mm50.length - 1];
    if (!fini(dernier20) && !avec20) {
      lignes.push("Courbe seule : moyennes indisponibles (moins de 20 séances).");
    } else if (!avec50) {
      lignes.push("Moyenne 20 séances : " + nombre(dernier20, 2) + " ; moyenne 50 indisponible (moins de 50 séances).");
    } else {
      lignes.push("Moyenne 20 séances : " + nombre(dernier20, 2) + " ; moyenne 50 séances : " + nombre(dernier50, 2) + ".");
    }
    // Les mêmes graduations qu'à l'écran : personne n'est privé d'un chiffre du dessin.
    lignes.push("Échelle des prix" + (devise ? " en " + devise : "") + " : " + textesPrix.join(" ; ") + ".");
    lignes.push("Dates de l'axe : " + textesDates.join(", ") + ".");
    return { svg: svg, alternative: alternative(lignes.concat(noteEcartees)) };
  }

  // --- L'anneau des poids du portefeuille -------------------------------------
  function anneau(poids) {
    var lignes = (poids || []).map(function (p) { return { nom: String(p && p.nom), poids: p && p.poids_pct }; });
    var parts = lignes.filter(function (l) { return fini(l.poids) && l.poids > 0; });
    if (parts.length === 0) {
      return { svg: null, alternative: alternative(["Répartition non calculable : aucun poids disponible."]) };
    }
    var total = parts.reduce(function (s, l) { return s + l.poids; }, 0);
    var rayon = 60, circonference = 2 * Math.PI * rayon, decalage = 0;
    var svg = cadre(160, 160, "Répartition du portefeuille en " + parts.length + " lignes", "anneau");
    parts.forEach(function (l, k) {
      var longueur = circonference * l.poids / total;
      var cercle = element("circle", { cx: 80, cy: 80, r: rayon, class: "part part-" + (k % 6), "data-serie": "part",
                                       "stroke-dasharray": arrondi(longueur) + " " + arrondi(circonference - longueur),
                                       "stroke-dashoffset": arrondi(-decalage), transform: "rotate(-90 80 80)" });
      var titre = element("title", {});
      titre.textContent = l.nom + " : " + nombre(l.poids, 1) + " %";
      cercle.appendChild(titre);
      svg.appendChild(cercle);
      decalage += longueur;
    });
    var textes = ["Répartition du portefeuille :"].concat(lignes.map(function (l) {
      return l.nom + " : " + (fini(l.poids) ? nombre(l.poids, 1) + " %" : "poids non disponible");
    }));
    return { svg: svg, alternative: alternative(textes) };
  }

  // --- Les barres de gain ou de perte -----------------------------------------
  function barres(lignes) {
    var donnees = (lignes || []).map(function (l) { return { nom: String(l && l.nom), valeur: l && l.performance_pct }; });
    var mesurees = donnees.filter(function (d) { return fini(d.valeur); });
    var textes = donnees.map(function (d) {
      if (!fini(d.valeur)) {
        return d.nom + " : non disponible";
      }
      var fleche = d.valeur > 0 ? "▲ " : (d.valeur < 0 ? "▼ " : "");
      return d.nom + " : " + fleche + signe(d.valeur, 2);
    });
    if (mesurees.length === 0) {
      return { svg: null, alternative: alternative(textes) };
    }
    var ligneH = 26, L = 640, nomL = 200, valeurL = 120;
    var zoneL = L - nomL - valeurL, H = mesurees.length * ligneH + 8;
    var maxAbs = Math.max.apply(null, mesurees.map(function (d) { return Math.abs(d.valeur); })) || 1;
    var zero = nomL + zoneL / 2;
    var svg = cadre(L, H, "Gain ou perte de " + mesurees.length + " lignes", "barres");
    svg.appendChild(element("line", { x1: zero, y1: 2, x2: zero, y2: H - 2, class: "axe" }));
    mesurees.forEach(function (d, k) {
      var largeur = Math.abs(d.valeur) * (zoneL / 2) / maxAbs;
      var haut = 4 + k * ligneH;
      var serie = d.valeur > 0 ? "hausse" : (d.valeur < 0 ? "baisse" : "nulle");
      svg.appendChild(element("rect", { x: arrondi(d.valeur >= 0 ? zero : zero - largeur), y: haut + 4,
                                        width: arrondi(Math.max(largeur, 1)), height: ligneH - 10,
                                        class: "barre-" + serie, "data-serie": serie }));
      var fleche = d.valeur > 0 ? "▲ " : (d.valeur < 0 ? "▼ " : "");
      svg.appendChild(texteSvg(4, haut + ligneH / 2 + 4, d.nom, { class: "etiquette" }));
      svg.appendChild(texteSvg(L - 4, haut + ligneH / 2 + 4, fleche + signe(d.valeur, 2),
                               { class: "etiquette", "text-anchor": "end" }));
    });
    return { svg: svg, alternative: alternative(textes) };
  }

  // --- La jauge du RSI : un fait, jamais un signal (contrainte AMF) ------------
  function jauge(rsi) {
    if (!fini(rsi) || rsi < 0 || rsi > 100) {
      return { svg: null, alternative: alternative(["RSI 14 : non disponible"]) };
    }
    var cx = 110, cy = 100, r = 80;
    function point(valeur, rayon) {
      var angle = Math.PI * (1 - valeur / 100);
      return [cx + rayon * Math.cos(angle), cy - rayon * Math.sin(angle)];
    }
    var svg = cadre(220, 130, "RSI 14 : " + nombre(rsi, 1), "jauge");
    var depart = point(0, r), arrivee = point(100, r);
    svg.appendChild(element("path", { d: "M " + arrondi(depart[0]) + " " + arrondi(depart[1]) + " A " + r + " " + r
                                      + " 0 0 1 " + arrondi(arrivee[0]) + " " + arrondi(arrivee[1]), class: "jauge-arc" }));
    [30, 70].forEach(function (repere) {
      var a = point(repere, r - 12), b = point(repere, r + 12), t = point(repere, r + 24);
      svg.appendChild(element("line", { x1: arrondi(a[0]), y1: arrondi(a[1]), x2: arrondi(b[0]), y2: arrondi(b[1]),
                                        class: "jauge-repere" }));
      svg.appendChild(texteSvg(t[0], t[1] + 4, String(repere), { class: "etiquette", "text-anchor": "middle" }));
    });
    var bout = point(rsi, r - 8);
    svg.appendChild(element("line", { x1: cx, y1: cy, x2: arrondi(bout[0]), y2: arrondi(bout[1]), class: "jauge-aiguille",
                                      "data-serie": "rsi" }));
    svg.appendChild(texteSvg(cx, cy + 24, nombre(rsi, 1), { class: "valeur-jauge", "text-anchor": "middle" }));
    return { svg: svg, alternative: alternative(["RSI 14 : " + nombre(rsi, 1) + ". Repères : 30 et 70."]) };
  }

  window.GRAPHIQUES = { courbe: courbe, anneau: anneau, barres: barres, jauge: jauge, moyenneMobile: moyenneMobile,
                        lireNombre: lireNombre };
})();
