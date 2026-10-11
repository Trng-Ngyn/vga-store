const { setHeadlessWhen, setCommonPlugins } = require('@codeceptjs/configure');

// Bật chế độ Headless khi chạy trên CI hoặc khi biến môi trường HEADLESS=true
setHeadlessWhen(process.env.HEADLESS || false);
setCommonPlugins();

/** @type {CodeceptJS.MainConfig} */
exports.config = {
  name: 'vga-store-e2e',
  tests: './tests/*_test.js',
  output: './output',
  helpers: {
    Playwright: {
      browser: 'chromium',
      url: process.env.BASE_URL || 'http://localhost:5173',
      show: !process.env.HEADLESS,
      waitForNavigation: 'load',
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
