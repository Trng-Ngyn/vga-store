import json
import time
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

COLLECTION_PATH = r"C:\Users\TRONG\.gemini\antigravity-ide\scratch\vga-store\postman\VGA_Store.postman_collection.json"
ENV_PATH = r"C:\Users\TRONG\.gemini\antigravity-ide\scratch\vga-store\postman\VGA_Store.postman_environment.json"

def run_tests():
    print("=" * 70)
    print("  POSTMAN AUTOMATED TEST RUNNER - VGA STORE API")
    print("  Môn học: Kiểm chứng phần mềm (Software Testing & QA)")
    print("=" * 70)
    
    # 1. Load Collection & Environment
    with open(COLLECTION_PATH, "r", encoding="utf-8") as f:
        col = json.load(f)
    with open(ENV_PATH, "r", encoding="utf-8") as f:
        env = json.load(f)
        
    env_vars = {item["key"]: item["value"] for item in env.get("values", [])}
    base_url = env_vars.get("baseUrl", "http://localhost:8080")
    
    print(f"Target Base URL: {base_url}")
    print(f"Collection: {col['info']['name']}\n")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # We will test admin login first or register
    # Note: Default admin in DataSeeder is admin / 123
    test_cases = [
        {
            "name": "1. Đăng ký tài khoản người dùng mới (POST /api/auth/register)",
            "method": "POST",
            "url": f"{base_url}/api/auth/register",
            "headers": {"Content-Type": "application/json"},
            "json": {
                "username": "tester_" + str(int(time.time()))[-4:],
                "email": f"tester_{str(int(time.time()))[-4:]}@vga.local",
                "password": "password123",
                "fullName": "Sinh Vien Kiem Chung"
            },
            "assertions": [
                ("Status Code 200 hoặc 201", lambda r: r.status_code in [200, 201]),
                ("Response time < 1500ms", lambda r: r.elapsed.total_seconds() < 1.5)
            ]
        },
        {
            "name": "2. Đăng nhập hệ thống & Lấy JWT Token (POST /api/auth/login)",
            "method": "POST",
            "url": f"{base_url}/api/auth/login",
            "headers": {"Content-Type": "application/json"},
            "json": {
                "username": "admin",
                "password": "123"
            },
            "assertions": [
                ("Status Code 200 OK", lambda r: r.status_code == 200),
                ("Response có chứa thuộc tính 'token'", lambda r: "token" in r.json() and len(r.json()["token"]) > 20),
                ("Response time < 1000ms", lambda r: r.elapsed.total_seconds() < 1.0)
            ],
            "extract": lambda r, envs: envs.update({"jwtToken": r.json().get("token")})
        },
        {
            "name": "3. Lấy danh sách danh mục sản phẩm (GET /api/categories)",
            "method": "GET",
            "url": f"{base_url}/api/categories?page=0&size=10",
            "headers": {},
            "assertions": [
                ("Status Code 200 OK", lambda r: r.status_code == 200),
                ("Response trả về đúng cấu trúc ApiResponse (có trường 'data')", lambda r: "data" in r.json()),
                ("Response time < 1000ms", lambda r: r.elapsed.total_seconds() < 1.0)
            ]
        },
        {
            "name": "4. Lấy danh mục đang kích hoạt (GET /api/categories/active)",
            "method": "GET",
            "url": f"{base_url}/api/categories/active",
            "headers": {},
            "assertions": [
                ("Status Code 200 OK", lambda r: r.status_code == 200),
                ("Response time < 1000ms", lambda r: r.elapsed.total_seconds() < 1.0)
            ]
        },
        {
            "name": "5. Lấy danh sách sản phẩm VGA kèm phân trang (GET /api/products)",
            "method": "GET",
            "url": f"{base_url}/api/products?page=0&size=10&sortBy=id&direction=asc",
            "headers": {},
            "assertions": [
                ("Status Code 200 OK", lambda r: r.status_code == 200),
                ("Response có chứa danh sách sản phẩm", lambda r: "data" in r.json()),
                ("Response time < 1000ms", lambda r: r.elapsed.total_seconds() < 1.0)
            ]
        },
        {
            "name": "6. Tìm kiếm sản phẩm VGA theo từ khóa RTX (GET /api/products/search)",
            "method": "GET",
            "url": f"{base_url}/api/products/search?keyWord=RTX",
            "headers": {},
            "assertions": [
                ("Status Code 200 OK", lambda r: r.status_code == 200),
                ("Response time < 1000ms", lambda r: r.elapsed.total_seconds() < 1.0)
            ]
        },
        {
            "name": "7. Lấy danh sách thương hiệu VGA (GET /api/brands)",
            "method": "GET",
            "url": f"{base_url}/api/brands?page=0&size=10",
            "headers": {},
            "assertions": [
                ("Status Code 200 OK", lambda r: r.status_code == 200),
                ("Response trả về dữ liệu thương hiệu", lambda r: "data" in r.json()),
                ("Response time < 1000ms", lambda r: r.elapsed.total_seconds() < 1.0)
            ]
        },
        {
            "name": "8. Truy vấn giỏ hàng bảo mật với Bearer Token (GET /api/cart)",
            "method": "GET",
            "url": f"{base_url}/api/cart",
            "headers": lambda envs: {"Authorization": f"Bearer {envs.get('jwtToken', '')}"},
            "assertions": [
                ("Status Code 200 OK khi có Bearer Token", lambda r: r.status_code in [200, 204]),
                ("Response time < 1000ms", lambda r: r.elapsed.total_seconds() < 1.0)
            ]
        }
    ]
    
    start_time = time.time()
    
    for tc in test_cases:
        print("-" * 70)
        print(f"Request: {tc['name']}")
        
        headers = tc["headers"](env_vars) if callable(tc["headers"]) else tc["headers"]
        
        try:
            req_start = time.time()
            if tc["method"] == "POST":
                resp = requests.post(tc["url"], json=tc.get("json"), headers=headers, timeout=5)
            else:
                resp = requests.get(tc["url"], headers=headers, timeout=5)
            ms = int((time.time() - req_start) * 1000)
            
            print(f"  HTTP {resp.status_code} | {ms} ms | URL: {tc['url']}")
            
            if "extract" in tc:
                tc["extract"](resp, env_vars)
                print(f"  [Auto-Extract] Đã trích xuất và cập nhật JWT Token: {env_vars.get('jwtToken')[:25]}...")
                
            for desc, fn in tc["assertions"]:
                total_tests += 1
                try:
                    ok = fn(resp)
                    if ok:
                        passed_tests += 1
                        print(f"  [PASS] {desc}")
                    else:
                        failed_tests += 1
                        print(f"  [FAIL] {desc}")
                except Exception as ex:
                    failed_tests += 1
                    print(f"  [FAIL] {desc} (Lỗi: {ex})")
                    
        except Exception as e:
            print(f"  [ERROR] Không thể kết nối tới server: {e}")
            total_tests += len(tc["assertions"])
            failed_tests += len(tc["assertions"])
            
    total_elapsed = round(time.time() - start_time, 2)
    
    print("=" * 70)
    print("  TỔNG KẾT KẾT QUẢ KIỂM THỬ POSTMAN API")
    print("=" * 70)
    print(f"  Tổng số requests thực thi : {len(test_cases)}")
    print(f"  Tổng số assertions kiểm tra: {total_tests}")
    print(f"  Số assertions đạt (PASS)  : {passed_tests}")
    print(f"  Số assertions hỏng (FAIL) : {failed_tests}")
    print(f"  Tỉ lệ thành công (Pass rate): {round(passed_tests / total_tests * 100, 1)}%")
    print(f"  Tổng thời gian chạy test  : {total_elapsed} giây")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
