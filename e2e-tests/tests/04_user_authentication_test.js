Feature('Xác thực người dùng (Authentication & Security)');

Scenario('Kiểm tra trang đăng nhập hiển thị đầy đủ trường nhập liệu', ({ I }) => {
  I.amOnPage('/login');
  I.see('Đăng nhập');
  I.seeElement('input[type="email"]');
  I.seeElement('input[type="password"]');
  I.seeElement('button[type="submit"]');
});

Scenario('Đăng nhập thất bại khi nhập sai mật khẩu (Security Negative Test)', ({ I }) => {
  I.amOnPage('/login');
  I.fillField('input[type="email"]', 'wrong_user@example.com');
  I.fillField('input[type="password"]', 'WrongPassword123');
  I.click('button[type="submit"]');
  // Hệ thống phải hiển thị thông báo lỗi hoặc cảnh báo
  I.see('Sai thông tin' || 'Thất bại' || 'Error');
});
