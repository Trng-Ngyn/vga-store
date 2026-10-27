# BÁO CÁO THIẾT KẾ TEST CASES BẰNG PHƯƠNG PHÁP PHÂN VÙNG TƯƠNG ĐƯƠNG VÀ GIÁ TRỊ BIÊN
**Môn học:** Kiểm chứng phần mềm (Software Testing & QA)  
**Dự án:** VGA Store — Cửa hàng Card Màn Hình Online  
**Nhóm thực hiện:** Trần Đình Trọng, Ngô Hữu Phước, Phan Khôi, Lê Minh Hiếu, Nguyễn Văn Huy, Duy Vũ  
**Chức năng áp dụng:** Form Đặt hàng & Thanh toán (Checkout) và Form Đăng ký tài khoản (Register)

---

## PHẦN 1: BẢNG ĐIỀU KIỆN TEST (TEST CONDITIONS)
*Áp dụng kỹ thuật Equivalence Partitioning (EP) & Boundary Value Analysis (BVA)*

### 1.1 Chức năng: Đặt hàng & Thanh toán (Checkout Order)

| Conditions (Điều kiện) | Valid Partitions (Phân vùng hợp lệ) | Tag | Invalid Partitions (Phân vùng không hợp lệ) | Tag | Valid Boundaries (Biên hợp lệ) | Tag |
| :--- | :--- | :---: | :--- | :---: | :--- | :---: |
| **Customer name**<br>*(Họ và tên người nhận)* | • 2 – 50 ký tự<br>• Ký tự chữ cái hợp lệ | **V1**<br>**V2** | • < 2 ký tự (1 chữ hoặc để trống)<br>• > 50 ký tự<br>• Chứa số hoặc ký tự đặc biệt (@, #...) | **X1**<br>**X2**<br>**X3** | • 2 ký tự (Min)<br>• 3 ký tự (Min + 1)<br>• 25 ký tự (Nominal - Giữa)<br>• 49 ký tự (Max - 1)<br>• 50 ký tự (Max) | **B1**<br>**B2**<br>**B3**<br>**B4**<br>**B5** |
| **Phone number**<br>*(Số điện thoại nhận hàng)* | • Từ 10 – 15 ký tự số<br>• Bắt đầu bằng chữ số 0<br>• Toàn bộ là ký tự số | **V3**<br>**V4**<br>**V5** | • < 10 chữ số (thiếu số)<br>• > 15 chữ số (quá dài)<br>• Bắt đầu bằng số khác 0<br>• Chứa chữ cái hoặc ký tự đặc biệt | **X4**<br>**X5**<br>**X6**<br>**X7** | • 10 chữ số (Min - chuẩn VN: 0901234567)<br>• 11 chữ số (Min + 1)<br>• 15 chữ số (Max chuẩn quốc tế) | **B6**<br>**B7**<br>**B8** |
| **Quantity**<br>*(Số lượng VGA mua)* | • Từ 1 – 10 chiếc<br>• Là số nguyên dương | **V6**<br>**V7** | • < 1 (nhập 0 hoặc số âm)<br>• > 10 chiếc (vượt hạn mức bán lẻ)<br>• Chứa số thập phân hoặc chữ cái | **X8**<br>**X9**<br>**X10** | • 1 chiếc (Min)<br>• 2 chiếc (Min + 1)<br>• 5 chiếc (Nominal)<br>• 9 chiếc (Max - 1)<br>• 10 chiếc (Max) | **B9**<br>**B10**<br>**B11**<br>**B12**<br>**B13** |
| **Shipping Address**<br>*(Địa chỉ giao hàng)* | • Từ 5 – 255 ký tự<br>• Chuỗi ký tự hợp lệ | **V8**<br>**V9** | • < 5 ký tự (quá ngắn)<br>• > 255 ký tự (vượt độ dài DB) | **X11**<br>**X12** | • 5 ký tự (Min: "Ha Noi")<br>• 6 ký tự (Min + 1)<br>• 254 ký tự (Max - 1)<br>• 255 ký tự (Max) | **B14**<br>**B15**<br>**B16**<br>**B17** |

---

## PHẦN 2: THIẾT KẾ TEST CASES (TEST CASES DESIGN)
*Kết hợp các giá trị đầu vào để tối ưu số lượng ca kiểm thử và đạt độ phủ Tags cao nhất*

| Test Case | Input (Dữ liệu thử nghiệm) | Expected Outcome (Kết quả mong đợi) | New Tags Covered (Nhãn Tags được phủ) |
| :---: | :--- | :--- | :--- |
| **TC_01**<br>*(Happy Path - Dữ liệu chuẩn)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "0908123456"<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc, TP.HCM" | Hệ thống chấp nhận đơn hàng, chuyển hướng sang cổng thanh toán VNPAY thành công, mã HTTP 200. | **V1, V2, V3, V4, V5, V6, V7, V8, V9, B2, B7, B10** |
| **TC_02**<br>*(Kiểm thử biên Min)* | • **Name:** "An" (2 ký tự)<br>• **Phone:** "0901234567" (10 số)<br>• **Quantity:** 1 chiếc<br>• **Address:** "Ha Noi" (5 ký tự) | Đặt hàng thành công với các giá trị biên nhỏ nhất hợp lệ. | **B1, B6, B9, B14** |
| **TC_03**<br>*(Kiểm thử biên Max)* | • **Name:** Chuỗi 50 ký tự chữ hợp lệ<br>• **Phone:** "090123456789012" (15 số)<br>• **Quantity:** 10 chiếc<br>• **Address:** Chuỗi 255 ký tự hợp lệ | Đặt hàng thành công với các giá trị biên lớn nhất hợp lệ. | **B4, B5, B8, B12, B13, B16, B17** |
| **TC_04**<br>*(Kiểm thử biên giữa - Nominal)* | • **Name:** "Phan Khoi Developer" (19 ký tự)<br>• **Phone:** "0912345678"<br>• **Quantity:** 5 chiếc<br>• **Address:** "123 Nguyen Trai, Quan 1, TP Ho Chi Minh" | Đặt hàng thành công với các giá trị danh nghĩa tiêu chuẩn. | **B3, B11, B15** |
| **TC_05**<br>*(Negative - Tên quá ngắn)* | • **Name:** "A" (1 ký tự)<br>• **Phone:** "0908123456"<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Họ và tên người nhận phải có ít nhất 2 ký tự"*, không tạo đơn hàng. | **X1** |
| **TC_06**<br>*(Negative - Tên quá dài)* | • **Name:** Chuỗi 51 ký tự<br>• **Phone:** "0908123456"<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Họ và tên không được vượt quá 50 ký tự"*. | **X2** |
| **TC_07**<br>*(Negative - Tên chứa ký tự đặc biệt)* | • **Name:** "Trong@123#$"<br>• **Phone:** "0908123456"<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Họ và tên chỉ được chứa chữ cái và khoảng trắng"*. | **X3** |
| **TC_08**<br>*(Negative - SĐT thiếu số)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "090812345" (9 số)<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Số điện thoại phải có từ 10 - 15 ký tự"*, HTTP 400. | **X4** |
| **TC_09**<br>*(Negative - SĐT quá dài)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "09081234567890123" (17 số)<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Số điện thoại không được vượt quá 15 ký tự"*. | **X5** |
| **TC_10**<br>*(Negative - SĐT không bắt đầu bằng số 0)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "9081234567" (bắt đầu bằng 9)<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Số điện thoại không hợp lệ (phải bắt đầu bằng chữ số 0)"*. | **X6** |
| **TC_11**<br>*(Negative - SĐT chứa chữ cái)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "09081234ab"<br>• **Quantity:** 2<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Số điện thoại chỉ được chứa ký tự số"*. | **X7** |
| **TC_12**<br>*(Negative - Số lượng bằng 0 hoặc âm)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "0908123456"<br>• **Quantity:** 0 (hoặc -1)<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Số lượng phải lớn hơn hoặc bằng 1"*. | **X8** |
| **TC_13**<br>*(Negative - Số lượng vượt quá tối đa)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "0908123456"<br>• **Quantity:** 11 chiếc<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi nghiệp vụ: *"Vượt quá hạn mức bán lẻ (tối đa 10 chiếc/đơn)"*. | **X9** |
| **TC_14**<br>*(Negative - Số lượng không phải số nguyên)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "0908123456"<br>• **Quantity:** "hai" (hoặc 1.5)<br>• **Address:** "So 1 Vo Van Ngan, Thu Duc" | Báo lỗi validation: *"Số lượng phải là số nguyên dương"*. | **X10** |
| **TC_15**<br>*(Negative - Địa chỉ quá ngắn)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "0908123456"<br>• **Quantity:** 2<br>• **Address:** "HCM" (3 ký tự) | Báo lỗi validation: *"Địa chỉ giao hàng phải có ít nhất 5 ký tự"*. | **X11** |
| **TC_16**<br>*(Negative - Địa chỉ vượt quá 255 ký tự)* | • **Name:** "Tran Dinh Trong"<br>• **Phone:** "0908123456"<br>• **Quantity:** 2<br>• **Address:** Chuỗi 256 ký tự | Báo lỗi validation: *"Địa chỉ không được vượt quá 255 ký tự"*. | **X12** |

---

## PHẦN 3: ĐÁNH GIÁ ĐỘ PHỦ TAGS (TAG COVERAGE MATRIX)

- **Tổng số nhãn Valid (V):** 9/9 Tags (Độ phủ: **100%**)
- **Tổng số nhãn Invalid (X):** 12/12 Tags (Độ phủ: **100%**)
- **Tổng số nhãn Boundary (B):** 17/17 Tags (Độ phủ: **100%**)
- **Kết luận:** Bộ 16 Test Cases được thiết kế đảm bảo kiểm thử toàn diện các luồng nghiệp vụ cốt lõi, giá trị biên giáp ranh và xử lý ngoại lệ theo đúng tiêu chuẩn kiểm chứng phần mềm.
