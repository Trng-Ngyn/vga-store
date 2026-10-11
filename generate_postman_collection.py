import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Postman Collection v2.1.0 definition
collection_data = {
    "info": {
        "_postman_id": "vga-store-software-testing-collection-2026",
        "name": "VGA Store - Kiểm Chứng Phần Mềm (API Test Suite)",
        "description": "Bộ API Collection kiểm thử tự động toàn diện cho dự án VGA Store môn Kiểm chứng phần mềm.\nBao gồm kiểm thử xác thực, danh mục, sản phẩm, thương hiệu và giỏ hàng.",
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
    },
    "item": [
        {
            "name": "1. Authentication",
            "item": [
                {
                    "name": "POST Đăng ký tài khoản mới",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Mã trạng thái phản hồi hợp lệ (200 hoặc 400 nếu đã tồn tại)\", function () {",
                                    "    pm.expect(pm.response.code).to.be.oneOf([200, 201, 400]);",
                                    "});",
                                    "",
                                    "pm.test(\"Thời gian phản hồi nhanh dưới 1500ms\", function () {",
                                    "    pm.expect(pm.response.responseTime).to.be.below(1500);",
                                    "});"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "username": "{{testUsername}}",
                                "email": "{{testEmail}}",
                                "password": "{{testPassword}}",
                                "fullName": "Kiểm Thử Viên"
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{baseUrl}}/api/auth/register",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "auth", "register"]
                        },
                        "description": "Gửi thông tin đăng ký tài khoản mới vào hệ thống."
                    }
                },
                {
                    "name": "POST Đăng nhập & Tự động lưu JWT Token",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Đăng nhập thành công trả về mã HTTP 200\", function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});",
                                    "",
                                    "var jsonData = pm.response.json();",
                                    "pm.test(\"Response có chứa JWT token\", function () {",
                                    "    pm.expect(jsonData).to.have.property('token');",
                                    "    pm.expect(jsonData.token).to.be.a('string');",
                                    "});",
                                    "",
                                    "// Tự động lưu Token vào biến môi trường để các request sau sử dụng",
                                    "if (jsonData.token) {",
                                    "    pm.environment.set(\"jwtToken\", jsonData.token);",
                                    "    console.log(\"Đã lưu JWT Token vào Environment thành công!\");",
                                    "}"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "POST",
                        "header": [
                            {"key": "Content-Type", "value": "application/json"}
                        ],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps({
                                "username": "{{testUsername}}",
                                "password": "{{testPassword}}"
                            }, indent=2)
                        },
                        "url": {
                            "raw": "{{baseUrl}}/api/auth/login",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "auth", "login"]
                        },
                        "description": "Xác thực tài khoản và tự động nạp Token vào biến môi trường jwtToken."
                    }
                }
            ]
        },
        {
            "name": "2. Categories (Danh mục sản phẩm)",
            "item": [
                {
                    "name": "GET Lấy tất cả danh mục",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Trạng thái HTTP 200 OK\", function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});",
                                    "",
                                    "var jsonData = pm.response.json();",
                                    "pm.test(\"Dữ liệu trả về đúng cấu trúc ApiResponse\", function () {",
                                    "    pm.expect(jsonData).to.have.property('data');",
                                    "    pm.expect(jsonData).to.have.property('message');",
                                    "});",
                                    "",
                                    "pm.test(\"Thời gian phản hồi dưới 1000ms\", function () {",
                                    "    pm.expect(pm.response.responseTime).to.be.below(1000);",
                                    "});"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}/api/categories?page=0&size=10",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "categories"],
                            "query": [
                                {"key": "page", "value": "0"},
                                {"key": "size", "value": "10"}
                            ]
                        },
                        "description": "Lấy danh sách các danh mục VGA kèm phân trang."
                    }
                },
                {
                    "name": "GET Lấy danh mục đang kích hoạt (Active)",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Trạng thái HTTP 200 OK\", function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}/api/categories/active",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "categories", "active"]
                        }
                    }
                }
            ]
        },
        {
            "name": "3. Products (Sản phẩm VGA)",
            "item": [
                {
                    "name": "GET Lấy danh sách sản phẩm VGA",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Trạng thái HTTP 200 OK\", function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});",
                                    "",
                                    "var jsonData = pm.response.json();",
                                    "pm.test(\"Dữ liệu sản phẩm trả về thành công\", function () {",
                                    "    pm.expect(jsonData).to.have.property('data');",
                                    "});"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}/api/products?page=0&size=10&sortBy=id&direction=asc",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "products"],
                            "query": [
                                {"key": "page", "value": "0"},
                                {"key": "size", "value": "10"},
                                {"key": "sortBy", "value": "id"},
                                {"key": "direction", "value": "asc"}
                            ]
                        }
                    }
                },
                {
                    "name": "GET Tìm kiếm sản phẩm theo tên (Search RTX)",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Trạng thái HTTP 200 OK\", function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}/api/products/search?keyWord=RTX",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "products", "search"],
                            "query": [
                                {"key": "keyWord", "value": "RTX"}
                            ]
                        }
                    }
                }
            ]
        },
        {
            "name": "4. Brands (Thương hiệu VGA)",
            "item": [
                {
                    "name": "GET Lấy danh sách thương hiệu",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Trạng thái HTTP 200 OK\", function () {",
                                    "    pm.response.to.have.status(200);",
                                    "});",
                                    "",
                                    "var jsonData = pm.response.json();",
                                    "pm.test(\"Danh sách thương hiệu trả về hợp lệ\", function () {",
                                    "    pm.expect(jsonData.data).to.be.an('object');",
                                    "});"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}/api/brands?page=0&size=10",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "brands"],
                            "query": [
                                {"key": "page", "value": "0"},
                                {"key": "size", "value": "10"}
                            ]
                        }
                    }
                }
            ]
        },
        {
            "name": "5. Cart (Giỏ hàng - Cần xác thực Bearer Token)",
            "item": [
                {
                    "name": "GET Lấy giỏ hàng người dùng hiện tại",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "exec": [
                                    "pm.test(\"Trạng thái phản hồi thành công hoặc yêu cầu auth\", function () {",
                                    "    pm.expect(pm.response.code).to.be.oneOf([200, 401, 403]);",
                                    "});"
                                ],
                                "type": "text/javascript"
                            }
                        }
                    ],
                    "request": {
                        "auth": {
                            "type": "bearer",
                            "bearer": [
                                {"key": "token", "value": "{{jwtToken}}", "type": "string"}
                            ]
                        },
                        "method": "GET",
                        "header": [],
                        "url": {
                            "raw": "{{baseUrl}}/api/cart",
                            "host": ["{{baseUrl}}"],
                            "path": ["api", "cart"]
                        }
                    }
                }
            ]
        }
    ]
}

# 2. Postman Environment definition
environment_data = {
    "id": "vga-store-local-environment-2026",
    "name": "VGA Store - Local Environment",
    "values": [
        {
            "key": "baseUrl",
            "value": "http://localhost:8080",
            "type": "default",
            "enabled": True
        },
        {
            "key": "jwtToken",
            "value": "",
            "type": "secret",
            "enabled": True
        },
        {
            "key": "testUsername",
            "value": "demotester",
            "type": "default",
            "enabled": True
        },
        {
            "key": "testEmail",
            "value": "demotester@vga.local",
            "type": "default",
            "enabled": True
        },
        {
            "key": "testPassword",
            "value": "123456",
            "type": "secret",
            "enabled": True
        }
    ],
    "_postman_variable_scope": "environment"
}

# 3. Save files to project directory
project_postman_dir = r"C:\Users\TRONG\.gemini\antigravity-ide\scratch\vga-store\postman"
os.makedirs(project_postman_dir, exist_ok=True)

col_path = os.path.join(project_postman_dir, "VGA_Store.postman_collection.json")
env_path = os.path.join(project_postman_dir, "VGA_Store.postman_environment.json")

with open(col_path, "w", encoding="utf-8") as f:
    json.dump(collection_data, f, ensure_ascii=False, indent=2)

with open(env_path, "w", encoding="utf-8") as f:
    json.dump(environment_data, f, ensure_ascii=False, indent=2)

# 4. Copy to Downloads folder for convenient import
downloads_dir = r"C:\Users\TRONG\Downloads"
shutil.copy2(col_path, os.path.join(downloads_dir, "VGA_Store.postman_collection.json"))
shutil.copy2(env_path, os.path.join(downloads_dir, "VGA_Store.postman_environment.json"))

print("Tạo thành công bộ Postman Collection & Environment!")
print(f"File 1: {col_path}")
print(f"File 2: {env_path}")
print(f"Đã sao chép vào Downloads: {downloads_dir}")
