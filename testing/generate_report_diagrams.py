import csv
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Segoe UI']
plt.rcParams['axes.edgecolor'] = '#334155'

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "testing" / "diagrams"
OUT.mkdir(parents=True, exist_ok=True)


def draw_box(ax, x, y, w, h, title, body="", fc="#EFF6FF", ec="#1D4ED8", title_fc="#1E3A8A", fs=8.5, bold_title=True):
    box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04", facecolor=fc, edgecolor=ec, linewidth=1.4)
    ax.add_patch(box)
    if body:
        nlines = title.count("\n") + 1
        div_offset = 0.28 + 0.16 * nlines
        ax.text(x + w / 2, y + h - 0.13, title, ha='center', va='top', fontsize=fs + 0.3,
                fontweight='bold' if bold_title else 'normal', color=title_fc)
        ax.plot([x + 0.03, x + w - 0.03], [y + h - div_offset, y + h - div_offset], color=ec, linewidth=0.8, alpha=0.6)
        ax.text(x + w / 2, y + h - div_offset - 0.08, body, ha='center', va='top', fontsize=fs - 0.7, color='#1E293B', linespacing=1.3)
    else:
        ax.text(x + w / 2, y + h / 2, title, ha='center', va='center', fontsize=fs,
                fontweight='bold' if bold_title else 'normal', color=title_fc)


def arrow(ax, x1, y1, x2, y2, label="", color="#475569", style="-|>", ls="-"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=1.2, linestyle=ls))
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx, my + 0.08, label, fontsize=7.5, ha='center', va='bottom',
                color='#0F172A', bbox=dict(boxstyle='round,pad=0.12', facecolor='white', edgecolor='none', alpha=0.85))


def gen_architecture():
    fig, ax = plt.subplots(figsize=(11, 6.4), dpi=200)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6.4)
    ax.axis('off')
    ax.set_title("VGA Store - System & Docker Container Architecture", fontsize=13, fontweight='bold', color='#0F172A', pad=10)

    # Outer Docker Container Network box
    outer = FancyBboxPatch((0.2, 1.35), 10.6, 4.7, boxstyle="round,pad=0.05,rounding_size=0.08",
                           facecolor="#F8FAFC", edgecolor="#64748B", linewidth=1.4, linestyle="--")
    ax.add_patch(outer)
    ax.text(0.4, 5.88, "Docker Compose Bridge Network (vga_network)", fontsize=9.5, fontweight='bold', color='#334155')

    # Clients (put User Frontend on lower row so OAuth/Gemini arrows don't cross Admin box)
    draw_box(ax, 0.5, 4.1, 2.7, 1.45, "Admin Frontend (vga_admin)",
             "React 19 + Vite 8 + Recharts\nNginx Alpine (Port 5174)\nDashboard, CRUD VGA, Orders",
             fc="#E0E7FF", ec="#4338CA")
    draw_box(ax, 0.5, 2.0, 2.7, 1.45, "User Frontend (vga_user)",
             "React 19 + Vite 8 + Redux\nNginx Alpine (Port 5173)\nCatalog, Cart, Checkout, AI Chat",
             fc="#DBEAFE", ec="#2563EB")

    # Backend
    draw_box(ax, 4.2, 2.35, 3.0, 2.95, "Backend REST API (vga_backend)",
             "Java 17/21 + Spring Boot 3.3.4\nPort 8080\n- controler/ (12 REST Controllers)\n- security/ (Spring Security + JWT)\n- service/ (11 Business Services)\n- repository/ (Spring Data JPA)\n- utils/ (VNPay & MoMo HMAC)",
             fc="#DCFCE7", ec="#15803D", title_fc="#14532D", fs=8.3)

    # DB
    draw_box(ax, 8.1, 3.15, 2.4, 1.65, "Database (vga_db)",
             "PostgreSQL 17.7 Alpine\nPort 5433 -> 5432\n16 Relational Tables\nseed_vga.sql + create_tables.sql",
             fc="#FEF3C7", ec="#B45309", title_fc="#78350F")

    # External systems
    draw_box(ax, 0.6, 0.15, 2.3, 0.9, "Google OAuth 2.0", "Xác thực đăng nhập nhanh", fc="#F1F5F9", ec="#475569", fs=8)
    draw_box(ax, 3.2, 0.15, 2.3, 0.9, "Google Gemini 1.5 Flash", "Tư vấn build/chọn VGA AI", fc="#F1F5F9", ec="#475569", fs=8)
    draw_box(ax, 5.8, 0.15, 2.2, 0.9, "VNPay Sandbox", "HMAC-SHA512 Payment URL", fc="#F1F5F9", ec="#475569", fs=8)
    draw_box(ax, 8.3, 0.15, 2.2, 0.9, "MoMo Test Gateway", "HMAC-SHA256 IPN Callback", fc="#F1F5F9", ec="#475569", fs=8)

    arrow(ax, 3.22, 4.75, 4.18, 4.35, "HTTP/JSON + JWT")
    arrow(ax, 3.22, 2.75, 4.18, 3.25, "HTTP/JSON + JWT")
    arrow(ax, 7.22, 4.0, 8.08, 4.0, "JDBC / JPA")
    arrow(ax, 1.45, 1.98, 1.45, 1.08, "OAuth Token", ls="--")
    arrow(ax, 2.45, 1.98, 4.15, 1.08, "SDK Prompt", ls="--")
    arrow(ax, 5.8, 2.33, 6.7, 1.08, "Pay URL / IPN", ls="--")
    arrow(ax, 6.4, 2.33, 9.2, 1.08, "QR Pay / Callback", ls="--")

    fig.tight_layout()
    fig.savefig(OUT / "fig_04_architecture.png", dpi=200)
    plt.close(fig)


def gen_use_case():
    fig, ax = plt.subplots(figsize=(10.5, 6.5), dpi=200)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 6.5)
    ax.axis('off')
    ax.set_title("VGA Store - System Use Case Diagram", fontsize=13, fontweight='bold', color='#0F172A', pad=8)

    sys_box = FancyBboxPatch((2.1, 0.3), 6.2, 5.8, boxstyle="round,pad=0.05,rounding_size=0.06",
                             facecolor="#F8FAFC", edgecolor="#1E40AF", linewidth=1.6)
    ax.add_patch(sys_box)
    ax.text(5.2, 5.92, "<<system>> VGA Store E-Commerce System", ha='center', fontsize=10, fontweight='bold', color='#1E3A8A')

    ucs = [
        (3.8, 5.3, "UC-01: Browse, Search & Filter VGA"),
        (3.8, 4.7, "UC-02: Compare Specs & AI Advisor Chat"),
        (3.8, 4.1, "UC-03: Register / Login / Google OAuth"),
        (3.8, 3.5, "UC-04: Manage Shopping Cart"),
        (3.8, 2.9, "UC-05: Checkout & VNPay/MoMo Payment"),
        (3.8, 2.3, "UC-06: Track, Cancel Order & Review Product"),
        (6.6, 4.3, "UC-07: Dashboard Analytics & Pin to Top"),
        (6.6, 3.5, "UC-08: CRUD Products, Categories & Brands"),
        (6.6, 2.7, "UC-09: Update Order & Payment Status"),
        (6.6, 1.9, "UC-10: Manage Users, Blogs & System Settings"),
    ]
    for cx, cy, label in ucs:
        el = patches.Ellipse((cx, cy), width=2.65, height=0.46, facecolor="#EFF6FF", edgecolor="#2563EB", lw=1.2)
        ax.add_patch(el)
        ax.text(cx, cy, label, ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1E293B')

    # Actors
    for ax_x, ax_y, aname in [(0.9, 4.8, "Guest\n(Khách vãng lai)"), (0.9, 2.7, "Customer\n(Khách hàng)"), (9.4, 3.1, "Admin / Staff\n(Quản trị viên)")]:
        draw_box(ax, ax_x - 0.7, ax_y - 0.4, 1.4, 0.8, aname, fc="#FEF3C7", ec="#D97706", title_fc="#78350F", fs=8.2)

    for cy in [5.3, 4.7, 4.1]:
        ax.plot([1.62, 2.47], [4.8, cy], color='#475569', lw=1.1)
    for cy in [5.3, 4.7, 4.1, 3.5, 2.9, 2.3]:
        ax.plot([1.62, 2.47], [2.7, cy], color='#1D4ED8', lw=1.1)
    for cy in [4.3, 3.5, 2.7, 1.9]:
        ax.plot([8.7, 7.93], [3.1, cy], color='#B91C1C', lw=1.1)
    # Generalization Customer -> Guest
    arrow(ax, 0.9, 3.12, 0.9, 4.38, "<<extends>>", color="#64748B", ls="--")

    fig.tight_layout()
    fig.savefig(OUT / "fig_01_use_case.png", dpi=200)
    plt.close(fig)


def gen_screen_flow():
    fig, ax = plt.subplots(figsize=(11, 5.6), dpi=200)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5.6)
    ax.axis('off')
    ax.set_title("VGA Store - User & Admin Portal Screen Flow", fontsize=13, fontweight='bold', color='#0F172A', pad=8)

    draw_box(ax, 0.3, 3.4, 1.8, 1.3, "Home (/)", "Banner, Series GPU,\nFeatured VGAs, AI Chat", fc="#DBEAFE", ec="#2563EB")
    draw_box(ax, 2.6, 4.0, 1.9, 1.1, "Shop (/products)", "Search, Brand Filter,\nPrice Range, Compare", fc="#DBEAFE", ec="#2563EB")
    draw_box(ax, 2.6, 2.5, 1.9, 1.1, "ProductDetail\n(/product/:id)", "Specs, Stock, Gallery,\nReviews, Add to Cart", fc="#DBEAFE", ec="#2563EB")
    draw_box(ax, 5.0, 4.0, 1.7, 1.1, "Cart (/cart)", "Update Qty, Remove,\nTotal Calc, BVA", fc="#DCFCE7", ec="#15803D")
    draw_box(ax, 7.2, 4.0, 1.8, 1.1, "Checkout (/checkout)", "Address, Phone, Payment\nCOD / VNPay / MoMo", fc="#DCFCE7", ec="#15803D")
    draw_box(ax, 7.2, 2.5, 1.8, 1.1, "PaymentPending\n(/payment/pending)", "QR / Gateway Callback\nStatus Poll", fc="#DCFCE7", ec="#15803D")
    draw_box(ax, 5.0, 2.5, 1.7, 1.1, "Profile & Orders\n(/profile, /track-order)", "Info, Change PW,\nAddress Book, History", fc="#FEF3C7", ec="#B45309")

    # Admin flow row
    draw_box(ax, 0.3, 0.5, 2.0, 1.1, "Admin Login\n(/login :5174)", "JWT ROLE_ADMIN Guard", fc="#FCE7F3", ec="#BE185D")
    draw_box(ax, 2.8, 0.5, 2.2, 1.1, "Admin Dashboard (/)", "KPI Revenue, Today Orders,\nLow Stock, Sales Charts", fc="#FCE7F3", ec="#BE185D")
    draw_box(ax, 5.5, 0.5, 2.5, 1.1, "Catalog & Content", "Products, Brands, Categories,\nBlogs, Reviews, Pin to Top", fc="#FCE7F3", ec="#BE185D")
    draw_box(ax, 8.4, 0.5, 2.3, 1.1, "Orders, Users & Settings", "Order Status Workflow,\nUser Lock/Role, Bank Config", fc="#FCE7F3", ec="#BE185D")

    arrow(ax, 2.12, 4.3, 2.58, 4.5)
    arrow(ax, 2.12, 3.7, 2.58, 3.1)
    arrow(ax, 3.55, 3.98, 3.55, 3.62)
    arrow(ax, 4.52, 4.5, 4.98, 4.5)
    arrow(ax, 6.72, 4.5, 7.18, 4.5)
    arrow(ax, 8.1, 3.98, 8.1, 3.62)
    arrow(ax, 7.18, 3.0, 6.72, 3.0)
    arrow(ax, 2.32, 1.05, 2.78, 1.05)
    arrow(ax, 5.02, 1.05, 5.48, 1.05)
    arrow(ax, 8.02, 1.05, 8.38, 1.05)

    fig.tight_layout()
    fig.savefig(OUT / "fig_02_screen_flow.png", dpi=200)
    plt.close(fig)


def gen_erd():
    fig, ax = plt.subplots(figsize=(11.5, 6.8), dpi=200)
    ax.set_xlim(0, 11.5)
    ax.set_ylim(0, 6.8)
    ax.axis('off')
    ax.set_title("VGA Store - Entity Relationship Diagram (PostgreSQL 17 Schema)", fontsize=13, fontweight='bold', color='#0F172A', pad=8)

    tables = [
        (0.3, 4.2, 2.3, 2.2, "users", "PK id (bigint)\nusername (unique)\nemail (unique)\npassword (BCrypt)\nfull_name, phone, role\nstatus, deleted"),
        (0.3, 2.0, 2.3, 1.5, "user_addresses", "PK id (bigint)\nFK user_id -> users.id\nrecipient_name, phone\ndetailed_address, is_default"),
        (3.2, 4.6, 2.4, 1.8, "carts & cart_items", "carts: id, FK user_id\ntotal_amount\ncart_items: id, FK cart_id\nFK product_id, quantity"),
        (3.2, 2.2, 2.4, 1.9, "orders", "PK id, order_code (UQ)\nFK user_id -> users.id\nstatus, payment_status\ntotal_amount, shipping_address\nconfirmed_at, shipped_at"),
        (3.2, 0.3, 2.4, 1.4, "order_items", "PK id\nFK order_id -> orders.id\nFK product_id -> products.id\nprice, quantity"),
        (6.2, 2.5, 2.5, 1.7, "payments", "PK id, transaction_code\nFK order_id -> orders.id\npayment_method, amount\npayment_status, paid_at"),
        (6.2, 4.7, 2.5, 1.8, "products", "PK id, name, sku (UQ)\nFK brand_id, FK category_id\nprice, old_price, stock\ngpu_model, vram, deleted"),
        (9.1, 4.9, 2.1, 1.4, "brands & categories", "brands: id, name, slug, logo\ncategories: id, name, active\ndisplay_order, deleted"),
        (9.1, 2.5, 2.1, 1.8, "reviews & blogs", "reviews: id, FK user_id,\nFK product_id, blog_id, rating\nblogs: id, title, author,\ncategory, featured, views"),
        (6.2, 0.3, 5.0, 1.5, "system_settings / service_policies / coupons",
         "system_settings (id, setting_key UQ, setting_value)   |   service_policies (id, title, content)\ncoupons (id, code UQ, discount_percent, valid_until)   |   warranties (serial_number UQ)"),
    ]
    for x, y, w, h, t, b in tables:
        draw_box(ax, x, y, w, h, t, b, fc="#F8FAFC", ec="#0F766E", title_fc="#134E4A", fs=8.0)

    arrow(ax, 1.45, 4.18, 1.45, 3.52, "1:N")
    arrow(ax, 2.62, 5.3, 3.18, 5.3, "1:1 / 1:N")
    arrow(ax, 2.62, 4.5, 3.18, 3.4, "1:N")
    arrow(ax, 4.4, 2.18, 4.4, 1.72, "1:N")
    arrow(ax, 5.62, 3.1, 6.18, 3.3, "1:N")
    arrow(ax, 5.62, 5.2, 6.18, 5.4, "N:1")
    arrow(ax, 5.62, 1.0, 6.4, 4.68, "N:1")
    arrow(ax, 8.72, 5.6, 9.08, 5.6, "N:1")
    arrow(ax, 8.72, 5.1, 9.08, 3.8, "1:N")

    fig.tight_layout()
    fig.savefig(OUT / "fig_03_erd.png", dpi=200)
    plt.close(fig)


def gen_sequence():
    fig, ax = plt.subplots(figsize=(10.8, 5.8), dpi=200)
    ax.set_xlim(0, 10.8)
    ax.set_ylim(0, 5.8)
    ax.axis('off')
    ax.set_title("Detailed Design Sequence Diagram - Checkout & Payment Workflow", fontsize=12.5, fontweight='bold', color='#0F172A', pad=8)

    actors = [(1.0, "Customer UI\n(React)"), (3.2, "OrderController\n& SecurityFilter"), (5.6, "OrderService\n& CartRepo"), (8.0, "PaymentService\n& VNPayUtils"), (9.7, "PostgreSQL\nDatabase")]
    for x, label in actors:
        draw_box(ax, x - 0.8, 5.0, 1.6, 0.55, label, fc="#DBEAFE", ec="#1D4ED8", fs=7.8)
        ax.plot([x, x], [0.3, 4.98], color="#94A3B8", linestyle="--", lw=1.1)

    msgs = [
        (4.5, 1.0, 3.2, "1. POST /api/orders/checkout (Bearer JWT)"),
        (4.0, 3.2, 5.6, "2. JwtAuthFilter validate -> createOrderFromCart(req)"),
        (3.5, 5.6, 9.7, "3. Load Cart, validate stock >= qty, decrement stock"),
        (3.0, 5.6, 9.7, "4. Save Order(PENDING/UNPAID) & Clear Cart"),
        (2.5, 3.2, 1.0, "5. 200 OK ApiResponse<OrderResponse(orderId)>"),
        (2.0, 1.0, 3.2, "6. POST /api/payments/orders/{orderId} (VNPAY/MOMO)"),
        (1.5, 3.2, 8.0, "7. PaymentService.createPayment() -> HMAC-SHA512 URL"),
        (1.0, 8.0, 9.7, "8. Persist Payment(PENDING, transactionCode)"),
        (0.55, 8.0, 1.0, "9. Return signed paymentUrl -> Redirect Gateway"),
    ]
    for y, x1, x2, txt in msgs:
        col = "#1E40AF" if x1 < x2 else "#0F766E"
        arrow(ax, x1, y, x2, y, txt, color=col, ls="-" if x1 < x2 else "--")

    fig.tight_layout()
    fig.savefig(OUT / "fig_05_sequence_checkout.png", dpi=200)
    plt.close(fig)


def gen_cfg():
    fig, ax = plt.subplots(figsize=(10.5, 5.4), dpi=200)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 5.4)
    ax.axis('off')
    ax.set_title("White-Box Control Flow Graph (CFG): AuthService.register() - V(G) = 4 Basic Paths", fontsize=12, fontweight='bold', color='#0F172A', pad=8)

    nodes = [
        (5.25, 4.8, "N1: Entry\nAuthService.register(req)", "#DCFCE7", "#15803D"),
        (5.25, 3.9, "D1: existsByUsername(username)?", "#FEF3C7", "#B45309"),
        (8.4, 3.9, "N2: Throw RuntimeException\n'Tên đăng nhập đã tồn tại'", "#FEE2E2", "#B91C1C"),
        (5.25, 2.9, "D2: existsByEmail(email)?", "#FEF3C7", "#B45309"),
        (8.4, 2.9, "N3: Throw RuntimeException\n'Email đã được sử dụng'", "#FEE2E2", "#B91C1C"),
        (5.25, 1.9, "D3: fullName != null &&\n!fullName.isEmpty()?", "#FEF3C7", "#B45309"),
        (2.4, 1.1, "N4: setFullName(req.fullName)", "#DBEAFE", "#1D4ED8"),
        (8.0, 1.1, "N5: setFullName(req.username)", "#DBEAFE", "#1D4ED8"),
        (5.25, 0.35, "N6: encode BCrypt, save User, return JWT", "#DCFCE7", "#15803D"),
    ]
    for cx, cy, txt, fc, ec in nodes:
        draw_box(ax, cx - 1.45, cy - 0.28, 2.9, 0.56, txt, fc=fc, ec=ec, title_fc="#0F172A", fs=7.8)

    arrow(ax, 5.25, 4.5, 5.25, 4.2)
    arrow(ax, 6.72, 3.9, 6.93, 3.9, "True")
    arrow(ax, 5.25, 3.6, 5.25, 3.2, "False")
    arrow(ax, 6.72, 2.9, 6.93, 2.9, "True")
    arrow(ax, 5.25, 2.6, 5.25, 2.2, "False")
    arrow(ax, 4.1, 1.75, 2.7, 1.4, "True")
    arrow(ax, 6.4, 1.75, 7.7, 1.4, "False")
    arrow(ax, 2.7, 0.8, 4.1, 0.55)
    arrow(ax, 7.7, 0.8, 6.4, 0.55)

    fig.tight_layout()
    fig.savefig(OUT / "fig_06_cfg_whitebox.png", dpi=200)
    plt.close(fig)


def gen_state_transition():
    fig, ax = plt.subplots(figsize=(10.5, 4.6), dpi=200)
    ax.set_xlim(0, 10.5)
    ax.set_ylim(0, 4.6)
    ax.axis('off')
    ax.set_title("State Transition Diagram: Order Lifecycle (OrderService & PaymentExpiryScheduler)", fontsize=12, fontweight='bold', color='#0F172A', pad=8)

    states = [
        (0.5, 2.5, 1.8, 0.8, "PENDING\n(Chờ xử lý)", "#FEF3C7", "#D97706"),
        (3.1, 2.5, 1.8, 0.8, "CONFIRMED\n(Đã xác nhận)", "#DBEAFE", "#2563EB"),
        (5.7, 2.5, 1.8, 0.8, "SHIPPING\n(Đang giao)", "#E0E7FF", "#4F46E5"),
        (8.3, 2.5, 1.8, 0.8, "DELIVERED\n(Hoàn thành)", "#DCFCE7", "#15803D"),
        (2.8, 0.5, 2.2, 0.8, "CANCEL_REQUESTED\n(Yêu cầu hủy)", "#FFEDD5", "#C2410C"),
        (6.4, 0.5, 2.2, 0.8, "CANCELLED\n(Đã hủy & Hoàn kho)", "#FEE2E2", "#B91C1C"),
    ]
    for x, y, w, h, t, fc, ec in states:
        draw_box(ax, x, y, w, h, t, fc=fc, ec=ec, title_fc="#0F172A", fs=8.3)

    arrow(ax, 2.32, 2.9, 3.08, 2.9, "VNPay/MoMo OK\nhoặc Admin duyệt")
    arrow(ax, 4.92, 2.9, 5.68, 2.9, "Xuất kho")
    arrow(ax, 7.52, 2.9, 8.28, 2.9, "Khách nhận")
    arrow(ax, 1.4, 2.48, 3.2, 1.32, "User hủy (PENDING)")
    arrow(ax, 4.0, 2.48, 4.0, 1.32, "")
    ax.text(3.35, 1.78, "User hủy (CONFIRMED)", fontsize=7.5, ha='center', color='#0F172A',
            bbox=dict(boxstyle='round,pad=0.12', facecolor='white', edgecolor='none', alpha=0.9))
    arrow(ax, 5.02, 0.9, 6.38, 0.9, "Admin duyệt hủy")
    arrow(ax, 2.1, 2.48, 6.6, 1.32, "", ls="--", color="#B91C1C")
    ax.text(5.45, 1.88, "Scheduler >15m Unpaid Bank", fontsize=7.5, ha='center', color='#991B1B',
            bbox=dict(boxstyle='round,pad=0.12', facecolor='white', edgecolor='none', alpha=0.95))
    arrow(ax, 9.0, 2.48, 8.1, 1.32, "BUG-05: Thiếu guard\nchặn DELIVERED->CANCELLED!", ls=":", color="#DC2626")

    fig.tight_layout()
    fig.savefig(OUT / "fig_07_state_transition.png", dpi=200)
    plt.close(fig)


def gen_unit_test_report_img():
    # Generate UNIT TEST REPORT card inspired by sample report (p.317-318) using real Maven & Vitest counts
    rows = [
        ("1", "AuthService (login, register, googleLogin)", "11", "0", "0", "5", "4", "2", "11"),
        ("2", "CartService (getMyCart, add, update, remove, clear)", "7", "0", "0", "2", "3", "2", "7"),
        ("3", "OrderService (place, createFromCart, cancel, status)", "7", "0", "0", "3", "3", "1", "7"),
        ("4", "Product / Brand / Category Services", "8", "0", "0", "4", "3", "1", "8"),
        ("5", "AdminService (dashboard, charts, pin, CRUD)", "4", "0", "0", "2", "1", "1", "4"),
        ("6", "PaymentService & PaymentExpiryScheduler", "3", "0", "0", "2", "1", "0", "3"),
        ("7", "SystemSettingService & UserService", "3", "0", "0", "2", "1", "0", "3"),
        ("8", "JwtUtil & PaymentUtils (VNPay / MoMo HMAC)", "14", "0", "0", "6", "5", "3", "14"),
        ("9", "Controllers, Filters & GlobalExceptionHandler", "6", "0", "0", "3", "3", "0", "6"),
        ("10", "CategoryController & Boot Test (@SpringBootTest)", "1", "0", "0", "1", "0", "0", "1"),
        ("11", "Frontend User Redux & Admin Utils (Vitest)", "8", "0", "0", "4", "2", "2", "8"),
    ]
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=200)
    ax.axis('off')
    ax.set_title("UNIT TEST REPORT — VGA STORE (JUnit 5 + Mockito + Vitest)", fontsize=13, fontweight='bold', color='#000080', pad=10)

    meta = (
        "Project Name: VGA Store — E-Commerce System     |   Author / Lead: Tran Dinh Trong\n"
        "Advisor: Nguyen Van Chien                       |   Tools: JUnit 5, Mockito, JaCoCo 0.8.12, Vitest 4.1\n"
        "Result: 64 Backend JUnit + 8 Frontend Vitest = 72 Passed / 0 Failed | Bundle Line Coverage: 75.8%"
    )
    ax.text(0.01, 0.96, meta, transform=ax.transAxes, fontsize=8.5, va='top',
            bbox=dict(boxstyle='square,pad=0.5', facecolor='#F8FAFC', edgecolor='#334155', lw=1))

    cols = ["No", "Module / Test Suite", "Passed", "Failed", "Untested", "N", "A", "B", "Total"]
    table = ax.table(cellText=rows + [["", "Sub Total (All Unit Tests)", "72", "0", "0", "34", "26", "12", "72"]],
                     colLabels=cols, loc='center', cellLoc='center', bbox=[0.01, 0.03, 0.98, 0.72])
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    for (r, c), cell in table.get_celld().items():
        if r == 0 or r == len(rows) + 1:
            cell.set_facecolor('#000080')
            cell.set_text_props(color='white', fontweight='bold')
        elif r % 2 == 0:
            cell.set_facecolor('#F1F5F9')
        if c == 1 and 1 <= r <= len(rows):
            cell.set_text_props(ha='left')
    col_widths = [0.05, 0.43, 0.08, 0.08, 0.09, 0.06, 0.06, 0.06, 0.09]
    for idx, w in enumerate(col_widths):
        for r in range(len(rows) + 2):
            table[(r, idx)].set_width(w)

    fig.savefig(OUT / "fig_08_unit_test_report_table.png", dpi=200, bbox_inches='tight')
    plt.close(fig)


def gen_metrics_charts():
    # Read real JaCoCo CSV & performance_results.json if present
    jacoco_csv = ROOT / "backend" / "vgashop" / "target" / "site" / "jacoco" / "jacoco.csv"
    perf_json = ROOT / "testing" / "performance_results.json"

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.6), dpi=200)

    if jacoco_csv.exists():
        rows = list(csv.DictReader(open(jacoco_csv, encoding='utf-8')))
        targets = []
        for r in rows:
            pkg = r['PACKAGE'].split('.')[-1]
            if pkg == 'service' or r['CLASS'] in ['JwtUtil', 'SecurityConfig', 'VNPayUtils', 'MomoUtils', 'GlobalExceptionHandler']:
                lc, lm = int(r['LINE_COVERED']), int(r['LINE_MISSED'])
                pct = lc * 100.0 / max(lc + lm, 1)
                targets.append((r['CLASS'], pct))
        targets.sort(key=lambda x: x[1])
        names = [x[0] for x in targets]
        vals = [x[1] for x in targets]
        colors = ['#16A34A' if v >= 90 else ('#2563EB' if v >= 70 else '#DC2626') for v in vals]
        ax1.barh(names, vals, color=colors)
        ax1.axvline(70, color='#DC2626', linestyle='--', linewidth=1.2, label='Exit Criterion (70%)')
        ax1.set_xlim(0, 108)
        ax1.set_xlabel("Line Coverage (%)")
        ax1.set_title("JaCoCo Line Coverage by Core Class", fontsize=10.5, fontweight='bold')
        ax1.legend(loc='lower right', fontsize=8)
        for i, v in enumerate(vals):
            ax1.text(v + 1, i, f"{v:.1f}%", va='center', fontsize=7.5)

    if perf_json.exists():
        pdata = json.loads(perf_json.read_text(encoding='utf-8'))["scenarios"]
        labels = [s["scenario"].split(":")[0] for s in pdata]
        avgs = [s["avg_ms"] for s in pdata]
        p95s = [s["p95_ms"] for s in pdata]
        x = range(len(labels))
        w = 0.36
        ax2.bar([i - w / 2 for i in x], avgs, width=w, label="Avg (ms)", color="#2563EB")
        ax2.bar([i + w / 2 for i in x], p95s, width=w, label="P95 (ms)", color="#F59E0B")
        ax2.set_xticks(list(x))
        ax2.set_xticklabels(labels, rotation=20, fontsize=8)
        ax2.set_ylabel("Latency (ms)")
        ax2.set_title("Load & Performance Test (10-25 Concurrent VUs)", fontsize=10.5, fontweight='bold')
        ax2.legend(fontsize=8)
    else:
        ax2.text(0.5, 0.5, "Performance results pending", ha='center', va='center')

    fig.tight_layout()
    fig.savefig(OUT / "fig_09_coverage_and_perf_charts.png", dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    gen_use_case()
    gen_screen_flow()
    gen_erd()
    gen_architecture()
    gen_sequence()
    gen_cfg()
    gen_state_transition()
    gen_unit_test_report_img()
    gen_metrics_charts()
    print("Generated all diagrams in:", OUT)
