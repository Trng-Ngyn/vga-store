import json
import os
import re
import subprocess
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "testing" / "verification_results.json"
DIAG = ROOT / "testing" / "diagrams"


def strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s or "")


def run_cmd(cmd, cwd=None, env=None):
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    proc = subprocess.run(cmd, cwd=cwd or ROOT, env=merged_env, capture_output=True, text=True, encoding="utf-8", errors="replace", shell=True)
    return proc.returncode, strip_ansi(proc.stdout + "\n" + proc.stderr)


def parse_postman_table(output: str):
    def grab(metric):
        m = re.search(rf"[│|]\s*{metric}\s*[│|]\s*(\d+)\s*[│|]\s*(\d+)\s*[│|]", output)
        if m:
            return {"executed": int(m.group(1)), "failed": int(m.group(2))}
        return None

    run_url_m = re.search(r"https://go\.postman\.co/workspace/[^\s]+", output)
    dur_m = re.search(r"total run duration:\s*([^\n\r│|]+)", output)
    return {
        "iterations": grab("iterations"),
        "requests": grab("requests"),
        "test_scripts": grab("test-scripts"),
        "assertions": grab("assertions"),
        "total_duration": dur_m.group(1).strip() if dur_m else "",
        "cloud_run_url": run_url_m.group(0).strip() if run_url_m else "",
    }


def fetch_fresh_jwt(username: str, password: str) -> str:
    req = urllib.request.Request(
        "http://localhost:8080/api/auth/login",
        data=json.dumps({"username": username, "password": password}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8")).get("token", "")


def capture_live_screenshots():
    DIAG.mkdir(parents=True, exist_ok=True)
    rc, out = run_cmd('node ..\\testing\\capture_screenshots.js', cwd=ROOT / "e2e-tests")
    print("Screenshots exit:", rc, out.strip())


def main():
    results = {}

    # 1. Local Postman CLI Full Collection (54 requests across 8 folders)
    print("Running Postman CLI Full Suite (local collection, 8 folders)...")
    rc1, out1 = run_cmd('postman collection run "postman\\VGA_Store.postman_collection.json" -e "postman\\VGA_Store.postman_environment.json"')
    results["postman_full_local"] = {"exit_code": rc1, **parse_postman_table(out1)}
    print("  -> Exit:", rc1, results["postman_full_local"])

    # 2. Data-Driven CSV Login Run
    print("Running Postman CLI Data-Driven Login CSV (6 iterations)...")
    rc2, out2 = run_cmd('postman collection run "postman\\VGA_Store.postman_collection.json" -e "postman\\VGA_Store.postman_environment.json" -i "1. Authentication & Security (EP / BVA / RBAC)" -d "postman\\data_login_test.csv"')
    results["postman_dd_login"] = {"exit_code": rc2, **parse_postman_table(out2)}
    print("  -> Exit:", rc2, results["postman_dd_login"])

    # 3. Data-Driven CSV Search Run
    print("Running Postman CLI Data-Driven Search CSV (5 iterations)...")
    rc3, out3 = run_cmd('postman collection run "postman\\VGA_Store.postman_collection.json" -e "postman\\VGA_Store.postman_environment.json" -i "4. Products (EP, BVA Phân trang, Tìm kiếm & Lọc giá)" -d "postman\\data_search_test.csv"')
    results["postman_dd_search"] = {"exit_code": rc3, **parse_postman_table(out3)}
    print("  -> Exit:", rc3, results["postman_dd_search"])

    # 4. Data-Driven CSV Checkout BVA Run (with fresh JWT for authenticated endpoints)
    print("Running Postman CLI Data-Driven Checkout BVA CSV (6 iterations)...")
    tok = fetch_fresh_jwt("demotester", "123456")
    rc4, out4 = run_cmd(f'postman collection run "postman\\VGA_Store.postman_collection.json" -e "postman\\VGA_Store.postman_environment.json" -i "6. Orders (Đặt hàng - EP, BVA Checkout & State Transition)" -d "postman\\data_checkout_bva.csv" --env-var "jwtToken={tok}"')
    results["postman_dd_checkout"] = {"exit_code": rc4, **parse_postman_table(out4)}
    print("  -> Exit:", rc4, results["postman_dd_checkout"])

    # 5. Live CodeceptJS E2E Suite (7 suites, 20 tests against Docker http://localhost:5173 & 5174)
    print("Running CodeceptJS Live E2E Suite (Headless Chromium)...")
    rc5, out5 = run_cmd('npx codeceptjs run --steps', cwd=ROOT / "e2e-tests", env={"HEADLESS": "true"})
    ok_m = re.search(r"OK\s*\|\s*(\d+)\s+passed", out5)
    fail_m = re.search(r"FAIL\s*\|\s*(\d+)\s+passed,\s*(\d+)\s+failed", out5)
    if ok_m:
        passing, failing = int(ok_m.group(1)), 0
    elif fail_m:
        passing, failing = int(fail_m.group(1)), int(fail_m.group(2))
    else:
        passing, failing = 0, 0
    results["codecept_e2e"] = {
        "exit_code": rc5,
        "passing": passing,
        "failing": failing,
        "tail": "\n".join(out5.strip().splitlines()[-30:]),
    }
    print("  -> Exit:", rc5, "Passing:", passing, "Failing:", failing)

    capture_live_screenshots()
    OUT_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print("Saved ->", OUT_JSON)


if __name__ == "__main__":
    main()
