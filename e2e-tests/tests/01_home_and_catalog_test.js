Feature('Trang chủ và Danh mục sản phẩm VGA Store');

Scenario('Kiểm tra tải trang chủ thành công và hiển thị các thành phần chính', ({ I }) => {
  I.amOnPage('/');
  I.seeElement('header');
  I.see('SẢN PHẨM');
  I.see('CARD ĐỒ HỌA');
});

Scenario('Xem chi tiết một sản phẩm card màn hình', ({ I }) => {
  I.amOnPage('/products');
  I.waitForElement('a.product-card', 10);
  I.click('a.product-card');
  I.waitForText('Thông Số Kỹ Thuật', 10);
  I.see('Thêm vào giỏ');
});
