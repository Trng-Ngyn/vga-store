Feature('Kiem thu Bang quyet dinh va Chuyen trang thai (Decision Table & State Transition)');

Scenario('DT_01: Khách vãng lai truy cập giỏ hàng và kiểm tra trạng thái giỏ trống', ({ I }) => {
  I.amOnPage('/cart');
  I.see('GIỎ HÀNG CỦA BẠN');
  I.see('QUAY LẠI CỬA HÀNG');
});

Scenario('DT_02: Khách vãng lai vào trang chi tiết sản phẩm có đủ thông tin mua hàng', ({ I }) => {
  I.amOnPage('/products');
  I.waitForElement('a.product-card', 10);
  I.click('a.product-card');
  I.waitForText('MUA NGAY', 10);
  I.seeElement('button');
  I.see('VGA');
});

Scenario('DT_03: Điều hướng danh mục Card đồ họa và lọc sản phẩm theo từ khóa', ({ I }) => {
  I.amOnPage('/products');
  I.waitForElement('input[placeholder*="Tìm kiếm"]', 10);
  I.fillField('input[placeholder*="Tìm kiếm"]', 'ASUS');
  I.see('ASUS');
});

Scenario('ST_01: Chuyển trạng thái từ Trang chủ -> Modal Đăng nhập -> Tab Đăng ký tài khoản', ({ I }) => {
  I.amOnPage('/');
  I.waitForElement('button[title="Đăng nhập"]', 10);
  I.click('button[title="Đăng nhập"]');
  I.click('ĐĂNG KÝ');
  I.see('TẠO TÀI KHOẢN');
  I.seeElement('button[type="submit"]');
});

Scenario('ST_02: Kiểm tra truy cập trang Tin tức công nghệ (Blog)', ({ I }) => {
  I.amOnPage('/blog');
  I.seeElement('header');
  I.see('TIN TỨC');
});
