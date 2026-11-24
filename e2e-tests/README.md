# 🧪 CodeceptJS E2E Testing Suite — VGA Store

Bộ kiểm thử tự động End-to-End (E2E / Acceptance Testing) cho dự án **VGA Store** sử dụng framework **[CodeceptJS](https://codecept.io/)** với Playwright driver.

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Tests

### 1. Cài đặt thư viện
```bash
cd e2e-tests
npm install
```

### 2. Cài đặt trình duyệt Playwright (lần đầu tiên)
```bash
npx playwright install chromium
```

### 3. Chạy kiểm thử tự động
```bash
# Chạy với giao diện trình duyệt trực quan:
npm test

# Chạy ở chế độ ngầm (Headless - dùng cho CI/CD):
npm run test:headless

# Chạy riêng nhóm test KAN-12 đến KAN-14:
npm run test:headless -- --grep '@catalog'
npm run test:ui -- --grep '@catalog'
```

Khởi động frontend, backend và nạp dữ liệu mẫu trước khi chạy. Nhóm test
`@catalog` cần danh mục có ít nhất một sản phẩm RTX.

### 4. Cấu hình biến môi trường
Mặc định bài test gọi đến `http://localhost:5173`. Có thể đổi sang server khác:
```bash
BASE_URL=http://your-server.com npm test
```
