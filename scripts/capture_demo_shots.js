#!/usr/bin/env node
/**
 * HyperPresenter Studio - Automated Visual Demo Shot Capture Engine
 * Uses system Chrome via puppeteer-core to capture pixel-perfect 1920x1080
 * screenshots of all 3 acts for immediate visual review.
 */

const puppeteer = require('puppeteer-core');
const path = require('path');
const fs = require('fs');

async function capture() {
  const args = process.argv.slice(2);
  let htmlFile = '01_prototype_opendesign/prototype_ink-wash.html';
  let outDir = path.resolve(__dirname, '../output/screenshots');
  let prefix = 'demo';
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--input' && args[i + 1]) htmlFile = args[i + 1];
    if (args[i] === '--output-dir' && args[i + 1]) outDir = args[i + 1];
    if (args[i] === '--prefix' && args[i + 1]) prefix = args[i + 1];
  }

  // Ensure output directory exists
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const projectRoot = path.resolve(__dirname, '..');
  const fullHtmlPath = path.isAbsolute(htmlFile) ? htmlFile : path.resolve(projectRoot, htmlFile);
  const fileUrl = 'file:///' + fullHtmlPath.replace(/\\/g, '/');

  // Also mirror to global conversation artifact directory if available
  const artifactDir = 'C:\\Users\\26048\\.gemini\\antigravity-ide\\brain\\1ac08551-ed06-4911-9b5b-dae57d72411a';
  const hasArtifactDir = fs.existsSync(artifactDir);

  const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const browser = await puppeteer.launch({
    executablePath: chromePath,
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1920,1080', '--disable-web-security']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  console.log(`📸 [Demo Capture] Loading HTML: ${fullHtmlPath}`);
  await page.goto(fileUrl, { waitUntil: 'networkidle0', timeout: 30000 });
  await new Promise(r => setTimeout(r, 2000)); // wait for fonts & images to render

  for (let act = 1; act <= 3; act++) {
    try {
      await page.evaluate((a) => {
        if (typeof switchAct === 'function') switchAct(a);
      }, act);
      await new Promise(r => setTimeout(r, 800));
    } catch (e) {
      console.warn(`Note: switchAct not found, capturing static page for act ${act}`);
    }

    const filename = `${prefix}_act${act}.jpg`;
    const localShot = path.join(outDir, filename);
    await page.screenshot({ path: localShot, quality: 92, type: 'jpeg' });
    console.log(`  ✔ Act ${act} captured: ${localShot}`);

    if (hasArtifactDir) {
      const artifactShot = path.join(artifactDir, `${prefix}_act${act}.jpg`);
      fs.copyFileSync(localShot, artifactShot);
    }
  }

  await browser.close();
  console.log('🎉 [Demo Capture] All 3 acts captured successfully!');
}

capture().catch(err => {
  console.error('❌ Capture error:', err);
  process.exit(1);
});
