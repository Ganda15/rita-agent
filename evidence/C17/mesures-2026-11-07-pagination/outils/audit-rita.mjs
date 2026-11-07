// Audit Lighthouse des cinq ecrans de RITA, par le mode "flux" (navigations + instantanes).
// Repris du script du 03/10 (evidence/C17/mesures-2026-10-03/outils/audit-rita.mjs), memes etapes ; ajouts du 06/11 :
// les ecrans Question (formulaire affiche, sans question posee : aucun appel au modele) et Tableau de bord (cartes chargees).
// Usage : node audit-rita.mjs <dossier-de-sortie> <bureau|mobile>
// Le serveur tourne sur le port 8001 avec une cle jetable ; le traçage est coupe ; l'appel au modele est remplace.
import fs from 'node:fs';
import path from 'node:path';
import puppeteer from 'puppeteer-core';
import {startFlow} from 'lighthouse';
import desktopConfig from 'lighthouse/core/config/desktop-config.js';

const BASE = 'http://127.0.0.1:8001';
const CLE = process.env.LH_CLE;
if (!CLE) { console.error('Variable LH_CLE absente : la cle jetable du serveur de mesure.'); process.exit(1); }
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const [,, SORTIE, MODE] = process.argv;
fs.mkdirSync(SORTIE, {recursive: true});

// Un vrai texte de briefing, produit par le modele le 03/10 (banc C7) : le poids de la page est celui d'un vrai rendu.
const ligne = fs.readFileSync(process.env.RESULTATS, 'utf8').split('\n').filter(Boolean).map(JSON.parse)
  .find((l) => l.fournisseur === 'foundry' && l.ticker === 'MC.PA' && l.texte);
const BRIEFING = {ticker: 'MC.PA', price: 378.55, change_pct: -0.25, currency: 'EUR', briefing: ligne.texte,
                  conforme_amf: true, motifs_amf: []};

const pages = [
  {nom: 'portefeuille', url: `${BASE}/index.html`, apres: async (page) => { await page.waitForSelector('#lignes tr', {timeout: 30000}); }},
  {nom: 'indicateurs', url: `${BASE}/indicateurs.html`, apres: async (page) => { await page.waitForSelector('#lignes tr', {timeout: 30000}); }},
  {nom: 'briefing', url: `${BASE}/briefing.html`, apres: async (page) => { await page.waitForSelector('#demande:not([hidden])', {timeout: 30000}); }},
  {nom: 'question', url: `${BASE}/question.html`, apres: async (page) => { await page.waitForSelector('#demande:not([hidden])', {timeout: 30000}); }},
  {nom: 'tableau-de-bord', url: `${BASE}/tableau-de-bord.html`, apres: async (page) => { await page.waitForSelector('#tableau:not([hidden]) #cartes > *', {timeout: 30000}); }},
];

const config = MODE === 'bureau' ? desktopConfig : undefined;
const resume = [];

function extraire(lhr, etape, ecran) {
  const a = (id) => lhr.audits[id];
  const cat = (id) => (lhr.categories[id]?.score ?? null);
  const echecs = Object.values(lhr.audits)
    .filter((x) => lhr.categories.accessibility?.auditRefs.some((r) => r.id === x.id) && x.score === 0)
    .map((x) => ({id: x.id, titre: x.title, elements: (x.details?.items ?? []).length,
                  exemples: (x.details?.items ?? []).slice(0, 3).map((i) => i.node?.selector ?? i.node?.snippet ?? '')}));
  const manuels = Object.values(lhr.audits)
    .filter((x) => lhr.categories.accessibility?.auditRefs.some((r) => r.id === x.id) && x.scoreDisplayMode === 'manual').length;
  const reussis = Object.values(lhr.audits)
    .filter((x) => lhr.categories.accessibility?.auditRefs.some((r) => r.id === x.id) && x.score === 1).length;
  const requetes = (a('network-requests')?.details?.items ?? []);
  return {
    ecran, etape, mode: MODE, mode_lighthouse: lhr.gatherMode, version: lhr.lighthouseVersion,
    scores: {performance: cat('performance'), accessibilite: cat('accessibility'), bonnes_pratiques: cat('best-practices'), seo: cat('seo')},
    poids_octets: a('total-byte-weight')?.numericValue ?? null,
    requetes: requetes.length || null,
    requetes_detail: requetes.map((r) => ({url: r.url.replace(BASE, ''), type: r.resourceType, octets: r.transferSize, statut: r.statusCode})),
    noeuds_dom: a('dom-size-insight')?.details?.items?.[0]?.value?.value ?? null,
    fcp_ms: a('first-contentful-paint')?.numericValue ?? null, lcp_ms: a('largest-contentful-paint')?.numericValue ?? null,
    cls: a('cumulative-layout-shift')?.numericValue ?? null, tbt_ms: a('total-blocking-time')?.numericValue ?? null,
    compression_texte: a('uses-text-compression') ? {score: a('uses-text-compression').score, gain_octets: a('uses-text-compression').details?.overallSavingsBytes ?? null} : null,
    cache_long: a('uses-long-cache-ttl') ? {score: a('uses-long-cache-ttl').score, elements: (a('uses-long-cache-ttl').details?.items ?? []).length} : null,
    a11y_echecs: echecs, a11y_reussis: reussis, a11y_a_verifier_a_la_main: manuels,
  };
}

const browser = await puppeteer.launch({executablePath: CHROME, headless: true, args: ['--no-sandbox']});
try {
  for (const p of pages) {
    const page = await browser.newPage();
    await page.setViewport(MODE === 'bureau' ? {width: 1350, height: 940} : {width: 412, height: 823});
    const flow = await startFlow(page, {name: `RITA ${p.nom} (${MODE})`, config});
    // Etat 1 : aucune cle.
    await flow.navigate(p.url, {name: `${p.nom} : etat 1, aucune cle`});
    // Etats suivants : la cle est posee dans la memoire de l'onglet avant le chargement.
    await page.evaluateOnNewDocument((cle) => sessionStorage.setItem('rita_api_key', cle), CLE);
    await flow.navigate(p.url, {name: `${p.nom} : avec cle, donnees chargees`});
    await p.apres(page);
    await flow.snapshot({name: `${p.nom} : instantane apres chargement`});
    if (p.nom === 'briefing') {
      await page.setRequestInterception(true);
      page.on('request', (req) => {
        if (req.method() === 'POST' && req.url().includes('/briefing?ticker=')) {
          req.respond({status: 200, contentType: 'application/json', headers: {'X-Request-ID': 'lighthouse0123456789'}, body: JSON.stringify(BRIEFING)});
        } else req.continue();
      });
      await page.type('#ticker', 'MC.PA');
      await page.click('#form-briefing button');
      await page.waitForSelector('#texte p', {timeout: 30000});
      await flow.snapshot({name: 'briefing : etat 4, texte affiche (reponse enregistree)'});
    }
    const resultat = await flow.createFlowResult();
    fs.writeFileSync(path.join(SORTIE, `flux-${p.nom}-${MODE}.html`), await flow.generateReport());
    fs.writeFileSync(path.join(SORTIE, `flux-${p.nom}-${MODE}.json`), JSON.stringify(resultat));
    resultat.steps.forEach((s) => resume.push(extraire(s.lhr, s.name, p.nom)));
    await page.close();
  }
} finally {
  await browser.close();
}
fs.writeFileSync(path.join(SORTIE, `resume-${MODE}.json`), JSON.stringify(resume, null, 1));
console.log('ecrit', path.join(SORTIE, `resume-${MODE}.json`), resume.length, 'etapes');
