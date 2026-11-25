Feature('Xác thực người dùng (Authentication & Security)');

Scenario('Kiểm tra modal đăng nhập hiển thị đầy đủ trường nhập liệu', ({ I }) => {
  I.amOnPage('/');
  I.waitForElement('button[title="Đăng nhập"]', 10);
  I.click('button[title="Đăng nhập"]');
  I.waitForElement('form.auth-form', 10);
  I.see('ĐĂNG NHẬP');
  I.seeElement('input[placeholder*="tài khoản"]');
  I.seeElement('input[type="password"]');
  I.seeElement('button[type="submit"]');
});

Scenario('Đăng nhập thất bại khi nhập sai mật khẩu (Security Negative Test)', ({ I }) => {
  I.amOnPage('/');
  I.waitForElement('button[title="Đăng nhập"]', 10);
  I.click('button[title="Đăng nhập"]');
  I.waitForElement('form.auth-form', 10);
  I.fillField('input[placeholder*="tài khoản"]', 'wrong_user_nonexist');
  I.fillField('input[type="password"]', 'WrongPassword123');
  I.click('button[type="submit"]');
  I.wait(2);
  I.see('ĐĂNG NHẬP');
});
