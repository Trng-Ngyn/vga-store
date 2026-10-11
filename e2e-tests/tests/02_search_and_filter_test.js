Feature('Tìm kiếm và Lọc sản phẩm Card Đồ Họa');

Scenario('Tìm kiếm card màn hình với từ khóa RTX', ({ I }) => {
  I.amOnPage('/');
  I.fillField('input[placeholder*="Tìm kiếm"]', 'RTX');
  I.pressKey('Enter');
  // Kết quả tìm kiếm phải chứa các sản phẩm liên quan RTX
  I.see('RTX');
});

Scenario('Tìm kiếm với từ khóa không tồn tại trả về thông báo phù hợp (Negative Test)', ({ I }) => {
  I.amOnPage('/');
  I.fillField('input[placeholder*="Tìm kiếm"]', 'XYZ9999NONEXIST');
  I.pressKey('Enter');
  // Kiểm tra hệ thống hiển thị thông báo không tìm thấy kết quả
  I.see('Không tìm thấy sản phẩm');
});
