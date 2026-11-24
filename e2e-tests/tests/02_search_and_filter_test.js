const assert = require('node:assert/strict');
const resultNames = '.shop-product-grid .card-name';

Feature('Tìm kiếm sản phẩm Card Đồ Họa').tag('@catalog');

Scenario('Tìm kiếm từ khóa RTX trả về các sản phẩm RTX', async ({ I }) => {
  I.searchProduct('RTX');
  I.waitForVisible(resultNames, 10);
  const names = await I.grabTextFromAll(resultNames);
  assert.ok(names.some(name => /RTX/i.test(name)), 'Kết quả phải có ít nhất một sản phẩm RTX');
});

Scenario('Từ khóa không tồn tại cho kết quả rỗng', ({ I }) => {
  I.searchProduct('XYZ9999NONEXIST');
  I.waitForVisible('.shop-empty', 10);
  I.see('KHÔNG TÌM THẤY LINH KIỆN PHÙ HỢP', '.shop-empty h3');
  I.see('0 sản phẩm', '.result-count');
  I.dontSeeElement(resultNames);
});
