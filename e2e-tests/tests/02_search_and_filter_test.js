Feature('Tìm kiếm và Lọc sản phẩm Card Đồ Họa');

Scenario('Tìm kiếm card màn hình với từ khóa RTX', ({ I }) => {
  I.amOnPage('/products');
  I.waitForElement('input[placeholder*="Tìm kiếm"]', 10);
  I.fillField('input[placeholder*="Tìm kiếm"]', 'RTX');
  I.see('RTX');
});

Scenario('Tìm kiếm với từ khóa không tồn tại trả về thông báo phù hợp (Negative Test)', ({ I }) => {
  I.amOnPage('/products');
  I.waitForElement('input[placeholder*="Tìm kiếm"]', 10);
  I.fillField('input[placeholder*="Tìm kiếm"]', 'XYZ9999NONEXIST');
  I.see('KHÔNG TÌM THẤY LINH KIỆN PHÙ HỢP');
});
