<style>
@page{ size:A4 landscape; margin:12mm;
  @bottom-right{ content:"Annexe du rapport E5 · " counter(page) " / " counter(pages); } }
h2{ break-before:page; }
#a1{ break-before:auto; }
.ecran{ display:none; }
/* 18/11/2026 : le schéma global en HTML, aux couleurs du rapport (marine #12395E, bleus #0066A3 et #14607F, sarcelle
   #007B86, fonds #E6EEF5 et #E3F0F3). Les textes des boîtes sont ceux du rapport E5 v1.3, rien d'autre. */
.sg-legende{ font-size:8.6pt; color:#4A5766; margin:1mm 0 3mm; }
.sg-pastille{ display:inline-block; width:3.2mm; height:3.2mm; border-radius:.8mm; vertical-align:-.5mm; margin:0 1mm 0 3mm; }
.sg-grille{ display:grid; column-gap:0; row-gap:0; align-items:stretch; }
.sg-a1{ grid-template-columns:minmax(0,1fr) 13mm minmax(0,1fr) 13mm minmax(0,1fr) 15mm minmax(0,1fr) 15mm minmax(0,1fr); }
.sg-a2{ grid-template-columns:minmax(0,1fr) 6mm minmax(0,1fr) 6mm minmax(0,1fr) 6mm minmax(0,1fr) 6mm minmax(0,1fr) 6mm minmax(0,1fr); }
.sg-boite code, .sg-resultat code{ overflow-wrap:anywhere; }
.sg-boite{ border:.4mm solid #0066A3; background:#E6EEF5; border-radius:2mm; padding:2mm 2.6mm; font-size:8.4pt;
  line-height:1.3; color:#16202B; break-inside:avoid; }
.sg-boite b{ display:block; color:#12395E; font-size:9.4pt; margin-bottom:1mm; }
.sg-langfuse{ border-color:#007B86; background:#E3F0F3; }
.sg-fort{ border-color:#0066A3; background:#0066A3; color:#fff; }
.sg-fort b{ color:#fff; }
.sg-fort code{ background:rgba(255,255,255,.18); color:#fff; }
.sg-entree{ background:#fff; border-radius:7mm; text-align:center; display:flex; align-items:center; justify-content:center; }
.sg-fleche{ display:flex; flex-direction:column; align-items:center; justify-content:center; color:#14607F;
  font-size:15pt; font-weight:700; line-height:1; text-align:center; }
.sg-fleche small{ font-size:7.4pt; font-weight:600; color:#14607F; line-height:1.15; margin-top:.6mm; }
.sg-bas{ flex-direction:row; gap:2mm; padding:1mm 0; }
.sg-longue{ flex-direction:row; justify-content:flex-start; gap:2mm; padding-left:3mm; }
.sg-trait{ flex:1; height:.5mm; background:#14607F; }
.sg-question{ background:#D6E6F7; color:#12395E; font-weight:600; font-size:8.6pt; text-align:center;
  clip-path:polygon(50% 0, 100% 50%, 50% 100%, 0 50%); padding:5mm 9mm; display:flex; align-items:center; justify-content:center; min-height:20mm; }
.sg-resultat{ background:#EEF2F6; border:.3mm solid #C5D0DA; border-radius:2mm; padding:2mm; font-size:8.4pt; text-align:center; }
.sg-texte{ font-size:8.8pt; line-height:1.35; margin:3mm 0 0; }
.sg-perimetre{ font-size:8.8pt; margin:0 0 3mm; }
</style>

# Annexe du rapport E5 : le schéma global {: .ecran }

## 📡 A1. Le dispositif en une vue (C20) {: #a1 }

<p class="sg-legende">Cinq parties, toutes dans la version de production <code>6f428d6</code> (en production le 07/11/2026).<span class="sg-pastille" style="background:#E6EEF5;border:.3mm solid #0066A3"></span>RITA : API, tableau de bord et vigie<span class="sg-pastille" style="background:#E3F0F3;border:.3mm solid #007B86"></span>Langfuse Cloud, région UE<span class="sg-pastille" style="background:#0066A3"></span>GitHub : issues « incident »</p>

<div class="sg-grille sg-a1">
<div class="sg-boite sg-entree" style="grid-column:1;grid-row:1"><span>Appels à <code>/briefing</code> et <code>/question</code></span></div>
<div class="sg-fleche" style="grid-column:2;grid-row:1">→</div>
<div class="sg-boite" style="grid-column:3;grid-row:1"><b>🔢 1. Les compteurs</b>dans l'API, <code>compteurs.py</code> ; une observation par appel : route, résultat, motif, durée, jetons ; jamais de texte</div>
<div class="sg-fleche" style="grid-column:4;grid-row:1">→</div>
<div class="sg-boite" style="grid-column:5;grid-row:1"><b>⚖️ 2. Les verdicts</b><code>GET /sante</code> (<code>sante.py</code>, <code>signaux.py</code>, <code>seuils.json</code>) ; calcule chaque signal sur sa fenêtre et le classe : sain, attention, problème ou inconnu</div>
<div class="sg-fleche" style="grid-column:6;grid-row:1">→<small>lit /sante</small></div>
<div class="sg-boite" style="grid-column:7;grid-row:1"><b>🔭 4. La vigie</b>hors de l'API, <code>vigie.py</code> ; sonde /health, lit /sante ; en production, également programmée toutes les trois heures par GitHub Actions</div>
<div class="sg-fleche" style="grid-column:8;grid-row:1">→<small>ouvre, ferme</small></div>
<div class="sg-boite sg-fort" style="grid-column:9;grid-row:1 / span 4;display:flex;flex-direction:column;justify-content:center"><b>🎫 Les issues GitHub, outil de suivi</b>l'étiquette incident marque celles des alertes ; une alerte y ouvre ou commente une fiche datée, puis je diagnostique et je corrige (PR, post-mortem)</div>
<div class="sg-fleche sg-bas" style="grid-column:1;grid-row:2 / span 2">↓<small>lorsqu'une trace Langfuse est produite</small></div>
<div class="sg-fleche sg-bas" style="grid-column:5;grid-row:2">↓<small>affiche les verdicts</small></div>
<div class="sg-boite" style="grid-column:5;grid-row:3"><b>📊 3. Le tableau de bord</b><code>tableau-de-bord.html</code> ; affiche les verdicts de /sante, avec la clé de l'API ; s'actualise toutes les 30 s, suspendable depuis le 02/11</div>
<div class="sg-boite sg-langfuse" style="grid-column:1;grid-row:4;margin-top:4mm"><b>🧵 Traces du modèle</b>Langfuse Cloud, région UE, palier gratuit (rapport E3)</div>
<div class="sg-fleche" style="grid-column:2;grid-row:4;margin-top:4mm">→</div>
<div class="sg-boite sg-langfuse" style="grid-column:3;grid-row:4;margin-top:4mm"><b>🔔 5. Les alertes Langfuse</b>Langfuse Cloud, puis <code>alerte-incident.yml</code> ; deux alertes sur les traces du modèle</div>
<div class="sg-fleche sg-longue" style="grid-column:4 / span 5;grid-row:4;margin-top:4mm"><small>ouvre ou commente une issue incident ; un retour à OK sans issue ouverte : on le note dans le journal de l'exécution</small><span class="sg-trait"></span>→</div>
</div>

<p class="sg-texte"><b>Pourquoi ces outils</b> (§ 3) : une vigie hors de l'API, car une API arrêtée ne peut pas annoncer sa propre panne ; deux sondes à 10 secondes d'écart évitent une alerte sur un seul paquet perdu. Une seule source de verdicts, <code>/sante</code>, ce qui évite de dupliquer les règles. Des compteurs en mémoire : un seul processus, sans base ni service de plus. Langfuse Cloud, région UE, palier gratuit : l'auto-hébergement a été écarté par la mesure. Les issues GitHub comme outil de suivi : les incidents vivent déjà dans le dépôt (fiches, PR, tests).<br><b>Les limites</b> (§ 8) : seuils provisoires, jamais relus sur du trafic réel ; compteurs remis à zéro à chaque redémarrage de l'API ; deux règles de fermeture coexistent, la vigie ferme son issue, la chaîne Langfuse ne ferme jamais.</p>

## 🚨 A2. L'incident INC-009 (C21) {: #a2 }

<p class="sg-perimetre"><b>Périmètre</b> : la chaîne d'alerte seulement ; ni le service, ni les données, ni une alerte réelle ne sont touchés. Mais un faux incident, resté sept jours sans traitement, pouvait faire croire à une nouvelle panne de fournisseur.</p>

<div class="sg-grille sg-a2">
<div class="sg-boite sg-fort" style="grid-column:1"><b>🔔 Déclenchement</b>23/10, 08:30 UTC : l'alerte « fournisseur en erreur » ouvre #130 ; elle est fermée à la main, fausse alerte qualifiée. 24/10, 08:30 : Langfuse envoie le retour à la normale de la même alerte, gravité OK ; le workflow ne trouve aucune issue ouverte et en crée une nouvelle, #137.</div>
<div class="sg-fleche" style="grid-column:2">→</div>
<div class="sg-boite sg-fort" style="grid-column:3"><b>🔍 Diagnostic · C21.1</b>trouvé le 31/10 en relisant les issues incident ouvertes ; deux pistes écartées : une nouvelle panne, un doublon de Langfuse. Cause : la gravité était lue mais seulement affichée, et sans issue ouverte une issue était créée quelle que soit la gravité.</div>
<div class="sg-fleche" style="grid-column:4">→</div>
<div class="sg-boite sg-fort" style="grid-column:5"><b>🧪 Reproduction · C21.2</b>en environnement de développement : les deux étapes du workflow, rejouées telles qu'elles sont écrites, avec le message réel de #137 et un faux gh, dans un conteneur jetable, sans secret ni ticket créé ; le message OK sans issue ouverte demande issue create.</div>
<div class="sg-fleche" style="grid-column:6">→</div>
<div class="sg-boite sg-fort" style="grid-column:7"><b>🛠️ Résolution · C21.4</b>le titre d'origine envoyé par Langfuse est conservé pour reconnaître le retour à la normale (gravité OK ou titre « [OK] ») ; <code>alerte-incident.yml</code>, lignes 140 à 148, commit <code>a57dccb</code>.</div>
<div class="sg-fleche" style="grid-column:8">→</div>
<div class="sg-boite sg-fort" style="grid-column:9"><b>✅ Tests en succès</b><code>test_alerte_incident.py</code> ; avant le correctif : 13 tests passent, 1 échoue ; après, même conteneur et même fichier : 14 tests passent ; sur la PR #171, l'intégration continue passe : 1 821 tests réussis, dont les quatre nouveaux.</div>
<div class="sg-fleche" style="grid-column:10">→</div>
<div class="sg-boite sg-fort" style="grid-column:11"><b>🔀 Versionnement et documentation · C21.3, C21.5</b>branche <code>fix/137-retour-a-la-normale</code> ; PR #171 vers develop, puis PR #172 vers main, en production le 01/11 ; le débogage est écrit dans l'issue #137, le post-mortem dans <code>evidence/C21/</code>.</div>
</div>

<div class="sg-grille" style="grid-template-columns:1.25fr 1fr 16mm 1fr 16mm 1fr;margin-top:5mm">
<div class="sg-fleche" style="grid-column:1;grid-row:1;align-items:flex-end;color:#12395E;font-size:9pt;font-weight:600;padding-right:3mm;text-align:right">La décision devient<br><code>alerte-incident.yml</code><br>lignes 140 à 148</div>
<div class="sg-question" style="grid-column:2;grid-row:1">Issue déjà ouverte pour cette alerte ?</div>
<div class="sg-fleche" style="grid-column:3;grid-row:1">→<small>non</small></div>
<div class="sg-question" style="grid-column:4;grid-row:1">Retour à la normale (OK) ?</div>
<div class="sg-fleche" style="grid-column:5;grid-row:1">→<small>non</small></div>
<div class="sg-resultat" style="grid-column:6;grid-row:1;align-self:center">🎫 une alerte crée l'issue, comme avant (<code>--label incident</code>)</div>
<div class="sg-fleche sg-bas" style="grid-column:2;grid-row:2">↓<small>oui</small></div>
<div class="sg-fleche sg-bas" style="grid-column:4;grid-row:2">↓<small>oui</small></div>
<div class="sg-resultat" style="grid-column:2;grid-row:3">💬 une issue ouverte est commentée, comme avant</div>
<div class="sg-resultat" style="grid-column:4;grid-row:3">📝 aucune issue créée ; on le note dans le journal de l'exécution</div>
</div>

<p class="sg-texte">Dans cette chaîne d'alerte Langfuse, la fermeture reste manuelle : une décision humaine, justifiée. Neuf autres incidents ont leur fiche dans <code>evidence/C21/</code> ; INC-005 et INC-009 sont documentés de bout en bout (issue, PR, post-mortem). <b>Le correctif d'INC-009 est sur main depuis le 01/11</b> (<code>922349d</code>), tests de non-régression verts. Le 15/11, après le correctif, un retour à OK est commenté dans #250 déjà ouverte ; sans issue ouverte, seul le test le prouve.</p>
