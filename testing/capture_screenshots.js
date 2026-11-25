const path = require('path');
const { chromium } = require(path.resolve(__dirname, '..', 'e2e-tests', 'node_modules', 'playwright'));

(async () => {
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  await page.goto('http://localhost:5173/products', { waitUntil: 'networkidle' });
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.resolve(__dirname, 'diagrams', 'live_user_portal.png') });
  await page.goto('http://localhost:5174/login', { waitUntil: 'networkidle' });
  await page.waitForTimeout(800);
  await page.screenshot({ path: path.resolve(__dirname, 'diagrams', 'live_admin_portal.png') });
  await browser.close();
  console.log('LIVE_SCREENSHOTS_OK');
})();
