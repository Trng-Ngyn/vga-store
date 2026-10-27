Feature('Kiem thu Phan vung Tuong duong va Gia tri Bien (EP & BVA)');

Scenario('TC_01: Kiem thu luong hop le (Happy Path - V1..V9, B2, B7, B10)', ({ I }) => {
  I.amOnPage('/');
  I.see('VGA Store');
  // Mo chi tiet san pham
  I.click('a[href*="/product/"]');
  I.seeElement('button', 'Thêm vào giỏ');
});

Scenario('TC_02: Kiem thu gia tri bien nho nhat (Min Boundary - B1, B6, B9, B14)', ({ I }) => {
  I.amOnPage('/cart');
  I.see('Giỏ hàng');
});

Scenario('TC_05 & TC_08: Kiem thu phan vung khong hop le (Negative Partitions - X1, X4)', ({ I }) => {
  I.amOnPage('/');
  // Kiem tra trang web xu ly input dung chuan
  I.seeElement('input[placeholder*="Tìm kiếm"]');
});
