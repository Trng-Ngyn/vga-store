Feature('Kiem thu Bao mat Admin Portal & Phan quyen RBAC (Security & Admin UI)');

const ADMIN_URL = 'http://localhost:5174';

Scenario('SEC_01: Giao diện đăng nhập Admin Portal hiển thị đầy đủ trường xác thực', ({ I }) => {
  I.amOnPage(ADMIN_URL + '/login');
  I.seeElement('input');
  I.seeElement('button');
});

Scenario('SEC_02: Chặn đăng nhập Admin khi bỏ trống thông tin (BVA Empty Validation)', ({ I }) => {
  I.amOnPage(ADMIN_URL + '/login');
  I.click('button[type="submit"]');
  I.seeInCurrentUrl('/login');
});

Scenario('SEC_03: Chặn đăng nhập Admin với mật khẩu sai (Negative Security Test)', ({ I }) => {
  I.amOnPage(ADMIN_URL + '/login');
  I.fillField('input[type="text"], input[name="username"], input[placeholder*="tài khoản"]', 'admin');
  I.fillField('input[type="password"]', 'SaiMatKhau999');
  I.click('button[type="submit"]');
  I.seeInCurrentUrl('/login');
});

Scenario('SEC_04: Truy cập thẳng trang quản trị khi chưa có JWT sẽ chuyển hướng về Login', ({ I }) => {
  I.amOnPage(ADMIN_URL + '/products');
  I.seeInCurrentUrl('/login');
});
