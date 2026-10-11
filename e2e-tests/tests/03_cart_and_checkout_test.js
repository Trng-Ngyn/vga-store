Feature('Quản lý Giỏ hàng và Thanh toán');

Scenario('Thêm sản phẩm VGA vào giỏ hàng và kiểm tra giỏ hàng', ({ I }) => {
  I.amOnPage('/');
  I.click('a[href*="/product/"]');
  I.click('button', 'Thêm vào giỏ');
  // Chuyển sang trang giỏ hàng
  I.amOnPage('/cart');
  I.see('Giỏ hàng');
  // Nút thanh toán hiển thị
  I.seeElement('button', 'Thanh toán');
});
