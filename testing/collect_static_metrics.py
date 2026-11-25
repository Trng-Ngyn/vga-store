import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def count_java_metrics(java_dir: Path):
    total_files = 0
    total_lines = 0
    code_lines = 0
    comment_lines = 0
    classes = []
    decision_kw = re.compile(r'\b(if|else\s+if|for|while|case|catch|\?\s*.*:)\b|&&|\|\|')
    method_pat = re.compile(r'^\s*(public|private|protected)\s+[\w<>?,\[\]\s]+\s+(\w+)\s*\([^)]*\)\s*(throws\s+[\w,\s]+)?\{?')

    for fp in sorted(java_dir.rglob("*.java")):
        total_files += 1
        lines = fp.read_text(encoding="utf-8", errors="ignore").splitlines()
        total_lines += len(lines)
        in_block = False
        file_code = 0
        file_cmt = 0
        for line in lines:
            s = line.strip()
            if not s:
                continue
            if in_block:
                file_cmt += 1
                if "*/" in s:
                    in_block = False
            elif s.startswith("/*"):
                file_cmt += 1
                if "*/" not in s:
                    in_block = True
            elif s.startswith("//"):
                file_cmt += 1
            else:
                file_code += 1
        code_lines += file_code
        comment_lines += file_cmt

        # Rough method cyclomatic complexity for services/security/utils
        rel = str(fp.relative_to(ROOT)).replace("\\", "/")
        if any(seg in rel for seg in ["/service/", "/security/", "/utils/"]):
            src = "\n".join(lines)
            vg_est = 1 + len(decision_kw.findall(src))
            classes.append({"file": rel, "loc": len(lines), "code_loc": file_code, "approx_file_vg": vg_est})

    return {
        "files": total_files,
        "total_lines": total_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "comment_ratio_pct": round(comment_lines * 100.0 / max(total_lines, 1), 2),
        "hotspots": sorted(classes, key=lambda x: x["approx_file_vg"], reverse=True)[:15],
    }


def count_js_metrics(src_dir: Path):
    files = 0
    total_lines = 0
    for ext in ("*.js", "*.jsx"):
        for fp in src_dir.rglob(ext):
            if "node_modules" in str(fp) or "__tests__" in str(fp):
                continue
            files += 1
            total_lines += len(fp.read_text(encoding="utf-8", errors="ignore").splitlines())
    return {"files": files, "total_lines": total_lines}


def main():
    metrics = {
        "backend_main_java": count_java_metrics(ROOT / "backend" / "vgashop" / "src" / "main" / "java"),
        "backend_test_java": count_java_metrics(ROOT / "backend" / "vgashop" / "src" / "test" / "java"),
        "frontend_user_src": count_js_metrics(ROOT / "fontend" / "user" / "src"),
        "frontend_admin_src": count_js_metrics(ROOT / "fontend" / "admin" / "src"),
        "e2e_tests_js": count_js_metrics(ROOT / "e2e-tests" / "tests"),
    }
    out = ROOT / "testing" / "static_metrics.json"
    out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
