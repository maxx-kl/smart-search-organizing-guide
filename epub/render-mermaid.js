// Usage: node render-mermaid.js <mermaid.min.js> <in.mmd> <out.png>
const fs = require('fs');
const { chromium } = require('playwright');
(async () => {
  const [mermaidJs, input, output] = process.argv.slice(2);
  const browser = await chromium.launch();
  const page = await browser.newPage({ deviceScaleFactor: 2, viewport: { width: 900, height: 600 } });
  await page.setContent('<html><body style="margin:0;background:#fff"><div id="d"></div></body></html>');
  await page.addScriptTag({ path: mermaidJs });
  const src = fs.readFileSync(input, 'utf8');
  await page.evaluate(async (src) => {
    mermaid.initialize({ startOnLoad: false, theme: 'neutral', fontFamily: 'Helvetica, Arial, sans-serif',
                         flowchart: { htmlLabels: true, useMaxWidth: false } });
    const { svg } = await mermaid.render('g', src);
    document.getElementById('d').innerHTML = svg;
  }, src);
  const el = await page.$('#d svg');
  await el.screenshot({ path: output, omitBackground: false });
  await browser.close();
})();
