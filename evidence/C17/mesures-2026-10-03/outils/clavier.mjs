// Parcours au clavier des trois ecrans : ordre de tabulation, focus visible, focus apres l'arrivee du briefing.
// Usage : node clavier.mjs <fichier-de-sortie.json>   (serveur sur le port 8001, cle jetable, traçage coupe)
import fs from 'node:fs';
import puppeteer from 'puppeteer-core';

const BASE = 'http://127.0.0.1:8001';
const CLE = process.env.LH_CLE;
if (!CLE) { console.error('Variable LH_CLE absente : la cle jetable du serveur de mesure.'); process.exit(1); }
const CHROME = 'C:/Program Files/Google/Chrome/Application/chrome.exe';
const TEXTE = 'LVMH clôture à 378,55 EUR, en légère baisse de 0,25 %.\n\nAucune actualité récente.';

const decrire = () => {
  const e = document.activeElement;
  if (!e || e === document.body) return null;
  const st = getComputedStyle(e);
  const dec = (e.id ? '#' + e.id : '') || (e.getAttribute('aria-label') ? `[${e.getAttribute('aria-label')}]` : '') || (e.textContent || '').trim().slice(0, 28);
  return {balise: e.tagName.toLowerCase(), repere: dec, role: e.getAttribute('role'),
          contour: st.outlineStyle !== 'none' && parseFloat(st.outlineWidth) >= 2 ? `${st.outlineWidth} ${st.outlineStyle}` : `${st.outlineWidth} ${st.outlineStyle}`,
          focus_visible: e.matches(':focus-visible'), visible_a_l_ecran: e.getBoundingClientRect().width > 0};
};

const browser = await puppeteer.launch({executablePath: CHROME, headless: true, args: ['--no-sandbox']});
const sortie = {};
try {
  for (const [nom, url, attente] of [
    ['portefeuille', `${BASE}/index.html`, '#lignes tr'],
    ['indicateurs', `${BASE}/indicateurs.html`, '#lignes tr'],
    ['briefing', `${BASE}/briefing.html`, '#demande:not([hidden])'],
  ]) {
    const page = await browser.newPage();
    await page.setViewport({width: 1350, height: 940});
    // Sans cle : le premier element qui recoit le focus doit etre le champ de la cle.
    await page.goto(url, {waitUntil: 'networkidle0'});
    const sansCle = await page.evaluate(decrire);
    await page.evaluateOnNewDocument((cle) => sessionStorage.setItem('rita_api_key', cle), CLE);
    await page.goto(url, {waitUntil: 'networkidle0'});
    await page.waitForSelector(attente, {timeout: 30000});
    await page.evaluate(() => { document.activeElement && document.activeElement.blur(); window.scrollTo(0, 0); });
    await page.mouse.click(2, 2);   // remet le point de depart de la tabulation en haut de la page
    const ordre = [];
    for (let i = 0; i < 12; i++) {
      await page.keyboard.press('Tab');
      const d = await page.evaluate(decrire);
      if (!d) break;
      ordre.push(d);
      if (ordre.length > 1 && JSON.stringify(ordre.at(-1)) === JSON.stringify(ordre[0])) break;   // boucle complete, pas de piege
    }
    sortie[nom] = {focus_au_chargement_sans_cle: sansCle, ordre_de_tabulation_avec_cle: ordre};
    if (nom === 'briefing') {
      await page.setRequestInterception(true);
      page.on('request', (req) => {
        if (req.method() === 'POST' && req.url().includes('/briefing?ticker=')) {
          req.respond({status: 200, contentType: 'application/json', headers: {'X-Request-ID': 'clavier0123456789'},
                       body: JSON.stringify({ticker: 'MC.PA', price: 378.55, change_pct: -0.25, currency: 'EUR', briefing: TEXTE, conforme_amf: true, motifs_amf: []})});
        } else req.continue();
      });
      await page.focus('#ticker');
      await page.keyboard.type('MC.PA');
      await page.keyboard.press('Enter');          // soumission au clavier, sans souris
      await page.waitForSelector('#texte p', {timeout: 30000});
      sortie[nom].focus_apres_arrivee_du_texte = await page.evaluate(decrire);
    }
    await page.close();
  }
} finally {
  await browser.close();
}
fs.writeFileSync(process.argv[2], JSON.stringify(sortie, null, 1));
console.log(JSON.stringify(sortie, null, 1));
