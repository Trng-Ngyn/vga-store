const { setCommonPlugins } = require('@codeceptjs/configure');

const headless = (process.env.HEADLESS ?? (process.env.CI ? 'true' : 'false')).toLowerCase() === 'true';
setCommonPlugins();

/** @type {CodeceptJS.MainConfig} */
exports.config = {
  name: 'vga-store-e2e',
  tests: './tests/*_test.js',
  output: './output',
  helpers: {
    Playwright: {
      browser: 'chromium',
      channel: process.env.PLAYWRIGHT_CHANNEL || undefined,
      url: process.env.BASE_URL || 'http://localhost:5173',
      show: !headless,
      waitForNavigation: 'domcontentloaded',
      waitForAction: 500,
      restart: 'keep',
      windowSize: '1280x800'
    }
  },
  include: {
    I: './steps_file.js'
  },
  bootstrap: null,
  mocha: {},
  plugins: {
    screenshotOnFail: {
      enabled: true
    },
    tryTo: {
      enabled: true
    },
    retryFailedStep: {
      enabled: true,
      retries: 2
    }
  }
};
