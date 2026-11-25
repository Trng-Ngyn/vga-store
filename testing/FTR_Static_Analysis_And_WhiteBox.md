# BÁO CÁO KIỂM THỬ TĨNH (FTR) & PHÂN TÍCH CẤU TRÚC HỘP TRẮNG
**Dự án:** VGA Store — E-Commerce System  
**Tham chiếu lý thuyết:** Chương III (Kiểm thử tĩnh) & Chương IV (Thiết kế test Hộp trắng / Hộp đen)

---

## PHẦN 1: QUY TRÌNH FORMAL TECHNICAL REVIEW (FTR) — CHƯƠNG III

### 1.1 Quy trình 6 bước thực hiện tại nhóm VGA Store
1. **Planning (Lập kế hoạch):** Xác định đối tượng review gồm SRS, mã nguồn `service/`, `security/` Backend và các trang React (`Checkout.jsx`, `ProductDetail.jsx`, `Profile.jsx`). Trưởng nhóm Trần Đình Trọng phân công tài liệu và tiêu chí đạt.
2. **Kick-off Meeting:** Phổ biến mục tiêu kiểm tra bảo mật JWT/RBAC, quy tắc trạng thái đơn hàng, xử lý ngoại lệ và chuẩn coding quy định tại dự án.
3. **Preparation (Chuẩn bị cá nhân với Checklist):** Mỗi thành viên đọc mã nguồn độc lập trong 2 giờ dựa trên bảng **FTR Review Checklist** bên dưới.
4. **Review Meeting (Họp rà soát):** Moderator (Trần Đình Trọng), Author (Lê Minh Hiếu / Nguyễn Văn Huy), Reviewers (Ngô Hữu Phước, Phan Khôi, Duy Vũ) ghi nhận danh sách lỗi (`BUG-01..BUG-09`) và cảnh báo ESLint/Qodana.
5. **Rework (Khắc phục):** Tác giả sửa các lỗi nghiêm trọng (`CartService @Transactional`, `SecurityConfig /api/settings/public`, `ProductDetail.jsx`, `Profile.jsx`, `admin/eslint.config.js`).
6. **Follow-up (Kiểm tra lại):** Chạy lại Maven JaCoCo, ESLint và Postman Security Suite để xác nhận đóng ticket trên Jira.

### 1.2 FTR Code Review Checklist áp dụng
| Hạng mục | Tiêu chí kiểm tra | Kết quả rà soát thực tế |
| :--- | :--- | :--- |
| **Security / Auth** | Endpoint public/private phân quyền chuẩn xác, không lộ dữ liệu (IDOR) | Phát hiện `GET /api/settings/public` thiếu `.permitAll()` (**BUG-02** - Đã sửa); `PaymentService.getPaymentByOrderId` thiếu check owner (**BUG-08** - Backlog) |
| **Transactions** | `@Transactional(readOnly=true)` không được gọi hàm ghi (`save`) | Phát hiện `CartService.getMyCart()` lỗi 500 trên Docker cũ (**BUG-01** - Đã sửa) |
| **Control Flow / Dead Code** | Không có nhánh điều kiện luôn sai hoặc filter chạy trùng | Phát hiện `BrandService.updateBrand` ghi đè tên trước khi so sánh tạo slug (**BUG-09**); `JwtFilter` trùng `JwtAuthFilter` (**BUG-06**) |
| **State Transition** | Kiểm tra chuyển trạng thái hợp lệ cho Đơn hàng (`PENDING` -> `DELIVERED`) | Phát hiện `OrderService.updateOrderStatus` thiếu guard chặn `DELIVERED -> CANCELLED` (**BUG-05**) |
| **Data Flow / Null Safety** | Mọi biến được khai báo/import trước khi gọi (`defined before use`) | ESLint phát hiện `toastSuccess` (`ProductDetail.jsx:201`) & `axiosClient` (`Profile.jsx:413`) chưa import (**BUG-03, BUG-04** - Đã sửa) |

---

## PHẦN 2: KIỂM THỬ HỘP TRẮNG CẤU TRÚC (CFG, CYCLOMATIC COMPLEXITY, MCDC & DATA FLOW)

### 2.1 Phân tích `AuthService.register(RegisterRequest)`
Các quyết định rẽ nhánh trong hàm:
- **Node 1:** Start
- **D1 (`P1`):** `if (userRepository.existsByUsername(req.getUsername()))` -> ném `RuntimeException`
- **D2 (`P2`):** `if (userRepository.existsByEmail(req.getEmail()))` -> ném `RuntimeException`
- **D3 (`P3`):** `if (req.getFullName() != null && !req.getFullName().isEmpty())` -> gán `fullName`, ngược lại dùng `username`
- Lưu DB & tạo `jwtUtil.generateToken(...)` -> **Exit Node**.

**Độ phức tạp Cyclomatic:**
- Số nhánh quyết định đơn giản (hoặc theo điều kiện kép):
  - Xét cấu trúc đồ thị dòng điều khiển chuẩn (7 đỉnh `N = 7`, 9 cung `E = 9`, số vị từ đơn `P = 2` cho `if..else` đơn + `D3` = 3 vùng độc lập hoặc tính cả điều kiện con `&&` thành `V(G) = 5`):
  - Với đồ thị nhánh mức Statement/Decision (`D1`, `D2`, `D3` gồm 3 câu lệnh `if`): $V(G) = P + 1 = 3 + 1 = 4$ đường thực thi độc lập tối thiểu (**Basic Path Set**):
    1. Path 1: `1 -> D1(T) -> ThrowUsernameExists` (`WB-AUTH-01`)
    2. Path 2: `1 -> D1(F) -> D2(T) -> ThrowEmailExists` (`WB-AUTH-02`)
    3. Path 3: `1 -> D1(F) -> D2(F) -> D3(T) -> Save&Token` (`WB-AUTH-03a`)
    4. Path 4: `1 -> D1(F) -> D2(F) -> D3(F) -> FallbackUsername -> Save&Token` (`WB-AUTH-03b` & `null` case)

**Kiểm tra Condition & Multiple Condition Coverage (MCC) tại `D3 (A && B)` với `A = (fullName != null)`, `B = (!fullName.isEmpty())`:**
| Case | A (`fullName != null`) | B (`!isEmpty()`) | Quyết định `D3` | Test Case phủ tương ứng |
| :---: | :---: | :---: | :---: | :--- |
| C1 | False (`null`) | Short-circuit (N/A) | **False** (fallback `username`) | `AuthServiceWhiteBoxTest` — `fullName = null` |
| C2 | True (`"Nguyen Van A"`) | True | **True** (dùng `fullName`) | `AuthServiceWhiteBoxTest` — `fullName = "Nguyen Van A"` |
| C3 | True (`""`) | False | **False** (fallback `username`) | `AuthServiceWhiteBoxTest` — `fullName = ""` |

-> Đạt **100% Statement Coverage (68/68 lines)** và **100% Branch Coverage (22/22 branches)** trên `AuthService` theo báo cáo JaCoCo!

### 2.2 Phân tích Data Flow (`Def-Use`) cho biến `existing` / `totalQty` trong `CartService.addToCart()`
1. `cart` được **Define** (`def`) từ `getOrCreateCart(user)` -> **Use** (`p-use` & `c-use`) trong tìm `existingItem` và `cart.recalculateTotal()`.
2. `newQty` được **Define** từ `existing != null ? existing.getQuantity() + req.getQuantity() : req.getQuantity()` -> **p-use** kiểm tra `if (newQty > product.getStock())` -> **c-use** cập nhật `item.setQuantity(newQty)`. Không tồn tại anomaly (`ur`, `du`, `dd`).

---

## PHẦN 3: DECISION TABLE & STATE TRANSITION & ERROR GUESSING (CHƯƠNG IV)

### 3.1 Decision Table — Nghiệp vụ Checkout & Áp dụng Thanh toán VGA Store
| Điều kiện / Hành động | R1 | R2 | R3 | R4 | R5 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| C1: Đã đăng nhập (JWT hợp lệ)? | **F** | **T** | **T** | **T** | **T** |
| C2: Giỏ hàng có sản phẩm (`items > 0`)? | - | **F** | **T** | **T** | **T** |
| C3: Tồn kho đủ (`stock >= qty`) & Địa chỉ/SĐT hợp lệ? | - | - | **F** | **T** | **T** |
| C4: Phương thức thanh toán = Online (VNPay/MoMo)? | - | - | - | **F (COD)** | **T (Online)** |
| **A1: Chặn `401/403` Unauthorized** | **X** | | | | |
| **A2: Báo lỗi `400 Bad Request` (Giỏ trống / Validation / Hết hàng)** | | **X** | **X** | | |
| **A3: Tạo Order `PENDING`, trừ kho, dọn giỏ hàng** | | | | **X** | **X** |
| **A4: Sinh URL Redirect cổng VNPay/MoMo ký HMAC-SHA512/256** | | | | | **X** |

### 3.2 Error Guessing & Exploratory Testing Checklist
- Gửi `quantity = 0`, `-1`, `999999` khi thêm giỏ hàng (BVA & Negative).
- Gửi chuỗi SQL Injection (`' OR '1'='1`) vào `/api/products/search` và `/api/auth/login`.
- Gửi XSS Payload (`<script>alert(1)</script>`) vào form Đăng ký.
- Giả mạo chữ ký JWT (`tamperedToken`) truy cập API riêng tư (`/api/orders`, `/api/admin/users`).
- Gửi callback giả mạo chữ ký VNPay/MoMo (`PaymentController` từ chối chữ ký sai).
- Kiểm tra truy cập trực tiếp route Admin `http://localhost:5174/` khi chưa đăng nhập (Redirect về `/login`).
