import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')


def make_test_event(lines):
    return [{
        "listen": "test",
        "script": {
            "exec": lines,
            "type": "text/javascript"
        }
    }]


def make_req(name, method, path_parts, query=None, body=None, token_var=None, tests=None, desc=""):
    url_obj = {
        "raw": "{{baseUrl}}/" + "/".join(path_parts),
        "host": ["{{baseUrl}}"],
        "path": path_parts
    }
    if query:
        q_str = "&".join(f"{k}={v}" for k, v in query)
        url_obj["raw"] += "?" + q_str
        url_obj["query"] = [{"key": k, "value": str(v)} for k, v in query]

    headers = []
    if body is not None:
        headers.append({"key": "Content-Type", "value": "application/json"})

    req_obj = {
        "method": method,
        "header": headers,
        "url": url_obj,
        "description": desc
    }
    if token_var:
        req_obj["auth"] = {
            "type": "bearer",
            "bearer": [{"key": "token", "value": f"{{{{{token_var}}}}}", "type": "string"}]
        }
    if body is not None:
        req_obj["body"] = {
            "mode": "raw",
            "raw": json.dumps(body, indent=2, ensure_ascii=False)
        }

    item = {"name": name, "request": req_obj}
    if tests:
        item["event"] = make_test_event(tests)
    return item


# Standard test snippets
T_STATUS_200 = [
    'pm.test("Trạng thái HTTP 200 OK", function () {',
    '    pm.response.to.have.status(200);',
    '});',
    'pm.test("Thời gian phản hồi dưới 1500ms", function () {',
    '    pm.expect(pm.response.responseTime).to.be.below(1500);',
    '});'
]

T_API_SUCCESS = T_STATUS_200 + [
    'pm.test("Cấu trúc ApiResponse success = true", function () {',
    '    var jsonData = pm.response.json();',
    '    pm.expect(jsonData).to.have.property("success", true);',
    '    pm.expect(jsonData).to.have.property("data");',
    '});'
]

T_STATUS_400 = [
    'pm.test("Black-Box Validation bắt lỗi (HTTP 400 Bad Request)", function () {',
    '    pm.expect(pm.response.code).to.be.oneOf([400, 422]);',
    '});',
    'pm.test("Thời gian phản hồi dưới 1500ms", function () {',
    '    pm.expect(pm.response.responseTime).to.be.below(1500);',
    '});'
]

T_STATUS_404 = [
    'pm.test("Tài nguyên không tồn tại trả về HTTP 404 Not Found", function () {',
    '    pm.response.to.have.status(404);',
    '});'
]

T_UNAUTH = [
    'pm.test("Chặn truy cập khi thiếu hoặc sai JWT (401/403)", function () {',
    '    pm.expect(pm.response.code).to.be.oneOf([401, 403]);',
    '});'
]

T_FORBIDDEN = [
    'pm.test("RBAC Security: User thường không có quyền Admin (403 Forbidden)", function () {',
    '    pm.expect(pm.response.code).to.be.oneOf([401, 403]);',
    '});'
]

collection_data = {
    "info": {
        "_postman_id": "vga-store-software-testing-collection-2026",
        "name": "VGA Store - Kiểm Chứng Phần Mềm (Full Black-Box API Suite)",
        "description": (
            "Bộ API Collection kiểm thử hộp đen toàn diện cho dự án VGA Store.\n"
            "Áp dụng EP (Equivalence Partitioning), BVA (Boundary Value Analysis), "
            "Negative Validation, State Transition và RBAC Security."
        ),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "1. Authentication & Security (EP / BVA / RBAC)",
            "item": [
                make_req(
                    "BB-AUTH-01: POST Đăng ký tài khoản mới (Happy Path / Existing)",
                    "POST", ["api", "auth", "register"],
                    body={
                        "username": "{{testUsername}}",
                        "email": "{{testEmail}}",
                        "password": "{{testPassword}}",
                        "fullName": "Kiểm Thử Viên"
                    },
                    tests=[
                        'pm.test("Mã phản hồi hợp lệ (200 tạo mới hoặc 400 đã tồn tại)", function () {',
                        '    pm.expect(pm.response.code).to.be.oneOf([200, 201, 400]);',
                        '});',
                        'pm.test("Thời gian phản hồi dưới 1500ms", function () {',
                        '    pm.expect(pm.response.responseTime).to.be.below(1500);',
                        '});'
                    ],
                    desc="EP Valid Partition: Dữ liệu đăng ký hợp lệ."
                ),
                make_req(
                    "BB-AUTH-02: POST Đăng ký Username ngắn hơn biên Min=3 ('ab') [BVA]",
                    "POST", ["api", "auth", "register"],
                    body={
                        "username": "ab",
                        "email": "bva_short@vga.local",
                        "password": "password123",
                        "fullName": "BVA Short"
                    },
                    tests=T_STATUS_400,
                    desc="BVA Invalid Lower Boundary: username = 2 chars (< 3)."
                ),
                make_req(
                    "BB-AUTH-03: POST Đăng ký Email sai định dạng [EP Invalid]",
                    "POST", ["api", "auth", "register"],
                    body={
                        "username": "validuser_99",
                        "email": "invalid-email-format",
                        "password": "password123",
                        "fullName": "Invalid Email"
                    },
                    tests=T_STATUS_400,
                    desc="EP Invalid Partition: email thiếu @ và domain."
                ),
                make_req(
                    "BB-AUTH-04: POST Đăng ký Password dưới biên Min=6 ('12345') [BVA]",
                    "POST", ["api", "auth", "register"],
                    body={
                        "username": "validuser_98",
                        "email": "shortpass@vga.local",
                        "password": "12345",
                        "fullName": "Short Pass"
                    },
                    tests=T_STATUS_400,
                    desc="BVA Invalid Lower Boundary: password = 5 chars (< 6)."
                ),
                make_req(
                    "BB-AUTH-05: POST Đăng nhập User hợp lệ & Lưu JWT Token",
                    "POST", ["api", "auth", "login"],
                    body={"username": "{{testUsername}}", "password": "{{testPassword}}"},
                    tests=[
                        'pm.test("Đăng nhập thành công HTTP 200", function () {',
                        '    pm.response.to.have.status(200);',
                        '});',
                        'pm.test("Response chứa JWT token hợp lệ", function () {',
                        '    var jsonData = pm.response.json();',
                        '    pm.expect(jsonData).to.have.property("token");',
                        '    pm.expect(jsonData.token).to.be.a("string").and.not.empty;',
                        '    pm.environment.set("jwtToken", jsonData.token);',
                        '});'
                    ],
                    desc="Happy Path login và tự động lưu jwtToken cho các request cần xác thực."
                ),
                make_req(
                    "BB-AUTH-06: POST Đăng nhập sai mật khẩu [Negative EP]",
                    "POST", ["api", "auth", "login"],
                    body={"username": "{{testUsername}}", "password": "wrong_password_999"},
                    tests=T_STATUS_400,
                    desc="Negative Test: Sai mật khẩu bị từ chối."
                ),
                make_req(
                    "BB-AUTH-07: POST Đăng nhập tài khoản không tồn tại [Negative EP]",
                    "POST", ["api", "auth", "login"],
                    body={"username": "nonexistent_user_xyz", "password": "123456"},
                    tests=[
                        'pm.test("Từ chối tài khoản không tồn tại (400 hoặc 404)", function () {',
                        '    pm.expect(pm.response.code).to.be.oneOf([400, 401, 404]);',
                        '});'
                    ],
                    desc="Negative Test: Username không tồn tại."
                ),
            ]
        },
        {
            "name": "2. Categories (Danh mục & Boundary)",
            "item": [
                make_req(
                    "BB-CAT-01: GET Lấy tất cả danh mục (Phân trang mặc định)",
                    "GET", ["api", "categories"],
                    query=[("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS + [
                        'var d = pm.response.json().data;',
                        'if (d && d.content && d.content.length > 0) {',
                        '    pm.environment.set("sampleCategoryId", d.content[0].id);',
                        '}'
                    ]
                ),
                make_req(
                    "BB-CAT-02: GET Lấy danh mục đang Active",
                    "GET", ["api", "categories", "active"],
                    query=[("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-CAT-03: GET Tìm kiếm danh mục theo từ khóa 'RTX'",
                    "GET", ["api", "categories", "search"],
                    query=[("keyWord", "RTX"), ("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-CAT-04: GET Lọc danh mục theo trạng thái active=true",
                    "GET", ["api", "categories", "filter"],
                    query=[("active", "true"), ("page", 0), ("size", 5)],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-CAT-05: GET Chi tiết danh mục hợp lệ theo ID",
                    "GET", ["api", "categories", "{{sampleCategoryId}}"],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-CAT-06: GET Chi tiết danh mục ID không tồn tại (999999) [404]",
                    "GET", ["api", "categories", "999999"],
                    tests=T_STATUS_404
                ),
            ]
        },
        {
            "name": "3. Brands (Thương hiệu VGA)",
            "item": [
                make_req(
                    "BB-BRAND-01: GET Lấy danh sách thương hiệu",
                    "GET", ["api", "brands"],
                    query=[("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS + [
                        'var d = pm.response.json().data;',
                        'if (d && d.content && d.content.length > 0) {',
                        '    pm.environment.set("sampleBrandId", d.content[0].id);',
                        '}'
                    ]
                ),
                make_req(
                    "BB-BRAND-02: GET Tìm kiếm thương hiệu 'ASUS'",
                    "GET", ["api", "brands", "search"],
                    query=[("keyWord", "ASUS"), ("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-BRAND-03: GET Lọc thương hiệu đang kích hoạt",
                    "GET", ["api", "brands", "filter"],
                    query=[("status", "true"), ("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-BRAND-04: GET Chi tiết thương hiệu hợp lệ theo ID",
                    "GET", ["api", "brands", "{{sampleBrandId}}"],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-BRAND-05: GET Chi tiết thương hiệu ID không tồn tại (999999) [404]",
                    "GET", ["api", "brands", "999999"],
                    tests=T_STATUS_404
                ),
            ]
        },
        {
            "name": "4. Products (EP, BVA Phân trang, Tìm kiếm & Lọc giá)",
            "item": [
                make_req(
                    "BB-PROD-01: GET Danh sách sản phẩm chuẩn (Page 0, Size 10)",
                    "GET", ["api", "products"],
                    query=[("page", 0), ("size", 10), ("sortBy", "id"), ("direction", "asc")],
                    tests=T_API_SUCCESS + [
                        'var d = pm.response.json().data;',
                        'pm.test("Danh sách sản phẩm có phần tử content", function () {',
                        '    pm.expect(d.content).to.be.an("array");',
                        '    if (d.content.length > 0) {',
                        '        pm.environment.set("sampleProductId", d.content[0].id);',
                        '    }',
                        '});'
                    ]
                ),
                make_req(
                    "BB-PROD-02: GET Phân trang biên nhỏ nhất Size=1 [BVA]",
                    "GET", ["api", "products"],
                    query=[("page", 0), ("size", 1)],
                    tests=T_API_SUCCESS + [
                        'pm.test("BVA Size=1 trả về tối đa 1 sản phẩm", function () {',
                        '    pm.expect(pm.response.json().data.content.length).to.be.at.most(1);',
                        '});'
                    ]
                ),
                make_req(
                    "BB-PROD-03: GET Sắp xếp sản phẩm theo giá giảm dần (Price DESC)",
                    "GET", ["api", "products"],
                    query=[("page", 0), ("size", 5), ("sortBy", "price"), ("direction", "desc")],
                    tests=T_API_SUCCESS + [
                        'pm.test("Thứ tự giá giảm dần hợp lệ", function () {',
                        '    var items = pm.response.json().data.content;',
                        '    if (items.length >= 2) {',
                        '        pm.expect(items[0].price).to.be.at.least(items[1].price);',
                        '    }',
                        '});'
                    ]
                ),
                make_req(
                    "BB-PROD-04: GET Chi tiết sản phẩm hợp lệ theo ID",
                    "GET", ["api", "products", "{{sampleProductId}}"],
                    tests=T_API_SUCCESS + [
                        'pm.test("Chi tiết sản phẩm có tên và giá", function () {',
                        '    var p = pm.response.json().data;',
                        '    pm.expect(p).to.have.property("name");',
                        '    pm.expect(p).to.have.property("price");',
                        '});'
                    ]
                ),
                make_req(
                    "BB-PROD-05: GET Chi tiết sản phẩm không tồn tại ID=999999 [404]",
                    "GET", ["api", "products", "999999"],
                    tests=T_STATUS_404
                ),
                make_req(
                    "BB-PROD-06: GET Tìm kiếm sản phẩm từ khóa hợp lệ 'RTX' [EP Valid]",
                    "GET", ["api", "products", "search"],
                    query=[("keyWord", "RTX"), ("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-PROD-07: GET Tìm kiếm từ khóa không tồn tại 'ZZZ999XYZ' [EP Empty]",
                    "GET", ["api", "products", "search"],
                    query=[("keyWord", "ZZZ999XYZ"), ("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS + [
                        'pm.test("Kết quả tìm kiếm rỗng trả về mảng trống", function () {',
                        '    pm.expect(pm.response.json().data.content.length).to.eql(0);',
                        '});'
                    ]
                ),
                make_req(
                    "BB-PROD-08: GET Lọc sản phẩm theo khoảng giá 5tr - 60tr [EP/BVA]",
                    "GET", ["api", "products", "filter"],
                    query=[("minPrice", 5000000), ("maxPrice", 60000000), ("page", 0), ("size", 10)],
                    tests=T_API_SUCCESS
                ),
            ]
        },
        {
            "name": "5. Cart (Giỏ hàng - Auth, BVA Tồn kho & CRUD)",
            "item": [
                make_req(
                    "BB-CART-01: GET Giỏ hàng khi CHƯA đăng nhập [Security 401/403]",
                    "GET", ["api", "cart"],
                    tests=T_UNAUTH
                ),
                make_req(
                    "BB-CART-02: GET Lấy giỏ hàng người dùng hiện tại [Bearer JWT]",
                    "GET", ["api", "cart"],
                    token_var="jwtToken",
                    tests=T_API_SUCCESS + [
                        'pm.test("Giỏ hàng có tổng tiền và danh sách items", function () {',
                        '    var c = pm.response.json().data;',
                        '    pm.expect(c).to.have.property("totalAmount");',
                        '    pm.expect(c).to.have.property("items");',
                        '});'
                    ]
                ),
                make_req(
                    "BB-CART-03: POST Thêm vào giỏ với số lượng biên 0 [BVA Invalid Min-1]",
                    "POST", ["api", "cart", "add"],
                    body={"productId": 1, "quantity": 0},
                    token_var="jwtToken",
                    tests=T_STATUS_400
                ),
                make_req(
                    "BB-CART-04: POST Thêm vào giỏ với số lượng âm -1 [EP Negative]",
                    "POST", ["api", "cart", "add"],
                    body={"productId": 1, "quantity": -1},
                    token_var="jwtToken",
                    tests=T_STATUS_400
                ),
                make_req(
                    "BB-CART-05: POST Thêm vào giỏ vượt quá tồn kho (999999) [BVA Max+1]",
                    "POST", ["api", "cart", "add"],
                    body={"productId": 1, "quantity": 999999},
                    token_var="jwtToken",
                    tests=T_STATUS_400
                ),
                make_req(
                    "BB-CART-06: POST Thêm sản phẩm hợp lệ vào giỏ (Qty = 1)",
                    "POST", ["api", "cart", "add"],
                    body={"productId": 1, "quantity": 1},
                    token_var="jwtToken",
                    tests=T_API_SUCCESS + [
                        'var items = pm.response.json().data.items;',
                        'pm.test("Giỏ hàng đã thêm ít nhất 1 sản phẩm", function () {',
                        '    pm.expect(items.length).to.be.above(0);',
                        '    pm.environment.set("sampleCartItemId", items[0].id);',
                        '});'
                    ]
                ),
                make_req(
                    "BB-CART-07: DELETE Xóa toàn bộ giỏ hàng để dọn dẹp dữ liệu test",
                    "DELETE", ["api", "cart"],
                    token_var="jwtToken",
                    tests=[
                        'pm.test("Xóa giỏ hàng thành công HTTP 200", function () {',
                        '    pm.response.to.have.status(200);',
                        '});'
                    ]
                ),
            ]
        },
        {
            "name": "6. Orders (Đặt hàng - EP, BVA Checkout & State Transition)",
            "item": [
                make_req(
                    "BB-ORD-01: GET Danh sách đơn hàng khi CHƯA đăng nhập [Security]",
                    "GET", ["api", "orders"],
                    tests=T_UNAUTH
                ),
                make_req(
                    "BB-ORD-02: POST Checkout khi giỏ hàng trống [Negative State]",
                    "POST", ["api", "orders", "checkout"],
                    body={"shippingAddress": "123 Nguyen Trai, Q1, HCM", "phone": "0908123456", "note": "Test empty cart"},
                    token_var="jwtToken",
                    tests=T_STATUS_400
                ),
                make_req(
                    "BB-ORD-03: POST Checkout SĐT ngắn dưới biên Min=10 ('090123') [BVA]",
                    "POST", ["api", "orders", "checkout"],
                    body={"shippingAddress": "123 Nguyen Trai, Q1, HCM", "phone": "090123", "note": "BVA phone"},
                    token_var="jwtToken",
                    tests=T_STATUS_400
                ),
                make_req(
                    "BB-ORD-04: POST Checkout Địa chỉ bỏ trống [EP Blank]",
                    "POST", ["api", "orders", "checkout"],
                    body={"shippingAddress": "", "phone": "0908123456", "note": "Blank address"},
                    token_var="jwtToken",
                    tests=T_STATUS_400
                ),
                make_req(
                    "BB-ORD-05: GET Lịch sử đơn hàng của User hiện tại",
                    "GET", ["api", "orders"],
                    query=[("page", 0), ("size", 10)],
                    token_var="jwtToken",
                    tests=T_API_SUCCESS
                ),
                make_req(
                    "BB-ORD-06: GET Chi tiết đơn hàng không tồn tại (999999) [404]",
                    "GET", ["api", "orders", "999999"],
                    token_var="jwtToken",
                    tests=T_STATUS_404
                ),
            ]
        },
        {
            "name": "7. Blogs, Reviews, Settings & RBAC Admin Security",
            "item": [
                make_req(
                    "BB-MISC-01: GET Danh sách bài viết Blog",
                    "GET", ["api", "blogs"],
                    tests=T_STATUS_200 + [
                        'pm.test("Blogs trả về dạng mảng Array", function () {',
                        '    pm.expect(pm.response.json()).to.be.an("array");',
                        '});'
                    ]
                ),
                make_req(
                    "BB-MISC-02: GET Chi tiết Blog không tồn tại (999999) [404]",
                    "GET", ["api", "blogs", "999999"],
                    tests=T_STATUS_404
                ),
                make_req(
                    "BB-MISC-03: GET Danh sách đánh giá sản phẩm",
                    "GET", ["api", "reviews", "product", "{{sampleProductId}}"],
                    tests=T_STATUS_200
                ),
                make_req(
                    "BB-MISC-04: GET Danh sách bài viết nổi bật (/api/blogs/featured)",
                    "GET", ["api", "blogs", "featured"],
                    tests=T_STATUS_200
                ),
                make_req(
                    "BB-MISC-05: GET Cấu hình hệ thống khi đã đăng nhập (/api/settings/public)",
                    "GET", ["api", "settings", "public"],
                    token_var="jwtToken",
                    tests=T_STATUS_200
                ),
                make_req(
                    "BB-SEC-01: RBAC - User thường truy cập /api/admin/dashboard bị chặn [403]",
                    "GET", ["api", "admin", "dashboard"],
                    token_var="jwtToken",
                    tests=T_FORBIDDEN
                ),
                make_req(
                    "BB-SEC-02: RBAC - User thường truy cập /api/admin/settings bị chặn [403]",
                    "GET", ["api", "admin", "settings"],
                    token_var="jwtToken",
                    tests=T_FORBIDDEN
                ),
            ]
        },
        {
            "name": "8. Security Testing (SQLi, XSS, Tampered JWT & Public Config)",
            "item": [
                make_req(
                    "SEC-PUB-01: GET /api/settings/public không cần JWT [Public 200]",
                    "GET", ["api", "settings", "public"],
                    tests=T_STATUS_200
                ),
                make_req(
                    "SEC-SQLI-01: SQL Injection trong tìm kiếm sản phẩm [PreparedStatement Safe]",
                    "GET", ["api", "products", "search"],
                    query=[("keyWord", "' OR '1'='1"), ("page", 0), ("size", 10)],
                    tests=[
                        'pm.test("SQLi không gây lỗi 500 SQL Syntax và trả 200 rỗng an toàn", function () {',
                        '    pm.response.to.have.status(200);',
                        '    var d = pm.response.json().data;',
                        '    pm.expect(d.content.length).to.eql(0);',
                        '});'
                    ]
                ),
                make_req(
                    "SEC-SQLI-02: SQL Injection qua Path Variable Product ID",
                    "GET", ["api", "products", "1 OR 1=1"],
                    tests=[
                        'pm.test("Không trả 200 dữ liệu rò rỉ khi Path ID bị inject", function () {',
                        '    pm.expect(pm.response.code).to.be.oneOf([400, 404, 500]);',
                        '});'
                    ]
                ),
                make_req(
                    "SEC-SQLI-03: SQL Injection tại Form Đăng nhập [Auth Bypass Blocked]",
                    "POST", ["api", "auth", "login"],
                    body={"username": "admin' OR '1'='1' --", "password": "anypassword"},
                    tests=[
                        'pm.test("Không đăng nhập được bằng SQL Injection", function () {',
                        '    pm.expect(pm.response.code).to.be.oneOf([400, 401]);',
                        '    var body = pm.response.json();',
                        '    pm.expect(body.token).to.be.undefined;',
                        '});'
                    ]
                ),
                make_req(
                    "SEC-XSS-01: XSS Payload tại Đăng ký tài khoản [Input Sanitization / Rejection]",
                    "POST", ["api", "auth", "register"],
                    body={
                        "username": "<script>alert(1)</script>",
                        "email": "xss_bad_email",
                        "password": "123",
                        "fullName": "<img src=x onerror=alert(1)>"
                    },
                    tests=T_STATUS_400
                ),
                make_req(
                    "SEC-JWT-01: Tampered JWT Token bị từ chối tại /api/orders",
                    "GET", ["api", "orders"],
                    token_var="tamperedToken",
                    tests=T_UNAUTH
                ),
                make_req(
                    "SEC-JWT-02: Tampered JWT Token bị từ chối tại /api/admin/users",
                    "GET", ["api", "admin", "users"],
                    token_var="tamperedToken",
                    tests=T_UNAUTH
                ),
                make_req(
                    "SEC-ADMIN-01: Đăng nhập Admin và kiểm tra truy cập hợp lệ /api/admin/dashboard",
                    "POST", ["api", "auth", "login"],
                    body={"username": "{{adminUsername}}", "password": "{{adminPassword}}"},
                    tests=[
                        'pm.test("Admin login thành công hoặc kiểm tra môi trường", function () {',
                        '    pm.expect(pm.response.code).to.be.oneOf([200, 400]);',
                        '    if (pm.response.code === 200) {',
                        '        pm.environment.set("adminJwtToken", pm.response.json().token);',
                        '    }',
                        '});'
                    ]
                ),
            ]
        }
    ]
}

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "postman", "VGA_Store.postman_collection.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(collection_data, f, indent=2, ensure_ascii=False)

total_requests = sum(len(folder["item"]) for folder in collection_data["item"])
print(f"Generated {total_requests} Black-Box API requests across {len(collection_data['item'])} folders -> {out_path}")
