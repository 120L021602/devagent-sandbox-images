from playwright.sync_api import sync_playwright
import time
import os
import subprocess

def run_devagent_task():
    # print("[LOG] Fixing project directory permissions...")
    # subprocess.run(["sudo", "chmod", "-R", "777", "/home/coder/project"], check=True)
    # subprocess.run(["sudo", "chown", "-R", "coder:coder", "/home/coder/project"], check=True)
    # print("[LOG] Permissions fixed successfully")

    with sync_playwright() as p:
        user_data_dir = "/usr/chrome-persistent-data"
        os.makedirs(user_data_dir, exist_ok=True)
        os.chmod(user_data_dir, 0o777)

        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled",
                "--disable-gpu",
                "--start-maximized",
                "--disable-dev-shm-usage",
                # qemu-aarch64 模拟环境下必需：否则 chrome 多进程模型会触发 qemu SIGSEGV
                "--no-zygote",
                "--single-process",
                "--disable-crash-reporter",
                "--js-flags=--jitless",
            ],
            viewport={"width": 1920, "height": 1080}
        )

        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto("http://localhost:9000", timeout=30000)
            # time.sleep(100)
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            print("[LOG] Page loaded successfully")

            # 等待一段时间
            time.sleep(300)  

        except Exception as e:
            print(f"[ERROR] Failed：{str(e)}")
            page.screenshot(path="/home/coder/project/screenshots/task_error.png")
            with open("/home/coder/project/screenshots/page_source.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        finally:
            context.close()

if __name__ == "__main__":
    run_devagent_task()