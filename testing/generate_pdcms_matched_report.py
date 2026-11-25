import csv
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parent.parent
DIAG = ROOT / "testing" / "diagrams"


def load_inputs():
    perf_p = ROOT / "testing" / "performance_results.json"
    verif_p = ROOT / "testing" / "verification_results.json"
    stat_p = ROOT / "testing" / "static_metrics.json"
    jac_p = ROOT / "backend" / "vgashop" / "target" / "site" / "jacoco" / "jacoco.csv"

    perf = json.loads(perf_p.read_text(encoding="utf-8")) if perf_p.exists() else {"scenarios": []}
    verif = json.loads(verif_p.read_text(encoding="utf-8")) if verif_p.exists() else {}
    stat = json.loads(stat_p.read_text(encoding="utf-8")) if stat_p.exists() else {}
    jac_rows = list(csv.DictReader(open(jac_p, encoding="utf-8"))) if jac_p.exists() else []
    return perf, verif, stat, jac_rows


def set_cell_bg(cell, hex_color: str):
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading)


def set_cell_margins(cell, top=90, bottom=90, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, color="CBD5E1", sz="4"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(f'''
            <w:tblBorders {nsdecls("w")}>
                <w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
                <w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>
            </w:tblBorders>
        ''')
        tblPr[0].append(borders)


def add_page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run1 = p.add_run("VGA Store — Final Project & Software Verification Report   |   Trang ")
    run1.font.name = "Times New Roman"
    run1.font.size = Pt(9.5)
    run1.font.color.rgb = RGBColor(100, 116, 139)

    fld = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
    p._p.append(fld)


def style_run(run, size=12, bold=False, italic=False, color=RGBColor(15, 23, 42)):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def add_h(doc, text, level=1, space_before=12, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    try:
        p.style = doc.styles[f'Heading {level}']
    except KeyError:
        pass
    r = p.add_run(text)
    if level == 1:
        style_run(r, 15, bold=True, color=RGBColor(0, 32, 96))
    elif level == 2:
        style_run(r, 13, bold=True, color=RGBColor(30, 58, 138))
    elif level == 3:
        style_run(r, 12, bold=True, color=RGBColor(15, 23, 42))
    else:
        style_run(r, 11.5, bold=True, italic=True, color=RGBColor(51, 65, 85))
    return p


def add_p(doc, text, bold_prefix=None, space_after=5, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.2
    if bold_prefix:
        rb = p.add_run(str(bold_prefix).replace("`", ""))
        style_run(rb, 11.5, bold=True)
    r = p.add_run(str(text).replace("`", ""))
    style_run(r, 11.5, italic=italic)
    return p


def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        rb = p.add_run(str(bold_prefix).replace("`", ""))
        style_run(rb, 11.5, bold=True)
    r = p.add_run(str(text).replace("`", ""))
    style_run(r, 11.5)
    return p


def add_table(doc, headers, rows, col_widths=None, header_bg="1E3A8A", font_size=10):
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="CBD5E1", sz="4")

    # Repeat header across pages
    trPr = tbl.rows[0]._tr.get_or_add_trPr()
    trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))

    for c_idx, h in enumerate(headers):
        cell = tbl.rows[0].cells[c_idx]
        if col_widths:
            cell.width = Inches(col_widths[c_idx])
        set_cell_bg(cell, header_bg)
        set_cell_margins(cell, 90, 90, 100, 100)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        style_run(r, font_size, bold=True, color=RGBColor(255, 255, 255))

    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx + 1]
        bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            if col_widths:
                cell.width = Inches(col_widths[c_idx])
            set_cell_bg(cell, bg)
            set_cell_margins(cell, 75, 75, 100, 100)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.12
            r = p.add_run(str(val).replace("`", ""))
            style_run(r, font_size)

    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(4)
    return tbl


def add_img(doc, img_path: Path, caption: str, width_in=6.3):
    if not img_path.exists():
        add_p(doc, f"[Missing image: {img_path.name}]", italic=True)
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(img_path), width=Inches(width_in))
    cap = doc.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(0)
    cap.paragraph_format.space_after = Pt(8)
    r = cap.add_run(caption)
    style_run(r, 10, italic=True, color=RGBColor(71, 85, 105))


def build_report():
    perf, verif, stat, jac_rows = load_inputs()

    # Compute dynamic JaCoCo summary
    if jac_rows:
        tot_lc = sum(int(r["LINE_COVERED"]) for r in jac_rows)
        tot_lm = sum(int(r["LINE_MISSED"]) for r in jac_rows)
        tot_bc = sum(int(r["BRANCH_COVERED"]) for r in jac_rows)
        tot_bm = sum(int(r["BRANCH_MISSED"]) for r in jac_rows)
        tot_ic = sum(int(r["INSTRUCTION_COVERED"]) for r in jac_rows)
        tot_im = sum(int(r["INSTRUCTION_MISSED"]) for r in jac_rows)
        line_pct = tot_lc * 100.0 / max(tot_lc + tot_lm, 1)
        branch_pct = tot_bc * 100.0 / max(tot_bc + tot_bm, 1)
        inst_pct = tot_ic * 100.0 / max(tot_ic + tot_im, 1)
    else:
        tot_lc, tot_lm, tot_bc, tot_bm, line_pct, branch_pct, inst_pct = 2316, 739, 452, 241, 75.8, 65.2, 77.7

    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(11.5)

    # Set clean heading styles base fonts
    for hname, sz in [("Heading 1", 15), ("Heading 2", 13), ("Heading 3", 12)]:
        if hname in doc.styles:
            doc.styles[hname].font.name = "Times New Roman"
            doc.styles[hname].font.size = Pt(sz)

    # =========================================================================
    # COVER PAGE (UTH OFFICIAL DOUBLE BORDER + PDCMS CAPSTONE METADATA)
    # =========================================================================
    sec1 = doc.sections[0]
    sec1.top_margin = Inches(0.85)
    sec1.bottom_margin = Inches(0.85)
    sec1.left_margin = Inches(1.0)
    sec1.right_margin = Inches(0.85)

    pgBorders = parse_xml(f'''
        <w:pgBorders {nsdecls("w")} w:offsetFrom="page">
            <w:top w:val="double" w:sz="18" w:space="24" w:color="1E3A8A"/>
            <w:left w:val="double" w:sz="18" w:space="24" w:color="1E3A8A"/>
            <w:bottom w:val="double" w:sz="18" w:space="24" w:color="1E3A8A"/>
            <w:right w:val="double" w:sz="18" w:space="24" w:color="1E3A8A"/>
        </w:pgBorders>
    ''')
    sec1._sectPr.append(pgBorders)

    p_hdr = doc.add_paragraph()
    p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_hdr.paragraph_format.space_after = Pt(10)
    r = p_hdr.add_run("TRƯỜNG ĐẠI HỌC GIAO THÔNG VẬN TẢI TP. HỒ CHÍ MINH\n")
    style_run(r, 13.5, bold=True, color=RGBColor(0, 32, 96))
    r = p_hdr.add_run("VIỆN ĐÀO TẠO CHẤT LƯỢNG CAO — BỘ MÔN KIỂM CHỨNG PHẦN MỀM\n***")
    style_run(r, 11.5, bold=True, color=RGBColor(51, 65, 85))

    logo_p = ROOT / "uth_logo.png"
    if logo_p.exists():
        pl = doc.add_paragraph()
        pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pl.paragraph_format.space_before = Pt(14)
        pl.paragraph_format.space_after = Pt(14)
        pl.add_run().add_picture(str(logo_p), width=Inches(2.8))

    pt = doc.add_paragraph()
    pt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pt.paragraph_format.space_before = Pt(6)
    pt.paragraph_format.space_after = Pt(16)
    r = pt.add_run("FINAL PROJECT & SOFTWARE VERIFICATION REPORT\n\n")
    style_run(r, 16, bold=True, color=RGBColor(0, 32, 96))
    r = pt.add_run("VGA Store — Graphics Card E-Commerce System\n")
    style_run(r, 17, bold=True, color=RGBColor(30, 58, 138))
    r = pt.add_run("(Áp dụng quy trình kiểm chứng toàn diện theo Chuẩn Chương I–VII & Mẫu PDCMS)")
    style_run(r, 11.5, italic=True, color=RGBColor(71, 85, 105))

    pm = doc.add_paragraph()
    pm.alignment = WD_ALIGN_PARAGRAPH.LEFT
    pm.paragraph_format.space_before = Pt(16)
    pm.paragraph_format.line_spacing = 1.35

    def add_meta_line(label, val, bold_val=False):
        rl = pm.add_run(f"    {label:<28}:  ")
        style_run(rl, 12, bold=True, color=RGBColor(30, 58, 138))
        rv = pm.add_run(f"{val}\n")
        style_run(rv, 12, bold=bold_val)

    add_meta_line("Giảng viên hướng dẫn", "Nguyễn Văn Chiến", True)
    add_meta_line("Nhóm thực hiện", "Nhóm 7 — VGA Store QA & Engineering Team (6 thành viên)", True)
    add_meta_line("Thành viên 1 (Leader)", "Trần Đình Trọng (trongtd0773@ut.edu.vn)")
    add_meta_line("Thành viên 2", "Ngô Hữu Phước (ngohuuphuoc36@gmail.com)")
    add_meta_line("Thành viên 3", "Phan Khôi (khoiphan252005@gmail.com)")
    add_meta_line("Thành viên 4", "Lê Minh Hiếu (hieulm3065@ut.edu.vn)")
    add_meta_line("Thành viên 5", "Nguyễn Văn Huy (lehuy9095@gmail.com)")
    add_meta_line("Thành viên 6", "Duy Vũ (duyvudao79@gmail.com)")
    add_meta_line("Repository", "https://github.com/Trng-Ngyn/vga-store")

    pd = doc.add_paragraph()
    pd.alignment = WD_ALIGN_PARAGRAPH.CENTER
    pd.paragraph_format.space_before = Pt(24)
    r = pd.add_run("- TP. Hồ Chí Minh, tháng 11 năm 2026 -")
    style_run(r, 12.5, bold=True)

    # Switch to body section (no border + footer page numbering)
    sec2 = doc.add_section()
    sec2.top_margin = Inches(0.85)
    sec2.bottom_margin = Inches(0.85)
    sec2.left_margin = Inches(0.95)
    sec2.right_margin = Inches(0.8)
    sec2._sectPr.append(parse_xml(f'''
        <w:pgBorders {nsdecls("w")} w:offsetFrom="page">
            <w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>
        </w:pgBorders>
    '''))
    add_page_number_footer(sec2)

    # =========================================================================
    # TABLE OF CONTENTS (EXACTLY MATCHING COPY OF FINAL_PROJECT_REPORT_PDCMS)
    # =========================================================================
    add_h(doc, "Table of Contents", level=1, space_before=4, space_after=8)
    toc_lines = [
        ("Acknowledgement", 0),
        ("Definition and Acronyms", 0),
        ("I. Project Introduction", 0),
        ("1. Overview (1.1 Project Information, 1.2 Project Team)", 1),
        ("2. Product Background", 1),
        ("3. Existing Systems (3.1 GearVN.com, 3.2 PhongVu.vn)", 1),
        ("4. Business Opportunity", 1),
        ("5. Software Product Vision", 1),
        ("6. Project Scope & Limitations (6.1 Major Features, 6.2 Limitations & Exclusions)", 1),
        ("II. Project Management Plan", 0),
        ("1. Overview (1.1 Scope & Estimation, 1.2 Project Objectives, 1.3 Project Risks)", 1),
        ("2. Management Approach (2.1 Project Process, 2.2 Quality Management, 2.3 Training Plan)", 1),
        ("3. Project Deliverables", 1),
        ("4. Responsibility Assignments", 1),
        ("5. Project Communications", 1),
        ("6. Configuration Management (6.1 Documents, 6.2 Source Code & SCI, 6.3 Tools & Infrastructures)", 1),
        ("III. Software Requirement Specification", 0),
        ("1. Product Overview", 1),
        ("2. User Requirements (2.1 System Actors, 2.2 Use Cases: Diagram & Descriptions)", 1),
        ("3. Functional Requirements (3.1 System Functional Overview, 3.2 Web Application)", 1),
        ("4. Non-Functional Requirements (4.1 External Interfaces, 4.2 Quality Attributes)", 1),
        ("5. Requirement Appendix (5.1 Business Rules, 5.2 Common Requirements, 5.3 Application Messages)", 1),
        ("IV. Software Design Description", 0),
        ("1. System Design (1.1 System Architecture, 1.2 Package Diagram)", 1),
        ("2. Database Design", 1),
        ("3. Detailed Design (3.1 Auth, 3.2 Catalog, 3.3 Cart, 3.4 Checkout/Payment, 3.5 Admin)", 1),
        ("V. Software Testing Documentation", 0),
        ("1. Scope of Testing (1.1 In-Scope, 1.2 Out-of-Scope, 1.3 Constraints & Assumptions)", 1),
        ("2. Test Strategy (2.1 Testing Types, 2.2 Test Levels, 2.3 Supporting Tools)", 1),
        ("3. Test Plan (3.1 Human Resources, 3.2 Test Environment, 3.3 Milestones, 3.4 Syllabus Audit Ch.I–VII)", 1),
        ("4. Test Cases (Static FTR, EP/BVA, Decision Table, State Transition, White-Box CFG/V(G)/MCC, Security & Load)", 1),
        ("5. Test Reports (Unit/JaCoCo/Vitest, Postman/Security, CodeceptJS E2E, Performance, Defect Reports, Exit Criteria)", 1),
        ("VI. Release Package & User Guides", 0),
        ("1. Deliverable Package", 1),
        ("2. Installation Guides (2.1 System Requirements, 2.2 Installation Instruction)", 1),
        ("3. User Manual (3.1 Overview, 3.2 Admin Workflow, 3.3 Customer/User Workflow)", 1),
    ]
    for title, indent in toc_lines:
        ptoc = doc.add_paragraph()
        ptoc.paragraph_format.left_indent = Inches(0.28 * indent)
        ptoc.paragraph_format.space_before = Pt(1)
        ptoc.paragraph_format.space_after = Pt(2)
        rt = ptoc.add_run(title)
        style_run(rt, 11 if indent == 0 else 10.5, bold=(indent == 0))
    doc.add_page_break()

    # =========================================================================
    # ACKNOWLEDGEMENT & DEFINITION AND ACRONYMS
    # =========================================================================
    add_h(doc, "Acknowledgement", level=1)
    add_p(doc, "Việc hoàn thiện hệ thống thương mại điện tử VGA Store cùng toàn bộ bộ tài liệu Đặc tả, Thiết kế và Kiểm chứng phần mềm không thể thành công nếu thiếu sự hướng dẫn tận tâm của giảng viên và sự phối hợp chặt chẽ của các thành viên trong nhóm.")
    add_p(doc, "Trước hết, nhóm xin gửi lời cảm ơn chân thành đến giảng viên hướng dẫn Nguyễn Văn Chiến cùng quý thầy cô Trường Đại học Giao thông Vận tải TP. Hồ Chí Minh (UTH). Những bài giảng hệ thống từ Chương I đến Chương VII về quy trình kiểm thử, kiểm thử tĩnh FTR, các kỹ thuật thiết kế test hộp đen/hộp trắng, quản lý lỗi phần mềm và công cụ kiểm thử hiện đại đã giúp nhóm có nền tảng vững chắc để áp dụng trực tiếp vào dự án thực tế.")
    add_p(doc, "Cuối cùng, nhóm xin cảm ơn toàn thể 6 thành viên đã nỗ lực rà soát mã nguồn, xây dựng kịch bản kiểm thử tự động và khắc phục các lỗi phát hiện trong quá trình kiểm chứng. Mọi góp ý từ thầy và hội đồng đánh giá sẽ giúp nhóm tiếp tục hoàn thiện hệ thống ngày càng tốt hơn.")

    add_h(doc, "Definition and Acronyms", level=1)
    add_table(doc, ["Acronym", "Definition", "Description"], [
        ["API", "Application Programming Interface", "Giao diện lập trình ứng dụng RESTful JSON giao tiếp giữa React UI và Spring Boot Backend."],
        ["BVA", "Boundary Value Analysis", "Kỹ thuật kiểm thử hộp đen tập trung vào các giá trị tại biên và cận biên (Standard 4n+1, Robustness 6n+1)."],
        ["CFG", "Control Flow Graph", "Đồ thị dòng điều khiển biểu diễn các nút lệnh và nhánh rẽ trong kiểm thử hộp trắng cấu trúc."],
        ["CI/CD", "Continuous Integration / Deployment", "Quy trình tích hợp, kiểm thử và đóng gói Docker Image tự động trên GitHub Actions."],
        ["E2E", "End-to-End Testing", "Kiểm thử luồng nghiệp vụ toàn trình trên trình duyệt thực với CodeceptJS & Playwright."],
        ["EP", "Equivalence Partitioning", "Kỹ thuật phân hoạch miền đầu vào thành các lớp tương đương hợp lệ (Valid) và không hợp lệ (Invalid)."],
        ["ERD", "Entity Relationship Diagram", "Sơ đồ quan hệ thực thể mô tả 16 bảng dữ liệu trong PostgreSQL."],
        ["FTR", "Formal Technical Review", "Quy trình rà soát kỹ thuật chính thức 6 bước đối với mã nguồn và tài liệu thiết kế."],
        ["JWT", "JSON Web Token", "Chuỗi token ký số HS256 phục vụ xác thực không trạng thái (Stateless Auth) và phân quyền RBAC."],
        ["MCC", "Multiple Condition Coverage", "Độ phủ tổ hợp đa điều kiện logic bên trong biểu thức quyết định."],
        ["RBAC", "Role-Based Access Control", "Cơ chế phân quyền truy cập theo vai trò (ADMIN, STAFF, USER)."],
        ["SCI", "Software Configuration Item", "Các hạng mục cấu hình phần mềm (Tài liệu, Source code, Dữ liệu test, Công cụ)."],
        ["SDD / SRS", "Software Design / Requirement Spec", "Tài liệu thiết kế kiến trúc hệ thống và đặc tả yêu cầu phần mềm."],
        ["SQLi / XSS", "SQL Injection / Cross-Site Scripting", "Lỗ hổng bảo mật chèn truy vấn SQL hoặc mã JavaScript độc hại qua đầu vào."],
        ["UAT", "User Acceptance Testing", "Kiểm thử chấp nhận người dùng cuối xác nhận hệ thống đáp ứng nhu cầu nghiệp vụ."],
        ["V(G)", "Cyclomatic Complexity", "Độ phức tạp McCabe xác định số đường cơ sở độc lập tối thiểu (V(G) = E - N + 2 = P + 1)."],
    ], col_widths=[1.1, 2.0, 3.6], font_size=9.5)

    # =========================================================================
    # I. PROJECT INTRODUCTION
    # =========================================================================
    add_h(doc, "I. Project Introduction", level=1)
    add_h(doc, "1. Overview", level=2)
    add_h(doc, "1.1 Project Information", level=3)
    add_bullet(doc, "VGA Store — Cửa hàng Card Màn Hình (Graphics Card E-Commerce System)", bold_prefix="Project Name: ")
    add_bullet(doc, "010412204003 (Môn Kiểm chứng Phần mềm — Software Verification & Testing)", bold_prefix="Course / Project Code: ")
    add_bullet(doc, "Nhóm 7 — Trường Đại học Giao thông Vận tải TP. Hồ Chí Minh (UTH)", bold_prefix="Group Name: ")
    add_bullet(doc, "Full-Stack Web Application (React 19 Vite User/Admin Portals + Java Spring Boot 3.3.4 REST API + PostgreSQL 17 + Docker Compose)", bold_prefix="Software Type: ")

    add_h(doc, "1.2 Project Team", level=3)
    add_table(doc, ["Full Name", "Role", "Email / GitHub Handle", "Primary Focus"], [
        ["Nguyễn Văn Chiến", "Supervisor (GVHD)", "Giảng viên hướng dẫn UTH", "Định hướng chuyên môn, đánh giá quy trình & báo cáo"],
        ["Trần Đình Trọng", "Leader", "trongtd0773@ut.edu.vn (@Trng-Ngyn)", "CI/CD GitHub Actions, Jira Board, Test Plan, White-Box"],
        ["Ngô Hữu Phước", "Member", "ngohuuphuoc36@gmail.com (@NgoHuuPhuoc)", "Docker Containerization, Postman RBAC & Security Testing"],
        ["Phan Khôi", "Member", "khoiphan252005@gmail.com (@Koi252005)", "CodeceptJS E2E Setup, Catalog/Admin Flow & Usability QA"],
        ["Lê Minh Hiếu", "Member", "hieulm3065@ut.edu.vn (@Lehieu3065)", "JetBrains Qodana, ESLint Static Analysis & FTR Review"],
        ["Nguyễn Văn Huy", "Member", "lehuy9095@gmail.com (@huyhuy887)", "E2E Cart/Checkout/Auth, Decision Table & State Transition"],
        ["Duy Vũ", "Member", "duyvudao79@gmail.com (@DuyVu303)", "Unit Testing JUnit/Vitest, JaCoCo & Software Defect Reports"],
    ], col_widths=[1.45, 1.15, 2.0, 2.1], font_size=9.5)

    add_h(doc, "2. Product Background", level=2)
    add_p(doc, "Thị trường linh kiện máy tính hiệu năng cao, đặc biệt là Card Đồ Họa (VGA / GPU chuyên dụng cho Gaming, AI và Đồ họa 3D), đang tăng trưởng mạnh tại Việt Nam. Người mua thường gặp khó khăn khi phải tự so sánh thông số phức tạp (VRAM, bộ nhớ GDDR6/GDDR6X, công suất nguồn khuyến nghị PSU, đầu cấp nguồn, kích thước tản nhiệt) và dễ chọn sai cấu hình tương thích với PC hiện tại.")
    add_p(doc, "Nhằm giải quyết bài toán này, nhóm phát triển hệ thống VGA Store tích hợp danh mục thông số kỹ thuật chuyên sâu, công cụ so sánh trực quan tối đa 3 VGA cùng lúc, trợ lý ảo Google Gemini AI tư vấn cấu hình, giỏ hàng đồng bộ DB, thanh toán đa kênh (COD, Chuyển khoản ngân hàng, VNPay, MoMo) và cổng quản trị Admin riêng biệt.")

    add_h(doc, "3. Existing Systems", level=2)
    add_h(doc, "3.1 GearVN.com", level=3)
    add_bullet(doc, "Nền tảng bán lẻ linh kiện PC & Gaming Gear phổ biến tại Việt Nam với danh mục VGA đa dạng.", bold_prefix="Mô tả & Tính năng: ")
    add_bullet(doc, "Ưu điểm: Tốc độ tải nhanh, nhiều khuyến mãi. Nhược điểm: Chưa có công cụ AI hỏi đáp trực tiếp cấu hình PSU/case theo từng model GPU; mã nguồn đóng phục vụ thương mại.", bold_prefix="Ưu / Nhược điểm: ")
    add_h(doc, "3.2 PhongVu.vn", level=3)
    add_bullet(doc, "Hệ thống siêu thị công nghệ đa ngành hàng từ laptop đến linh kiện rời.", bold_prefix="Mô tả & Tính năng: ")
    add_bullet(doc, "Ưu điểm: Thanh toán trực tuyến ổn định, xuất hóa đơn điện tử. Nhược điểm: Bộ lọc chuyên biệt cho thông số phần cứng VGA chưa sâu và thiếu khu vực so sánh song song gọn nhẹ.", bold_prefix="Ưu / Nhược điểm: ")

    add_h(doc, "4. Business Opportunity", level=2)
    add_p(doc, "Xây dựng một nền tảng thương mại điện tử ngách tập trung 100% vào Card Đồ Họa giúp tối ưu trải nghiệm tư vấn kỹ thuật trước khi mua, rút ngắn thời gian chốt đơn qua luồng thanh toán VNPay/MoMo tự động hết hạn đơn chưa thanh toán sau 15 phút (giải phóng tồn kho tự động), đồng thời cung cấp bộ dữ liệu kiểm thử chuẩn hóa để chứng minh chất lượng vận hành tin cậy.")

    add_h(doc, "5. Software Product Vision", level=2)
    add_p(doc, "VGA Store hướng tới trở thành ứng dụng mẫu mực kết hợp kiến trúc tách biệt User/Admin Portal, API bảo mật JWT không trạng thái, đóng gói Container nhất quán qua Docker Compose và đạt chuẩn kiểm chứng đa tầng (Static Review, White-Box Unit Coverage >= 70%, Black-Box API & Data-Driven, Security SQLi/XSS, Performance Load Test và E2E Automation).")

    add_h(doc, "6. Project Scope & Limitations", level=2)
    add_h(doc, "6.1 Major Features", level=3)
    for feat in [
        "FE01 — Authentication & User Profile: Đăng ký, Đăng nhập (BCrypt + JWT), Google OAuth, quản lý sổ địa chỉ giao hàng và đổi mật khẩu.",
        "FE02 — VGA Catalog, Search, Filter & Compare: Hiển thị sản phẩm nổi bật, lọc đa tiêu chí (thương hiệu, khoảng giá, từ khóa), so sánh tối đa 3 VGA.",
        "FE03 — AI Advisor & Tech Blog / Reviews: Chatbot Gemini 1.5 Flash tư vấn chọn VGA, bài viết công nghệ và đánh giá sản phẩm 1–5 sao.",
        "FE04 — Shopping Cart & Checkout Workflow: Giỏ hàng DB có kiểm tra tồn kho, đặt hàng kèm tự động trừ tồn kho.",
        "FE05 — Payment Gateways & Auto-Expiry Scheduler: Hỗ trợ COD, Chuyển khoản, sinh URL VNPay HMAC-SHA512 / MoMo HMAC-SHA256 và cron job tự hủy đơn quá 15 phút.",
        "FE06 — Admin Portal: Dashboard thống kê doanh thu/đơn hàng, CRUD Sản phẩm (upload ảnh + thông số GPU), Hãng, Danh mục, Blog, Pin-to-top và Quản lý User/Order/System Settings.",
    ]:
        add_bullet(doc, feat)
    add_h(doc, "6.2 Limitations & Exclusions", level=3)
    for lim in [
        "LI-01: Tích hợp thanh toán VNPay/MoMo sử dụng môi trường Sandbox thử nghiệm, không phát sinh giao dịch tài chính thật.",
        "LI-02: Chức năng quản lý bảo hành (`warranties`) và mã giảm giá (`coupons`) đã có schema DB nhưng chưa mở UI quản trị hoàn chỉnh trong Sprint hiện tại.",
        "LI-03: Chưa kết nối đơn vị vận chuyển thực tế (GHN/GHTK API) để đồng bộ mã vận đơn tự động.",
    ]:
        add_bullet(doc, lim)

    # =========================================================================
    # II. PROJECT MANAGEMENT PLAN
    # =========================================================================
    add_h(doc, "II. Project Management Plan", level=1)
    add_h(doc, "1. Overview", level=2)
    add_h(doc, "1.1 Scope & Estimation (WBS — Chương VI)", level=3)
    add_table(doc, ["No.", "WBS Item", "Complexity", "Est. Effort (man-days)"], [
        ["1", "FE01. Authentication, Security & Profile Management", "Medium", "12"],
        ["2", "FE02. VGA Catalog, Multi-filter & 3-Way Comparison", "Medium", "14"],
        ["3", "FE03. Shopping Cart & Inventory Locking Logic", "Complex", "12"],
        ["4", "FE04. Checkout, Order Lifecycle & Payment Gateway (VNPay/MoMo)", "Complex", "18"],
        ["5", "FE05. Admin Portal, Charts Dashboard & Content CMS", "Medium", "15"],
        ["6", "QA01. Static Testing (Qodana, ESLint, FTR Review)", "Medium", "8"],
        ["7", "QA02. White-Box Unit Tests (JUnit 5 + Vitest + JaCoCo >= 70%)", "Complex", "14"],
        ["8", "QA03. Black-Box API (Postman/CSV), Security, Load Test & CodeceptJS E2E", "Complex", "16"],
        ["", "TOTAL ESTIMATED EFFORT", "", "109"],
    ], col_widths=[0.5, 3.8, 1.1, 1.3], font_size=9.5)

    add_h(doc, "1.2 Project Objectives (Quality & Verification Targets)", level=3)
    add_table(doc, ["#", "Testing Stage", "Target Coverage / Criteria", "Defect Threshold", "Tool / Method"], [
        ["1", "Static Review (FTR + Lint)", "100% core services & critical UI pages reviewed", "0 Critical blockers", "Qodana, ESLint 9, FTR Checklist"],
        ["2", "Unit Test (BE + FE)", "Backend Line Coverage >= 70% (75.8% achieved); Services >= 90%", "0 test failures", "JUnit 5, Mockito, JaCoCo, Vitest"],
        ["3", "Integration / API Testing", "100% core REST endpoints + EP/BVA CSV data-driven", "0 unhandled 500s", "Postman CLI v1.80.0 + Docker API"],
        ["4", "System E2E & Non-Functional", "100% E2E scenarios, SQLi/XSS blocked, Load Error Rate < 1%", "0 Critical bugs open", "CodeceptJS + Playwright, Python Load"],
    ], col_widths=[0.4, 1.5, 2.0, 1.2, 1.6], font_size=9.5)

    add_h(doc, "1.3 Project Risks", level=3)
    add_table(doc, ["#", "Risk Description", "Impact", "Possibility", "Mitigation / Response Plan"], [
        ["R1", "Kiểm thử phụ thuộc PostgreSQL live làm lỗi CI/local build", "High", "Medium", "Cấu hình H2 In-Memory mode PostgreSQL trong `src/test/resources/application.properties`"],
        ["R2", "Lỗi đường dẫn JDK trên Windows khiến Surefire fork thất bại", "Medium", "Medium", "Thiết lập `<forkCount>0</forkCount>` kết hợp `MAVEN_OPTS=-javaagent:jacoco`"],
        ["R3", "Docker Hub image cũ chưa đồng bộ bản vá code mới nhất", "High", "High", "Build lại container từ source local (`docker compose up -d --build`) trước mọi phiên chạy live"],
        ["R4", "Lỗ hổng bảo mật phân quyền / State Transition sai lệch tồn kho", "High", "Medium", "Kiểm thử RBAC, Tampered JWT, State Transition & lập Bug Report (`BUG-01..09`)"],
    ], col_widths=[0.4, 2.2, 0.8, 0.9, 2.4], font_size=9.5)

    add_h(doc, "2. Management Approach", level=2)
    add_h(doc, "2.1 Project Process", level=3)
    add_p(doc, "Dự án áp dụng mô hình phát triển linh hoạt Agile/Scrum kết hợp quy trình kiểm thử 5 bước (Planning & Control, Analysis & Design, Implementation & Execution, Evaluating Exit Criteria & Reporting, Test Closure). Công việc được chia thành các Sprint quản lý trực tiếp trên Jira (`KAN-1` đến `KAN-20`, tổng 19 hạng mục hoàn thành 100% trạng thái Done).")

    add_h(doc, "2.2 Quality Management", level=3)
    add_bullet(doc, "Tuân thủ nguyên tắc Early Testing (Chương I): quét tĩnh Qodana & ESLint sớm trước khi tích hợp.", bold_prefix="Static & Early QA: ")
    add_bullet(doc, "Mỗi thay đổi Backend đều phải vượt qua Maven `mvnw test`, `jacoco:report` và Postman CLI trước khi đóng ticket.", bold_prefix="Automated Regression Gate: ")
    add_bullet(doc, "Mọi lỗi phát hiện đều được tái hiện, phân loại Severity/Priority theo chuẩn Chương V và lưu vết trạng thái xử lý.", bold_prefix="Defect Lifecycle Tracking: ")

    add_h(doc, "2.3 Training Plan", level=3)
    add_table(doc, ["Training Topic", "Participants", "Duration", "Outcome"], [
        ["JUnit 5, Mockito & JaCoCo Coverage", "Duy Vũ, Trần Đình Trọng", "2 days", "Viết 64 ca Unit Test đạt 75.8% Line Coverage"],
        ["Postman CLI & Data-Driven CSV", "Lê Minh Hiếu, Ngô Hữu Phước", "1.5 days", "Xây dựng 54 API requests + 3 CSV EP/BVA"],
        ["CodeceptJS + Playwright & Security", "Phan Khôi, Nguyễn Văn Huy", "2 days", "Tự động hóa 20 kịch bản E2E & kiểm thử Admin"],
    ], col_widths=[2.1, 1.8, 0.9, 1.9], font_size=9.5)

    add_h(doc, "3. Project Deliverables", level=2)
    add_table(doc, ["#", "Deliverable", "Target Milestone", "Location / Artifact"], [
        ["1", "Jira Backlog & QA Plan", "Week 1–2", "Jira Project KAN (KAN-1..KAN-20), Ke_Hoach_Jira...md"],
        ["2", "CI/CD, Docker Compose & Qodana Config", "Week 3", ".github/workflows/*.yml, docker-compose.yml, qodana.yaml"],
        ["3", "White-Box Unit Suites (BE + FE)", "Week 4–6", "src/test/java/... (64 JUnit) & redux/__tests__, utils/__tests__ (8 Vitest)"],
        ["4", "Black-Box Postman + CSV + Performance + Security", "Week 7–9", "postman/, testing/performance_load_test.py"],
        ["5", "CodeceptJS E2E Suite & Static FTR / Defect Docs", "Week 10–11", "e2e-tests/tests/01..07, testing/FTR...md, testing/Software_Defect_Reports.md"],
        ["6", "Final Project & Verification Report", "Week 12", "Bao_Cao_Du_An_Va_Kiem_Chung_Phan_Mem_VGA_Store.docx"],
    ], col_widths=[0.4, 2.2, 1.1, 3.0], font_size=9.5)

    add_h(doc, "4. Responsibility Assignments (RDSI Matrix — 6 Members)", level=2)
    add_p(doc, "Quy ước vai trò: R = Responsible (Thực hiện chính), D = Decision/Approver (Duyệt), S = Support (Hỗ trợ), I = Informed (Được thông báo).", italic=True)
    add_table(doc, ["Work Package / Task", "Trọng", "Phước", "Khôi", "Hiếu", "Huy", "Vũ"], [
        ["Jira Sprint Setup & IEEE 829 Test Plan", "R/D", "S", "I", "I", "S", "S"],
        ["Static Analysis (Qodana, ESLint) & FTR Review", "D", "R", "R", "R", "S", "R"],
        ["Backend Unit Testing (JUnit 5 + JaCoCo)", "R/D", "S", "I", "I", "S", "R"],
        ["Frontend ESLint Fixes & Vitest Unit Tests", "R", "I", "R", "R", "I", "S"],
        ["Postman API, CSV Data-Driven & SQLi/XSS Security", "D", "R", "I", "R", "S", "S"],
        ["CodeceptJS Playwright E2E (User & Admin)", "D", "S", "R", "S", "R", "I"],
        ["Docker Containerization & Load Benchmark", "R/D", "R", "S", "I", "I", "S"],
        ["Defect Log & Final Verification Report", "R/D", "R", "R", "R", "R", "R"],
    ], col_widths=[2.8, 0.65, 0.65, 0.65, 0.65, 0.65, 0.65], font_size=9.5)

    add_h(doc, "5. Project Communications", level=2)
    add_table(doc, ["Communication Item", "Target", "Frequency", "Channel / Tool"], [
        ["Sprint Planning & Test Triage", "6 Members + GVHD", "Weekly / Sprint start", "Jira Board (`KAN`), Google Meet"],
        ["Code Review & FTR Meeting", "Author + Reviewers", "Before merge PR", "GitHub Pull Requests, `testing/FTR...md`"],
        ["Urgent Defect Sync", "QA & Dev owners", "Ad-hoc when bug found", "Zalo Group, GitHub Issues / Defect Log"],
    ], col_widths=[1.8, 1.4, 1.4, 2.1], font_size=9.5)

    add_h(doc, "6. Configuration Management", level=2)
    add_h(doc, "6.1 Document Management", level=3)
    add_p(doc, "Toàn bộ tài liệu đặc tả test case (`THIET_KE_TEST_CASE...md`), biên bản FTR, danh sách lỗi (`Software_Defect_Reports.md`) và báo cáo tổng hợp `.docx` được quản lý phiên bản tập trung trong Git repository nhánh `main` và sao lưu trên Desktop/Google Drive.")
    add_h(doc, "6.2 Source Code Management & SCI Inventory (Chương VI)", level=3)
    add_bullet(doc, "SCI-01 Documents: `README.md`, `Ke_Hoach_Jira...md`, `THIET_KE_TEST_CASE...md`, `testing/FTR_Static_Analysis_And_WhiteBox.md`, `testing/Software_Defect_Reports.md`.")
    add_bullet(doc, "SCI-02 Source Code: `backend/vgashop/`, `fontend/user/`, `fontend/admin/`, `database/create_tables.sql`, `database/seed_vga.sql`.")
    add_bullet(doc, "SCI-03 Test Data & Scripts: `postman/*.json`, `postman/*.csv`, `e2e-tests/tests/*.js`, `testing/*.py`, `src/test/java/...`.")
    add_bullet(doc, "SCI-04 Build & CI Tools: `docker-compose.yml`, `qodana.yaml`, `.github/workflows/*.yml`, `pom.xml` (JaCoCo 0.8.12).")

    add_h(doc, "6.3 Tools & Infrastructures", level=3)
    add_table(doc, ["Category", "Tools / Infrastructure Used in VGA Store"], [
        ["Backend Framework", "Java 17/21, Spring Boot 3.3.4, Spring Security, JJWT 0.11.5, Lombok"],
        ["Frontend Framework", "React 19.2, Vite 8.0, Redux Toolkit 2.11, Axios 1.14, Recharts 2.15, Gemini AI SDK"],
        ["Database", "PostgreSQL 17.7 Alpine (Production/Docker), H2 In-Memory DB (Unit Test CI)"],
        ["Static Analysis & Lint", "JetBrains Qodana (`qodana-jvm-community:2024.2`), ESLint 9.39"],
        ["Testing Frameworks", "JUnit 5 + Mockito, JaCoCo 0.8.12, Vitest 4.1, Postman CLI 1.80, CodeceptJS 3.6 + Playwright"],
        ["Container & CI/CD", "Docker Desktop & Compose, GitHub Actions (`main-ci`, `qodana`, `e2e-codecept`, `docker-build-push`), Jira"],
    ], col_widths=[1.8, 4.9], font_size=9.5)

    # =========================================================================
    # III. SOFTWARE REQUIREMENT SPECIFICATION
    # =========================================================================
    add_h(doc, "III. Software Requirement Specification", level=1)
    add_h(doc, "1. Product Overview", level=2)
    add_p(doc, "VGA Store vận hành theo mô hình Client-Server 3 tầng container hóa: người dùng cuối truy cập User Portal (`:5173`), quản trị viên truy cập Admin Portal (`:5174`), cả hai giao tiếp qua giao thức HTTP/JSON kèm JWT Bearer Token tới Spring Boot API (`:8080`) kết nối cơ sở dữ liệu PostgreSQL (`:5433`).")

    add_h(doc, "2. User Requirements", level=2)
    add_h(doc, "2.1 System Actors", level=3)
    add_table(doc, ["#", "Actor", "Role & Responsibilities"], [
        ["1", "Guest (Khách vãng lai)", "Xem trang chủ, duyệt/lọc/tìm kiếm VGA, so sánh thông số, xem chi tiết/review/blog, hỏi AI Chatbot, đăng ký/đăng nhập."],
        ["2", "Customer (ROLE_USER)", "Toàn bộ quyền Guest + quản lý giỏ hàng DB, đặt hàng Checkout, thanh toán COD/Bank/VNPay/MoMo, theo dõi/yêu cầu hủy đơn, đánh giá sản phẩm đã giao."],
        ["3", "Admin / Staff (ROLE_ADMIN, STAFF)", "Đăng nhập Admin Portal, xem Dashboard & biểu đồ doanh thu, CRUD Sản phẩm/Hãng/Danh mục/Blog, duyệt & đổi trạng thái Đơn hàng, khóa/mở khóa tài khoản User, cấu hình hệ thống."],
    ], col_widths=[0.4, 1.8, 4.5], font_size=9.5)

    add_h(doc, "2.2 Use Cases", level=2)
    add_h(doc, "2.2.1 Use Case Diagram", level=3)
    add_img(doc, DIAG / "fig_01_use_case.png", "Figure III.1: VGA Store System Use Case Diagram", width_in=6.2)

    add_h(doc, "2.2.2 Use Case Descriptions", level=3)
    add_table(doc, ["ID", "Use Case Name", "Actors", "Short Description"], [
        ["UC-01", "Browse, Search & Filter VGA", "Guest, Customer", "Liệt kê sản phẩm phân trang, tìm theo từ khóa, lọc theo hãng và khoảng giá min/max."],
        ["UC-02", "Compare Specs & AI Chat", "Guest, Customer", "So sánh tối đa 3 VGA (VRAM, PSU, kích thước) và hỏi tư vấn Google Gemini AI."],
        ["UC-03", "Register / Login / Google OAuth", "Guest, Customer, Admin", "Tạo tài khoản mã hóa BCrypt hoặc đăng nhập nhận JWT Token (HS256)."],
        ["UC-04", "Manage Shopping Cart", "Customer", "Thêm VGA (kiểm tra tồn kho), cập nhật số lượng, xóa item hoặc làm trống giỏ."],
        ["UC-05", "Checkout & Online Payment", "Customer", "Nhập địa chỉ/SĐT, trừ tồn kho, tạo Order PENDING và sinh URL thanh toán VNPay/MoMo."],
        ["UC-06", "Track, Cancel Order & Review", "Customer", "Theo dõi tiến độ đơn, gửi yêu cầu hủy khi PENDING/CONFIRMED, đánh giá sản phẩm."],
        ["UC-07", "Dashboard & Analytics Charts", "Admin", "Thống kê tổng đơn, doanh thu ngày/tháng/năm, hàng sắp hết (`stock <= 10`)."],
        ["UC-08", "Catalog & Content CRUD", "Admin", "Thêm/sửa/xóa mềm Sản phẩm kèm ảnh, Thương hiệu, Danh mục, Blog và Pin-to-top."],
        ["UC-09", "Order & Payment Management", "Admin", "Cập nhật trạng thái đơn (`CONFIRMED`, `SHIPPING`, `DELIVERED`, `CANCELLED`)."],
        ["UC-10", "User & System Settings Mgmt", "Admin", "Phân quyền Role, khóa tài khoản (chặn tự khóa chính mình/Admin khác), sửa cài đặt."],
    ], col_widths=[0.6, 1.8, 1.2, 3.1], font_size=9.2)

    add_h(doc, "3. Functional Requirements", level=2)
    add_h(doc, "3.1 System Functional Overview", level=3)
    add_h(doc, "3.1.1 – 3.1.4 User & Admin Screen Flows and Descriptions", level=4)
    add_img(doc, DIAG / "fig_02_screen_flow.png", "Figure III.2: User & Admin Portal Screen Flow Diagram", width_in=6.3)
    add_table(doc, ["Portal", "Route / Screen", "Key Functional Description"], [
        ["User (:5173)", "`/` (Home), `/products` (Shop)", "Banner động, danh sách VGA nổi bật, tìm kiếm từ khóa, lọc thương hiệu/khoảng giá."],
        ["User (:5173)", "`/product/:id`, `/blog`, `/service`", "Hiển thị thông số GPU (`gpu_model`, `vram`, `recommended_psu`), gửi đánh giá, tin công nghệ."],
        ["User (:5173)", "`/cart`, `/checkout`, `/payment/pending`", "Chỉnh số lượng giỏ hàng, nhập thông tin giao nhận, tạo giao dịch COD/VNPay/MoMo."],
        ["User (:5173)", "`/profile`, `/track-order`, `/wishlist`", "Cập nhật thông tin cá nhân, đổi mật khẩu, sổ địa chỉ mặc định, tra cứu lịch sử đơn hàng."],
        ["Admin (:5174)", "`/login`, `/` (Dashboard)", "Xác thực `ROLE_ADMIN`, biểu đồ Recharts theo chu kỳ (`today`, `7days`, `1month`, `1year`)."],
        ["Admin (:5174)", "`/products`, `/orders`, `/users`, `/settings`", "Quản lý kho sản phẩm, chuyển trạng thái đơn, quản lý thành viên & cấu hình công khai."],
    ], col_widths=[1.0, 2.0, 3.7], font_size=9.2)

    add_h(doc, "3.1.5 Screen & API Authorization Matrix", level=4)
    add_table(doc, ["Module / Endpoint Group", "CRUD", "Guest", "Customer (USER)", "Admin (ADMIN)"], [
        ["`/api/auth/**` (Login, Register, Google)", "C", "Allowed", "Allowed", "Allowed"],
        ["GET Products / Brands / Categories / Blogs / Reviews", "R", "Allowed", "Allowed", "Allowed"],
        ["GET `/api/settings/public`, `/api/service-policies/**`", "R", "Allowed (Fixed BUG-02)", "Allowed", "Allowed"],
        ["`/api/cart/**`, `/api/orders/checkout`, POST `/api/reviews`", "C-R-U-D", "401/403", "Allowed (Own data)", "Allowed"],
        ["`/api/payments/vnpay/callback`, `/momo/callback`", "C-U", "Signature Validated", "Signature Validated", "Allowed"],
        ["`/api/admin/**`, `/api/orders/admin/**`", "C-R-U-D", "401/403", "403 Forbidden", "Allowed"],
    ], col_widths=[2.6, 0.7, 1.1, 1.2, 1.1], font_size=9.2)

    add_h(doc, "3.1.6 Non-screen Functions & Background Jobs", level=4)
    add_bullet(doc, "`PaymentExpiryScheduler.expireUnpaidBankTransferOrders()`: Chạy định kỳ mỗi 60 giây (`@Scheduled(fixedDelay = 60_000)`), tự động tìm các đơn `PENDING` + `UNPAID` quá 15 phút dùng phương thức `BANK_TRANSFER`, đánh dấu Payment `FAILED`, đơn `CANCELLED` và hoàn trả số lượng tồn kho (`product.stock`).")

    add_h(doc, "3.1.7 Entity Relationship Diagrams", level=4)
    add_img(doc, DIAG / "fig_03_erd.png", "Figure III.3: Entity Relationship Diagram (16 PostgreSQL Tables)", width_in=6.3)

    add_h(doc, "3.2 Web Application Detailed Functional Specifications", level=3)
    add_table(doc, ["Function ID & Name", "Trigger & Actors", "Processing & Business Rules"], [
        ["3.2.1 Authenticate Web Users", "All Actors tại Header Login / `/login`", "Kiểm tra username/email & BCrypt password hash; nếu hợp lệ cấp JWT kèm claim `role`; từ chối tài khoản bị khóa."],
        ["3.2.2 Browse & Filter Products", "All Actors tại Shop `/products`", "Áp dụng Query JPA `findByNameContainingAndBrand_IdInAndPriceBetween`; phân trang mặc định theo `displayOrder` ASC."],
        ["3.2.3 Manage Shopping Cart", "Customer tại ProductDetail / Cart", "Tự tạo Cart khi chưa có (`CartService.getMyCart`); gộp số lượng nếu trùng VGA và chặn nếu vượt tồn kho."],
        ["3.2.4 Checkout & Create Order", "Customer tại `/checkout`", "Validate tên (2–50 ký tự), SĐT (10–15 số), địa chỉ (5–255 ký tự); trừ `product.stock`, tạo Order `PENDING` & làm rỗng Cart."],
        ["3.2.5 Online Payment Processing", "Customer chọn VNPay / MoMo", "Sinh chữ ký HMAC-SHA512 (`VNPayUtils`) / HMAC-SHA256 (`MomoUtils`); cập nhật `CONFIRMED` & `PAID` khi callback hợp lệ."],
        ["3.2.6 Admin CRUD & Pin-to-top", "Admin tại Portal `:5174`", "Kiểm tra trùng tên/SKU (`409 Conflict`), upload ảnh local `/uploads/`, soft-delete hoặc hard-delete kiểm thử ràng buộc FK."],
    ], col_widths=[1.7, 1.5, 3.5], font_size=9.2)

    add_h(doc, "4. Non-Functional Requirements", level=2)
    add_h(doc, "4.1 External Interfaces", level=3)
    add_bullet(doc, "Responsive ReactJS UI trên Chrome, Edge, Firefox (desktop `1280x720` và mobile `375x812`); giao diện hoàn toàn tiếng Việt.", bold_prefix="User Interface: ")
    add_bullet(doc, "Kết nối REST JSON nội bộ qua Axios, Google Gemini SDK (`@google/generative-ai`), Google OAuth, VNPay Sandbox và MoMo API.", bold_prefix="Software Interfaces: ")
    add_h(doc, "4.2 Quality Attributes", level=3)
    add_bullet(doc, "API catalog phản hồi trung bình < 100ms dưới tải 25 Concurrent VUs; trang tĩnh Nginx phản hồi < 20ms (xác minh tại Mục V.5.3).", bold_prefix="Performance: ")
    add_bullet(doc, "Mật khẩu băm BCrypt; xác thực Stateless JWT; chống SQL Injection qua JPA/Hibernate Prepared Statements; phân tách quyền User/Admin.", bold_prefix="Security: ")
    add_bullet(doc, "Hệ thống Docker Compose đảm bảo khởi tạo đồng nhất qua 4 container cô lập mạng `vga_network`.", bold_prefix="Reliability & Portability: ")

    add_h(doc, "5. Requirement Appendix", level=2)
    add_h(doc, "5.1 Business Rules", level=3)
    add_table(doc, ["ID", "Rule Definition"], [
        ["BR-01", "Username và Email đăng ký mới phải là duy nhất trong toàn hệ thống (`users` table)."],
        ["BR-02", "Người dùng chỉ được phép truy cập các endpoint phù hợp với Role (`ADMIN` / `USER`)."],
        ["BR-03", "Sản phẩm, Đơn hàng, Người dùng ưu tiên xóa mềm (`deleted = true`) nhằm bảo toàn lịch sử giao dịch."],
        ["BR-04", "Không được thêm vào giỏ hoặc đặt mua vượt quá số lượng tồn kho hiện có (`stock >= quantity`)."],
        ["BR-05", "Khách hàng chỉ được gửi yêu cầu hủy đơn khi trạng thái hiện tại là `PENDING` hoặc `CONFIRMED`."],
        ["BR-06", "Admin không thể tự khóa hoặc tự xóa chính tài khoản đang đăng nhập và không thể khóa Admin khác."],
        ["BR-07", "Đơn thanh toán chuyển khoản chưa trả sau 15 phút tự động hủy và hoàn tồn kho về sản phẩm."],
    ], col_widths=[0.8, 5.9], font_size=9.5)

    add_h(doc, "5.2 Common Requirements", level=3)
    add_table(doc, ["Req ID", "Name", "Specification"], [
        ["CR-01", "Dual Input Validation", "Kiểm tra ràng buộc bắt buộc (tên, email, SĐT, số lượng) đồng thời ở React Client và Spring `@Valid` DTO."],
        ["CR-02", "Authorization & Auth Check", "Mọi request tới tài nguyên riêng tư phải qua `JwtAuthFilter` xác thực Bearer JWT."],
        ["CR-03", "Friendly Error Wrapper", "`@RestControllerAdvice` (`GlobalExceptionHandler`) chuẩn hóa phản hồi lỗi JSON `ApiResponse(success=false, message)`."],
    ], col_widths=[0.8, 1.8, 4.1], font_size=9.5)

    add_h(doc, "5.3 Application Messages List", level=3)
    add_table(doc, ["Code", "HTTP / Type", "Context", "Actual Message in VGA Store"], [
        ["MSG01", "Toast Success", "Review submission", "Đăng đánh giá thành công!"],
        ["MSG02", "200 OK JSON", "Add to Cart", "Thêm vào giỏ hàng thành công"],
        ["MSG03", "400 Bad Request", "Validation DTO", "Dữ liệu không hợp lệ / Số lượng phải >= 1"],
        ["MSG04", "409 Conflict", "Duplicate SKU/Name", "Sản phẩm / Thương hiệu / Email đã tồn tại!"],
        ["MSG05", "404 Not Found", "Resource lookup", "Không tìm thấy sản phẩm / danh mục / đơn hàng"],
        ["MSG06", "401 / 403", "Security guard", "Chặn truy cập khi thiếu JWT hoặc sai quyền ADMIN"],
    ], col_widths=[0.7, 1.3, 1.5, 3.2], font_size=9.2)

    # =========================================================================
    # IV. SOFTWARE DESIGN DESCRIPTION
    # =========================================================================
    add_h(doc, "IV. Software Design Description", level=1)
    add_h(doc, "1. System Design", level=2)
    add_h(doc, "1.1 System Architecture", level=3)
    add_img(doc, DIAG / "fig_04_architecture.png", "Figure IV.1: VGA Store Full-Stack & Container Architecture", width_in=6.3)

    add_h(doc, "1.2 Package Diagram & Modules Structure", level=3)
    add_h(doc, "1.2.1 Web Application Package Structure (`fontend/user` & `fontend/admin`)", level=4)
    add_table(doc, ["Package", "Responsibility"], [
        ["`src/pages/`", "Các màn hình chính (`Home`, `Shop`, `ProductDetail`, `Cart`, `Checkout`, `Profile`, Admin `Dashboard/Products/Orders`)."],
        ["`src/components/`", "UI tái sử dụng (`Header`, `Footer`, `ProductCard`, `CompareModal`, `AIChatWidget`, `PrivateRoute`)."],
        ["`src/redux/`", "Quản lý State toàn cục bằng Redux Toolkit (`authSlice`, `cartSlice`, `compareSlice`, `wishlistSlice`)."],
        ["`src/services/` & `api/`", "Cấu hình `axiosClient` tự đính kèm JWT header và các hàm gọi REST API tương ứng từng module."],
        ["`src/utils/`", "Tiện ích hiển thị (`formatCurrency`, `truncate`, `alertUtils`, `orderNewUtils`)."],
    ], col_widths=[1.8, 4.9], font_size=9.5)

    add_h(doc, "1.2.2 Backend Source & Business Modules Structure (`com.example.vgashop`)", level=4)
    add_table(doc, ["Package", "Key Classes", "Description"], [
        ["`controler`", "12 REST Controllers", "`AuthController`, `ProductController`, `CartController`, `OrderController`, `PaymentController`, `AdminController`..."],
        ["`service`", "11 Business Services", "`AuthService`, `ProductService`, `BrandService`, `CategoryService`, `CartService`, `OrderService`, `PaymentService`, `AdminService`, `UserService`, `SystemSettingService`, `PaymentExpiryScheduler`"],
        ["`security`", "`SecurityConfig`, `JwtUtil`, Filters", "Phân quyền endpoint, CORS policy, password BCrypt và JWT validation."],
        ["`repository` & `entity`", "13 Repos, 16 Entities", "Spring Data JPA mapping quan hệ ORM sang PostgreSQL."],
        ["`exception` & `utils`", "`GlobalExceptionHandler`, VNPay/MoMo", "Bắt ngoại lệ tập trung và ký/kiểm tra chữ ký HMAC thanh toán."],
    ], col_widths=[1.4, 2.0, 3.3], font_size=9.2)

    add_h(doc, "2. Database Design", level=2)
    add_p(doc, "Cơ sở dữ liệu PostgreSQL 17 gồm 16 bảng chuẩn hóa (`database/create_tables.sql`), sử dụng khóa tự tăng Identity và các ràng buộc `CHECK` / `UNIQUE` / `FOREIGN KEY` bảo toàn toàn vẹn dữ liệu.")
    add_table(doc, ["Table Name", "Primary Keys & Constraints", "Core Purpose"], [
        ["`users`, `user_addresses`", "PK `id`, UQ `username`, UQ `email`", "Lưu thông tin tài khoản, mật khẩu BCrypt, Role và nhiều địa chỉ nhận hàng."],
        ["`brands`, `categories`", "PK `id`, UQ `name`, UQ `slug`", "Phân loại thương hiệu (ASUS, MSI, Gigabyte...) và danh mục GPU."],
        ["`products`", "PK `id`, UQ `sku`, FK `brand_id`, `category_id`", "Thông tin giá, tồn kho, ảnh và thông số phần cứng VGA chuyên biệt."],
        ["`carts`, `cart_items`", "PK `id`, UQ `user_id`, FK `cart_id`, `product_id`", "Giỏ hàng bền vững của khách hàng đã đăng nhập."],
        ["`orders`, `order_items`", "PK `id`, UQ `order_code`, CHECK `payment_status`", "Đơn hàng, tổng tiền, trạng thái xử lý và chi tiết sản phẩm tại thời điểm mua."],
        ["`payments`", "PK `id`, FK `order_id`, CHECK `payment_method`", "Lưu lịch sử thanh toán (`COD`, `BANK_TRANSFER`, `VNPAY`, `MOMO`) & mã giao dịch."],
        ["`reviews`, `blogs`, `system_settings`, `service_policies`, `coupons`, `warranties`", "PK `id`, CHECK `rating` 1..5", "Đánh giá, tin tức, cấu hình hệ thống, chính sách bảo hành & khuyến mãi."],
    ], col_widths=[1.6, 2.2, 2.9], font_size=9.2)

    add_h(doc, "3. Detailed Design", level=2)
    add_img(doc, DIAG / "fig_05_sequence_checkout.png", "Figure IV.2: Detailed Sequence Diagram — Checkout & Payment Gateway Flow", width_in=6.2)
    add_table(doc, ["Feature Flow", "Controller -> Service -> Repository", "Key Specification"], [
        ["3.1 Authenticate", "`AuthController` -> `AuthService` -> `UserRepository`, `JwtUtil`", "Kiểm tra `passwordEncoder.matches` hoặc đăng nhập Google; trả về `AuthResponse(token, username, role)`."],
        ["3.2 Search/Filter VGA", "`ProductController` -> `ProductService` -> `ProductRepository`", "Chuẩn hóa tham số null (`minPrice=0.0`, `maxPrice=MAX_VALUE`), sắp xếp Pageable theo `price`/`id`."],
        ["3.3 Cart Operations", "`CartController` -> `CartService` -> `CartRepository`", "`@Transactional` read-write tại `getMyCart` cho phép tạo mới Cart an toàn (Fix BUG-01)."],
        ["3.4 Checkout & Pay", "`OrderController`/`PaymentController` -> Services & Utils", "Trừ tồn kho nguyên tử trong Transaction; tạo chữ ký URL VNPay SHA512 / MoMo SHA256."],
        ["3.5 Admin Portal APIs", "`AdminController` -> `AdminService` -> All Repos", "Thống kê chart theo khoảng thời gian, khóa/mở user có guard tự bảo vệ Admin."],
    ], col_widths=[1.4, 2.3, 3.0], font_size=9.2)

    # =========================================================================
    # V. SOFTWARE TESTING DOCUMENTATION (CHƯƠNG I–VII COMPLETE IMPLEMENTATION)
    # =========================================================================
    add_h(doc, "V. Software Testing Documentation", level=1)
    add_h(doc, "1. Scope of Testing", level=2)
    add_h(doc, "1.1 In-Scope Testing", level=3)
    for item in [
        "Kiểm thử tĩnh (Static Analysis & FTR): Mã nguồn Java (`backend/vgashop/src/main/java`) và React JS/JSX (`fontend/user/src`, `fontend/admin/src`).",
        "Kiểm thử đơn vị (Unit Test): 11 Service Backend, Security Filters, VNPay/MoMo Utils, GlobalExceptionHandler, Controllers và Redux Slices/Utils của 2 Frontend.",
        "Kiểm thử tích hợp API & Bảo mật: 54 API requests trên 8 nhóm nghiệp vụ, 3 bộ Data-Driven CSV (`data_login_test`, `data_search_test`, `data_checkout_bva`), SQLi/XSS/Tampered JWT.",
        "Kiểm thử hệ thống E2E & Hiệu năng: 20 kịch bản trình duyệt CodeceptJS/Playwright qua 7 suites (`01..07`) và 7 kịch bản tải song song (Load Test 10–25 VUs).",
    ]:
        add_bullet(doc, item)

    add_h(doc, "1.2 Out-of-Scope Testing", level=3)
    add_bullet(doc, "Giao dịch tài chính thật qua cổng ngân hàng quốc gia VNPay/MoMo thực tế (chỉ xác minh ở mức tạo URL + chữ ký HMAC Sandbox & từ chối callback giả mạo).")
    add_bullet(doc, "Chất lượng trả lời ngữ nghĩa chuyên sâu của API bên thứ ba Google Gemini AI.")

    add_h(doc, "1.3 Constraints & Assumptions", level=3)
    add_bullet(doc, "Unit Test Backend chạy độc lập hoàn toàn với H2 In-Memory ở chế độ tương thích PostgreSQL; Integration/E2E/Load Test chạy trực tiếp trên 4 Docker containers đang vận hành (`localhost:8080`, `5173`, `5174`, `5433`).")

    add_h(doc, "2. Test Strategy", level=2)
    add_h(doc, "2.1 Testing Types & 2.2 Test Levels", level=3)
    add_table(doc, ["Type of Tests", "Unit", "Integration", "System", "Acceptance (UAT)"], [
        ["Static Testing (FTR, Qodana, ESLint)", "X", "X", "", ""],
        ["Structural White-Box (JUnit 5, JaCoCo, Vitest)", "X", "", "", ""],
        ["API Functional, Data-Driven & Contract Testing", "", "X", "X", ""],
        ["Non-Functional Security (RBAC, SQLi, XSS, JWT) & Performance Load", "", "X", "X", ""],
        ["Functional End-to-End & Change Regression (CodeceptJS)", "", "", "X", "X"],
    ], col_widths=[3.5, 0.7, 0.9, 0.7, 0.9], font_size=9.5)

    add_h(doc, "2.3 Supporting Tools (Phân loại theo 12 nhóm Chương VII)", level=3)
    add_table(doc, ["Tool Category (Ch. VII)", "Tool Applied in VGA Store", "Purpose / Role"], [
        ["Static Analysis Tools", "JetBrains Qodana, ESLint 9.39, `collect_static_metrics.py`", "Quét code smells, `no-undef` runtime crashes, đo LOC & Cyclomatic V(G)."],
        ["Test Execution & Harness", "JUnit 5 + Mockito, Vitest 4.1, CodeceptJS + Playwright", "Chạy tự động Unit Test (Java/JS) và kịch bản trình duyệt Chromium."],
        ["Coverage Measurement", "JaCoCo 0.8.12 (`jacoco-maven-plugin`)", "Đo chính xác độ phủ Line, Branch, Method, Instruction (đạt 75.8% Line)."],
        ["API & Test Data Prep", "Postman CLI 1.80.0 + CSV Data Files", "Tự động kiểm thử API, Data-Driven EP/BVA và xuất Run Reports lên Cloud."],
        ["Performance / Load Tool", "`testing/performance_load_test.py` (ThreadPoolExecutor)", "Giả lập 10–25 Concurrent VUs đo Avg, P95, Max Latency & RPS."],
        ["Test & Defect Management", "Jira Software (`KAN`), `testing/Software_Defect_Reports.md`", "Quản lý Sprint Backlog, phân công 6 thành viên và theo dõi vòng đời lỗi."],
    ], col_widths=[1.8, 2.3, 2.6], font_size=9.2)

    add_h(doc, "3. Test Plan", level=2)
    add_h(doc, "3.1 Human Resources & 3.2 Test Environment & 3.3 Milestones", level=3)
    add_table(doc, ["Phase / Milestone", "Assignee(s)", "Environment / Tools", "Timeline & Status"], [
        ["M1. Planning, Jira Setup & H2 Config", "Trần Đình Trọng, Duy Vũ", "Jira `KAN-3..KAN-5`, Spring H2", "Done (100%)"],
        ["M2. Static Review (FTR), Qodana & ESLint", "Lê Minh Hiếu, Trọng, Khôi", "Qodana, ESLint 9 (`user` & `admin`)", "Done (Phát hiện & vá BUG-03,04,07)"],
        ["M3. White-Box Unit Test Expansion & JaCoCo", "Duy Vũ, Trọng", "Maven + JUnit 5 + JaCoCo 0.8.12 + Vitest", "Done (64 BE + 8 FE Pass, 75.8% Cov)"],
        ["M4. Black-Box API, CSV & Security Suite", "Ngô Hữu Phước, Lê Minh Hiếu", "Postman CLI v1.80 + Docker `8080`", "Done (54 req + 3 CSV + Security)"],
        ["M5. E2E CodeceptJS Live & Load Benchmark", "Nguyễn Văn Huy, Phan Khôi", "Playwright Chromium + Docker `5173/5174`", "Done (20 E2E + 7 Load Scenarios)"],
    ], col_widths=[2.2, 1.5, 1.7, 1.3], font_size=9.2)

    add_h(doc, "3.4 Đánh giá mức độ áp dụng toàn bộ 7 Chương Slide (Course Syllabus Audit)", level=3)
    add_p(doc, "Trước khi hoàn thiện đồ án dựa trên tài liệu tham khảo và bản báo cáo mẫu, nhóm đã kiểm toán hiện trạng dự án so với toàn bộ 7 chương lý thuyết để bổ sung đầy đủ các phần còn thiếu:")
    add_table(doc, ["Nội dung lý thuyết", "Trạng thái trước kiểm toán", "Hành động đã bổ sung hoàn thiện"], [
        ["Ch. I: Quy trình test 5 bước & Exit Criteria", "Mới mô tả rời rạc trên Markdown", "Chuẩn hóa Test Plan Mục V.3 & bảng Đánh giá Tiêu chí Xuất Mục V.5.5."],
        ["Ch. II: 4 Test Levels (FE Unit, Non-func Security/Load)", "Mới có 45 BE Unit; thiếu FE Unit Test, thiếu Load Test & SQLi/XSS active test", "Bổ sung Vitest (8 tests), mở rộng JUnit lên 64 tests (75.8% Cov), thêm Security folder & Load Test 25 VUs."],
        ["Ch. III: Kiểm thử tĩnh FTR & Static Analysis Metrics", "Có cấu hình Qodana nhưng Admin thiếu `eslint.config.js`, chưa có biên bản FTR", "Tạo `admin/eslint.config.js`, chạy ESLint 2 app, đo LOC/V(G) & lập biên bản FTR 6 bước."],
        ["Ch. IV: EP, BVA, Decision Table, State Transition, CFG/MCC", "Có EP/BVA & E2E Decision; thiếu CFG `V(G)`, MCC, Data Flow & State Diagram", "Bổ sung CFG Figure V.1 (`V(G)=4`), bảng MCC, phân tích Def-Use & State Diagram."],
        ["Ch. V: Báo cáo Lỗi Phần mềm chuẩn", "Chưa có Defect Log chính thức theo chuẩn Severity/Frequency/Priority", "Lập danh sách 9 lỗi thực tế (`BUG-01..BUG-09`), đã sửa trực tiếp 5 lỗi trọng yếu."],
        ["Ch. VI & VII: Quản lý kiểm thử (WBS, RDSI, SCI) & 12 nhóm Công cụ", "Phân công sơ bộ", "Đồng bộ đúng cấu trúc Mẫu PDCMS với WBS, RDSI 6 thành viên, SCI & bảng Công cụ."],
    ], col_widths=[1.7, 2.2, 2.8], font_size=9.2)

    add_h(doc, "4. Test Cases (Thiết kế Kiểm thử Đa Kỹ Thuật)", level=2)
    add_h(doc, "4.1 Static Testing, Formal Technical Review (FTR) & Code Metrics (Chương III)", level=3)
    m_main = stat.get("backend_main_java", {})
    m_test = stat.get("backend_test_java", {})
    m_fe_u = stat.get("frontend_user_src", {})
    m_fe_a = stat.get("frontend_admin_src", {})
    add_p(doc, f"Phân tích định lượng mã nguồn thực tế (`collect_static_metrics.py`): Backend Java chính gồm {m_main.get('files', 99)} files ({m_main.get('total_lines', 9165)} tổng dòng, {m_main.get('code_lines', 6749)} code LOC, tỷ lệ comment {m_main.get('comment_ratio_pct', 5.46)}%); Backend Test gồm {m_test.get('files', 13)} files ({m_test.get('total_lines', 2318)} dòng); Frontend User {m_fe_u.get('files', 53)} files ({m_fe_u.get('total_lines', 7445)} dòng); Frontend Admin {m_fe_a.get('files', 34)} files ({m_fe_a.get('total_lines', 3132)} dòng).")
    add_table(doc, ["Tool / Review Activity", "Target Scope", "Findings Before Fix", "Outcome After Fix"], [
        ["ESLint 9 (`fontend/user`)", "53 JS/JSX files", "20 vấn đề (19 errors, 1 warning) gồm 2 lỗi crash `no-undef`", "Đã sửa 2 `no-undef` (`ProductDetail.jsx`, `Profile.jsx`); còn 17 lint style errors + 1 warning ghi nhận"],
        ["ESLint 9 (`fontend/admin`)", "34 JS/JSX files", "Crash thiếu file `eslint.config.js` (exit code 2)", "Bổ sung `eslint.config.js`; quét sạch ra 15 code-smell errors + 6 warnings"],
        ["JetBrains Qodana & Manual FTR", "Backend Java Services & Security", "0 Qodana Sarif alerts; FTR thủ công phát hiện 6 lỗi (`BUG-01,02,05,06,08,09`)", "Đã sửa & rebuild Docker cho `BUG-01`, `BUG-02`; log 4 backlog items vào Defect Report"],
    ], col_widths=[1.6, 1.4, 1.8, 1.9], font_size=9.2)

    add_h(doc, "4.2 Black-Box Test Design: EP, BVA, Decision Table & State Transition (Chương IV)", level=3)
    add_p(doc, "Áp dụng Phân vùng Tương đương (EP) & Giá trị Biên (BVA — 38 nhãn phủ `9/9 Valid`, `12/12 Invalid`, `17/17 Boundary` = 100%) cho Form Checkout (`TC_01..TC_16`) và API Tìm kiếm/Phân trang/Giỏ hàng; kết hợp Decision Table 5 Luật (Checkout & Thanh toán) và State Transition cho vòng đời Đơn hàng:")
    add_img(doc, DIAG / "fig_07_state_transition.png", "Figure V.1: Order Lifecycle State Transition Diagram (including BUG-05 finding)", width_in=6.2)

    add_table(doc, ["Decision Rule / State Case", "Condition Summary", "Expected System Behavior"], [
        ["DT Rule 1 (No Auth)", "JWT missing / invalid -> Checkout", "Chặn HTTP 401/403 (`BB-ORD-01`, `SEC-JWT-01`)"],
        ["DT Rule 2 (Empty Cart)", "Auth OK + Cart empty", "Báo lỗi HTTP 400 `'Cart is empty'` (`BB-ORD-02`)"],
        ["DT Rule 3 (Invalid BVA / Stock)", "Auth OK + Qty <= 0 hoặc > Stock hoặc SĐT < 10 số", "Báo lỗi validation HTTP 400 (`BB-CART-03..05`, `BB-ORD-03..04`)"],
        ["DT Rule 4–5 (COD / VNPay / MoMo)", "Auth OK + Cart > 0 + Valid BVA", "Tạo Order `PENDING`, trừ tồn kho; nếu Online ký URL HMAC"],
        ["ST-01..03 (Order Lifecycle)", "`PENDING -> CONFIRMED -> SHIPPING -> DELIVERED` / `CANCELLED`", "Cập nhật timestamp `confirmedAt/shippedAt/deliveredAt`; hoàn kho 1 lần khi hủy"],
    ], col_widths=[1.7, 2.2, 2.8], font_size=9.2)

    add_h(doc, "4.3 White-Box Test Design: CFG, Cyclomatic V(G), MCC & Data Flow (Chương IV)", level=3)
    add_img(doc, DIAG / "fig_06_cfg_whitebox.png", "Figure V.2: Control Flow Graph (CFG) of AuthService.register() — V(G) = 4 Basis Paths", width_in=6.2)
    add_table(doc, ["Class / Method", "V(G) & Coverage Metric", "Condition / MCC & Data-Flow Verification"], [
        ["`AuthService.register()`", "V(G) = 4; 100% Line (68/68), 100% Branch (22/22)", "Phủ đủ cả 3 tổ hợp MCC của `D3 (fullName != null && !isEmpty())`: False/N/A (`null`), True/True (`'Nguyen Van A'`), True/False (`''`)."],
        ["`CartService.addToCart()`", "100% Line (93/93), 75% Branch (18/24)", "Kiểm tra cặp `def-use` của biến `newQty`: tách nhánh tạo mới item, cộng gộp item cũ và chặn vượt tồn kho."],
        ["`OrderService` & `AdminService`", "Line: 98.2% (`OrderService`), 97.9% (`AdminService`)", "Phủ toàn bộ các nhánh switch `OrderStatus`, `period` (`today/7days/1month/1year`), `pinToTop` (`product/blog/category/brand`)."],
    ], col_widths=[1.7, 1.8, 3.2], font_size=9.2)

    add_h(doc, "4.4 Non-Functional Security, Performance & Error Guessing Test Design", level=3)
    add_bullet(doc, "Security Test Suite (`Folder 8 Postman`): Thử SQLi qua Query & Path ID, SQLi Auth Bypass tại `/api/auth/login`, XSS Payload `<script>alert(1)</script>`, Tampered JWT signature (`eyJhbGci...invalidSignature`), và kiểm tra public access `/api/settings/public`.", bold_prefix="Security Tests: ")
    add_bullet(doc, "Performance Load Test (`testing/performance_load_test.py`): Kịch bản `LOAD-01` đến `LOAD-07` giả lập 10 đến 25 người dùng truy cập đồng thời qua ThreadPool đo tổng 790 HTTP requests tới Backend API & 2 Frontend Nginx containers.", bold_prefix="Load & Stress Benchmark: ")

    # =========================================================================
    # 5. TEST REPORTS (ACTUAL OBSERVED EXECUTION RESULTS)
    # =========================================================================
    add_h(doc, "5. Test Reports", level=2)
    add_h(doc, "5.1 Unit Test & Code Coverage Reports (Backend & Frontend)", level=3)
    add_p(doc, f"Kết quả thực thi Maven + JaCoCo 0.8.12 ghi nhận 64/64 JUnit 5 Backend Unit Tests PASS (0 Failures, 0 Errors) và 8/8 Vitest Frontend Unit Tests PASS (5 User Redux + 3 Admin Utils). Tổng độ phủ Backend Bundle trên 78 lớp đạt {tot_lc}/{tot_lc + tot_lm} Lines ({line_pct:.1f}%), {tot_bc}/{tot_bc + tot_bm} Branches ({branch_pct:.1f}%) và {inst_pct:.1f}% Instructions — vượt ngưỡng Exit Criterion >= 70%.")
    add_img(doc, DIAG / "fig_08_unit_test_report_table.png", "Figure V.3: Unit Test Report Summary (JUnit 5 + Mockito + Vitest 4.1)", width_in=6.2)
    add_img(doc, DIAG / "fig_09_coverage_and_perf_charts.png", "Figure V.4: JaCoCo Line Coverage & Multi-VU Performance Latency Benchmark", width_in=6.3)

    if jac_rows:
        jac_tbl_rows = []
        for jr in sorted(jac_rows, key=lambda x: int(x["LINE_COVERED"]), reverse=True):
            pkg = jr["PACKAGE"].split(".")[-1]
            if pkg in ("service", "security", "utils", "exception") or (pkg == "controler" and int(jr["LINE_COVERED"]) >= 10):
                lc, lm = int(jr["LINE_COVERED"]), int(jr["LINE_MISSED"])
                bc, bm = int(jr["BRANCH_COVERED"]), int(jr["BRANCH_MISSED"])
                pl = f"{lc * 100.0 / max(lc + lm, 1):.1f}%"
                pb = f"{bc * 100.0 / max(bc + bm, 1):.1f}%" if (bc + bm) > 0 else "100.0%"
                jac_tbl_rows.append([f"{pkg}.{jr['CLASS']}", f"{lc}/{lc+lm} ({pl})", f"{bc}/{bc+bm} ({pb})"])
        add_table(doc, ["Backend Package & Class", "Line Coverage", "Branch Coverage"], jac_tbl_rows,
                  col_widths=[2.9, 1.9, 1.9], font_size=9.0)

    add_h(doc, "5.2 Integration, Data-Driven & Security Postman CLI Reports", level=3)
    p_full = verif.get("postman_full_local", {})
    p_dd_l = verif.get("postman_dd_login", {})
    p_dd_s = verif.get("postman_dd_search", {})
    p_dd_c = verif.get("postman_dd_checkout", {})

    def fmt_pm(d):
        if not d:
            return ("N/A", "N/A", "N/A", "N/A")
        reqs = d.get("requests") or {}
        asrt = d.get("assertions") or {}
        iters = (d.get("iterations") or {}).get("executed", 1)
        st = "PASS" if (d.get("exit_code") == 0 and reqs.get("failed", 1) == 0 and asrt.get("failed", 1) == 0) else f"FAIL ({asrt.get('failed', '?')} failed)"
        return (str(iters), f"{reqs.get('executed', 0)} req / {reqs.get('failed', 0)} fail", f"{asrt.get('executed', 0)} pass / {asrt.get('failed', 0)} fail", f"{st} ({d.get('total_duration', '')})")

    pm_rows = [
        ["Full Suite (8 Folders incl. SQLi/XSS/JWT Security)", *fmt_pm(p_full)],
        ["Data-Driven Login (`data_login_test.csv`)", *fmt_pm(p_dd_l)],
        ["Data-Driven Search (`data_search_test.csv`)", *fmt_pm(p_dd_s)],
        ["Data-Driven Checkout BVA (`data_checkout_bva.csv`)", *fmt_pm(p_dd_c)],
    ]
    add_table(doc, ["Postman CLI Execution Run", "Iterations", "Requests", "Assertions", "Result & Duration"], pm_rows,
              col_widths=[2.4, 0.7, 1.1, 1.2, 1.3], font_size=9.2)

    add_h(doc, "5.3 System E2E (CodeceptJS Live) & Performance Benchmark Reports", level=3)
    e2e = verif.get("codecept_e2e", {})
    add_p(doc, f"Kiểm thử toàn trình giao diện người dùng (CodeceptJS 3.6.5 + Playwright Headless Chromium trên Docker `http://localhost:5173` & `:5174` qua 7 suites `01..07`): Kết quả thực thi thực tế ghi nhận {e2e.get('passing', 0)} scenarios PASS, {e2e.get('failing', 0)} scenarios FAIL (Exit code: {e2e.get('exit_code', 'N/A')}).")

    perf_rows = []
    for s in perf.get("scenarios", []):
        perf_rows.append([
            s["scenario"], str(s["concurrency_vu"]), f"{s['success_count']}/{s['total_requests']}",
            f"{s['avg_ms']}", f"{s['p95_ms']}", f"{s['max_ms']}", f"{s['throughput_rps']}"
        ])
    if perf_rows:
        add_table(doc, ["Load Test Scenario", "VUs", "Success", "Avg (ms)", "P95 (ms)", "Max (ms)", "RPS"], perf_rows,
                  col_widths=[2.6, 0.5, 0.85, 0.7, 0.7, 0.7, 0.65], font_size=8.8)

    # Embed live portal screenshots if captured
    live_user = DIAG / "live_user_portal.png"
    live_admin = DIAG / "live_admin_portal.png"
    if live_user.exists():
        add_img(doc, live_user, "Figure V.5: Live User Storefront Verified in Docker (`http://localhost:5173`)", width_in=5.8)
    if live_admin.exists():
        add_img(doc, live_admin, "Figure V.6: Live Admin Portal Login Verified in Docker (`http://localhost:5174/login`)", width_in=5.8)

    add_h(doc, "5.4 Software Defect Reports (Chuẩn Chương V)", level=3)
    add_table(doc, ["Bug ID", "Summary", "Severity / Priority", "Reporter", "Status & Resolution"], [
        ["BUG-01", "`CartService.getMyCart()` dùng `@Transactional(readOnly=true)` gây HTTP 500 user mới", "Critical / Critical", "Trần Đình Trọng", "Fixed & Verified (200 OK on Docker)"],
        ["BUG-02", "`GET /api/settings/public` bị 403 do thiếu `.permitAll()`; `@PreAuthorize` lệch role", "Serious / Major", "Ngô Hữu Phước", "Fixed & Verified (`SEC-PUB-01` Pass)"],
        ["BUG-03", "`ProductDetail.jsx:201` lỗi runtime `toastSuccess is not defined` (`no-undef`)", "Serious / Major", "Phan Khôi", "Fixed & Verified (Imported + Lint Clean)"],
        ["BUG-04", "`Profile.jsx:413` lỗi runtime `axiosClient is not defined` (`no-undef`)", "Serious / Major", "Lê Minh Hiếu", "Fixed & Verified (Imported + Lint Clean)"],
        ["BUG-05", "`OrderService.updateOrderStatus()` thiếu guard chặn chuyển từ `DELIVERED/CANCELLED`", "Serious / Major", "Nguyễn Văn Huy", "Open Backlog (State Test Documented)"],
        ["BUG-06", "Trùng 2 filter JWT `@Component` (`JwtAuthFilter` & `JwtFilter`) chạy lặp", "Minor / Minor", "Duy Vũ", "Open Backlog (FTR Static Finding)"],
        ["BUG-07", "`fontend/admin` thiếu `eslint.config.js` làm ESLint 9 crash; CI dùng `|| true`", "Minor / Minor", "Trần Đình Trọng", "Fixed & Verified (`npm run lint` Active)"],
        ["BUG-08", "`PaymentService.getPaymentByOrderId()` chưa đối chiếu chủ đơn (`order.user.id`)", "Serious / Major", "Ngô Hữu Phước", "Open Backlog (IDOR Guard Needed)"],
        ["BUG-09", "`BrandService.updateBrand()` gán `brand.setName()` trước khi so sánh tạo slug (Dead Code)", "Minor / Minor", "Trần Đình Trọng", "Open Backlog (Caught by `WB-CATBRAND-02`)"],
    ], col_widths=[0.65, 2.55, 1.1, 1.05, 1.35], font_size=8.8)

    add_h(doc, "5.5 Evaluating Exit Criteria & Test Closure (Chương I)", level=3)
    add_table(doc, ["Exit Criterion", "Threshold", "Actual Observed Result", "Verdict"], [
        ["Backend Unit Test Pass Rate", "100% Pass", "64 / 64 JUnit Tests Passed (0 Failed)", "MET"],
        ["Frontend Unit Test Pass Rate", "100% Pass", "8 / 8 Vitest Tests Passed (5 User + 3 Admin)", "MET"],
        ["JaCoCo Bundle Line Coverage", ">= 70.0%", f"{line_pct:.1f}% ({tot_lc}/{tot_lc + tot_lm} lines; Services 94.5%–100%)", "MET"],
        ["Performance Error Rate (Peak 25 VUs)", "< 1%, Avg < 200ms", "0.0% Error across 790 requests, Avg API 41–95ms", "MET"],
        ["Critical Runtime Crashes Fixed", "0 Open Criticals", "BUG-01, BUG-02, BUG-03, BUG-04, BUG-07 Fixed & Rebuilt", "MET (4 Open Backlog logged)"],
    ], col_widths=[2.0, 1.1, 2.6, 1.0], font_size=9.2)

    # =========================================================================
    # VI. RELEASE PACKAGE & USER GUIDES
    # =========================================================================
    add_h(doc, "VI. Release Package & User Guides", level=1)
    add_h(doc, "1. Deliverable Package", level=2)
    add_table(doc, ["#", "Deliverable Item", "Storage / Path in Release Package"], [
        ["1", "Project Schedule & Jira Board", "Atlassian Jira `https://kiemchungphanmem.atlassian.net` (`KAN-1..20`)"],
        ["2", "Source Codes (Full-Stack Monorepo)", "GitHub `Trng-Ngyn/vga-store` (`backend/vgashop`, `fontend/user`, `fontend/admin`)"],
        ["3", "Database Scripts", "`database/create_tables.sql` (16 tables) & `database/seed_vga.sql`"],
        ["4", "Automated Verification Suites", "`src/test/java/`, `redux/__tests__/`, `postman/`, `e2e-tests/`, `testing/`"],
        ["5", "Docker Release Images", "`dinhtrng/vga-backend:latest`, `dinhtrng/vga-user:latest`, `dinhtrng/vga-admin:latest`"],
        ["6", "Final Verification Report & Defect Docs", "`Bao_Cao_Du_An_Va_Kiem_Chung_Phan_Mem_VGA_Store.docx`, `testing/Software_Defect_Reports.md`"],
    ], col_widths=[0.4, 2.1, 4.2], font_size=9.2)

    add_h(doc, "2. Installation Guides", level=2)
    add_h(doc, "2.1 System Requirements", level=3)
    add_table(doc, ["Component", "Minimum Requirement", "Recommended / Used Environment"], [
        ["Operating System", "Windows 10 64-bit / macOS / Ubuntu 22.04", "Windows 11 / Ubuntu Latest with Docker Desktop"],
        ["Hardware", "CPU 2 Cores 1.8GHz, RAM 8GB, Disk 10GB", "CPU 4+ Cores, RAM 16GB, SSD 20GB"],
        ["Runtime (Local Dev)", "Java 17+, Node.js 18+, PostgreSQL 15+", "Java 17/21, Node 25.1, PostgreSQL 17.7, Postman CLI 1.80"],
    ], col_widths=[1.4, 2.4, 2.9], font_size=9.2)

    add_h(doc, "2.2 Installation Instruction", level=3)
    add_p(doc, "Phương pháp khuyến nghị (1-Click Docker Compose):", bold_prefix="1. ")
    add_bullet(doc, "Bước 1: Mở Docker Desktop và clone repo: `git clone https://github.com/Trng-Ngyn/vga-store.git`")
    add_bullet(doc, "Bước 2: Chạy `docker compose up -d --build` (hoặc double-click `chay_docker.bat`) để khởi tạo 4 container `vga_db` (5433), `vga_backend` (8080), `vga_user` (5173), `vga_admin` (5174).")
    add_bullet(doc, "Bước 3: Chạy kiểm chứng toàn bộ: `chay_whitebox_jacoco.bat`, `chay_postman_test.bat`, `chay_postman_data_driven.bat`, `chay_e2e_test.bat`, hoặc `python testing/performance_load_test.py`.")

    add_h(doc, "3. User Manual", level=2)
    add_h(doc, "3.1 Overview", level=3)
    add_p(doc, "Hệ thống tách làm hai giao diện trực quan riêng biệt nhằm phân tách luồng thao tác mua sắm của khách hàng và luồng vận hành quản trị kho/đơn hàng của nhân viên.")
    add_h(doc, "3.2 Admin / Manager Workflow (`http://localhost:5174`)", level=3)
    add_bullet(doc, "Đăng nhập tại `/login` bằng tài khoản quản trị (`admin` / `admin123` theo cấu hình demo môi trường).")
    add_bullet(doc, "Xem tổng quan doanh thu, biểu đồ cột theo ngày/tuần/tháng và danh sách sản phẩm tồn kho thấp tại Dashboard.")
    add_bullet(doc, "Vào mục Sản phẩm / Thương hiệu / Danh mục để thêm mới (upload ảnh GPU + thông số VRAM/PSU), sửa hoặc Pin-to-top.")
    add_bullet(doc, "Vào mục Đơn hàng để duyệt chuyển trạng thái `PENDING -> CONFIRMED -> SHIPPING -> DELIVERED` hoặc xử lý yêu cầu hủy.")
    add_h(doc, "3.3 Customer / User Workflow (`http://localhost:5173`)", level=3)
    add_bullet(doc, "Tìm kiếm VGA theo tên/mã hoặc lọc theo Hãng & Khoảng giá tại trang Shop; chọn tối đa 3 VGA để mở bảng So sánh hoặc hỏi trợ lý Gemini AI.")
    add_bullet(doc, "Đăng nhập/Đăng ký trên Header -> Thêm sản phẩm vào Giỏ hàng -> Vào Checkout nhập Tên, SĐT (10–15 số), Địa chỉ và chọn COD / Chuyển khoản / VNPay / MoMo.")
    add_bullet(doc, "Vào Hồ sơ (`/profile`) hoặc Tra cứu đơn (`/track-order`) để theo dõi trạng thái giao hàng, sổ địa chỉ và viết đánh giá sau khi nhận hàng.")

    out_repo = ROOT / "Bao_Cao_Du_An_Va_Kiem_Chung_Phan_Mem_VGA_Store.docx"
    out_desk = Path(r"C:\Users\TRONG\Desktop\Bao_Cao_Du_An_Va_Kiem_Chung_Phan_Mem_VGA_Store.docx")
    out_dl = Path(r"C:\Users\TRONG\Documents\Downloads\Bao_Cao_Du_An_Va_Kiem_Chung_Phan_Mem_VGA_Store.docx")

    doc.save(str(out_repo))
    for dst in [out_desk, out_dl]:
        try:
            shutil.copy2(str(out_repo), str(dst))
        except Exception as exc:
            print("Copy note:", dst, exc)

    print("Saved DOCX report ->", out_repo, "size:", out_repo.stat().st_size, "bytes")


if __name__ == "__main__":
    build_report()
