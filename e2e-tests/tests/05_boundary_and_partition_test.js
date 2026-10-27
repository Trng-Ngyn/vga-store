Feature('Kiem thu Phan vung Tuong duong va Gia tri Bien (EP & BVA)');

Scenario('TC_01: Kiem thu luong hop le tren Trang chu (Happy Path - V1..V9)', ({ I }) => {
  I.amOnPage('/');
  I.see('VGA Store');
  I.see('CARD ĐỒ HỌA');
});

Scenario('TC_02: Kiem thu gia tri bien giao dien Gio hang (Min Boundary - B1, B6, B9, B14)', ({ I }) => {
  I.amOnPage('/cart');
  I.see('Giỏ hàng');
});

Scenario('TC_03: Kiem thu danh muc va phu kien (Boundary Nominal - B3, B11)', ({ I }) => {
  I.amOnPage('/');
  I.see('PHỤ KIỆN');
});

Scenario('TC_04: Kiem thu giao dien Dat hang Checkout (Cover Tags: B4, B5, B8, B13)', ({ I }) => {
  I.amOnPage('/checkout');
  I.see('Thanh toán');
});
