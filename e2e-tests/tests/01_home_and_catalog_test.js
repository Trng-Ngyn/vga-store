Feature('Trang chủ và Danh mục sản phẩm VGA Store');

Scenario('Kiểm tra tải trang chủ thành công và hiển thị các thành phần chính', ({ I }) => {
  I.amOnPage('/');
  I.see('VGA Store');
  // Kiểm tra thanh menu điều hướng
  I.seeElement('header');
  // Kiểm tra danh mục sản phẩm nổi bật
  I.see('Sản phẩm');
});

Scenario('Xem chi tiết một sản phẩm card màn hình', ({ I }) => {
  I.amOnPage('/');
  // Nhấp vào sản phẩm đầu tiên hiển thị trên trang chủ
  I.click('a[href*="/product/"]');
  // Kiểm tra trang chi tiết hiển thị thông số kỹ thuật và nút mua hàng
  I.see('Thông số kỹ thuật');
  I.seeElement('button', 'Thêm vào giỏ');
});
