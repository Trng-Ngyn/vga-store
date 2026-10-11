// Custom helper steps for VGA Store E2E Tests
module.exports = function() {
  return actor({
    // Helper function: Đăng nhập người dùng
    loginAsUser: function(email, password) {
      this.amOnPage('/login');
      this.fillField('input[type="email"]', email);
      this.fillField('input[type="password"]', password);
      this.click('button[type="submit"]');
    },

    // Helper function: Tìm kiếm VGA
    searchProduct: function(keyword) {
      this.amOnPage('/');
      this.fillField('input[placeholder*="Tìm kiếm"]', keyword);
      this.pressKey('Enter');
    }
  });
};
