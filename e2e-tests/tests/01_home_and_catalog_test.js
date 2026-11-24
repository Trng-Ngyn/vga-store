Feature('Trang chủ và Danh mục sản phẩm VGA Store').tag('@catalog');

Scenario('Trang chủ hiển thị header, logo và sản phẩm bán chạy', ({ I }) => {
  I.amOnPage('/');
  I.seeElement('header');
  I.seeElement('header img[alt="VGA Store Logo"]');
  I.waitForVisible('.bs-grid .bs-name', 15);
  I.see('SẢN PHẨM BÁN CHẠY', '.bs-title');
});

Scenario('Mở đúng sản phẩm từ trang chủ và hiển thị thông số GPU', async ({ I }) => {
  const firstCard = locate('.bs-grid .asus-corner-card').first();
  I.amOnPage('/');
  I.waitForVisible(firstCard, 15);
  const productName = await I.grabTextFrom(firstCard.find('.bs-name'));
  I.click(firstCard);
  I.seeInCurrentUrl('/product/');
  I.waitForVisible('.specs-table', 15);
  I.see(productName, 'h1');
  I.see('Model GPU', '.specs-table');
  I.see('Dung lượng VRAM', '.specs-table');
});
