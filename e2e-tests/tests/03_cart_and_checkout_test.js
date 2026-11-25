Feature('Quản lý Giỏ hàng và Thanh toán');

Scenario('Đăng nhập, thêm sản phẩm VGA vào giỏ hàng và kiểm tra nút thanh toán', ({ I }) => {
  I.amOnPage('/');
  I.waitForElement('button[title="Đăng nhập"]', 10);
  I.click('button[title="Đăng nhập"]');
  I.waitForElement('form.auth-form', 10);
  I.fillField('input[placeholder*="tài khoản"]', 'demotester');
  I.fillField('input[type="password"]', '123456');
  I.click('button.auth-submit-btn');
  I.wait(1.5);

  I.amOnPage('/products');
  I.waitForElement('a.product-card', 10);
  I.click('a.product-card');
  I.waitForElement('button.btn-add-cart', 10);
  I.click('button.btn-add-cart');
  I.wait(1.5);

  I.amOnPage('/cart');
  I.waitForText('GIỎ HÀNG CỦA BẠN', 10);
  I.seeElement('button.btn-checkout-now');
  I.see('TIẾN HÀNH THANH TOÁN');

  // Clean up test cart item and clear localStorage session for subsequent unauth tests
  I.click('Xóa toàn bộ giỏ hàng');
  I.wait(1);
  I.executeScript(() => localStorage.clear());
  I.amOnPage('/');
});
