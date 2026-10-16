from playwright.sync_api import sync_playwright
import time
import os
import subprocess


def run_devagent_task():
    print("[LOG] Fixing project directory permissions...")
    subprocess.run(["sudo", "chmod", "-R", "777", "/usr/chrome-persistent-data"], check=True)
    subprocess.run(["sudo", "chown", "-R", "ai-user:ai-group", "/usr/chrome-persistent-data"], check=True)
    print("[LOG] Permissions fixed successfully")

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
            ],
            viewport={"width": 1920, "height": 1080}
        )

        page = context.pages[0] if context.pages else context.new_page()
        try:
            page.goto("http://localhost:9000", timeout=30000)
            page.wait_for_load_state("networkidle")
            time.sleep(3)
            print("[LOG] Page loaded successfully")

            # 点击侧边栏DevAgent入口
            devagent_btn = page.locator('a[aria-label="DevAgent (Alt+J)"]')
            devagent_btn.wait_for(state="visible", timeout=15000)
            devagent_btn.click(force=True)
            time.sleep(3)
            print("[LOG] DevAgent icon clicked, sidebar expanded")

            # 嵌套两层iframe
            frame1 = page.frame_locator("iframe.webview.ready")
            print("[DEBUG] Found DevAgent iframe")
            frame2 = frame1.frame_locator("iframe#active-frame")
            print("[DEBUG] Found inner iframe inside DevAgent iframe")

            # 点击右上角设置齿轮按钮
            devagent_settings_button = frame2.locator('vscode-button >> i.codicon.codicon-settings-gear')
            devagent_settings_button.click(force=True)
            time.sleep(2)

            # 点击关于Tab
            about_button = frame2.locator('button[data-testid="tab-about"]')
            about_button.click(force=True)
            time.sleep(1)

            # ==================== 1.后端代理地址 ====================
            loc_backend = frame2.locator('vscode-text-field#backendHost >> input#control')
            loc_backend.click()
            loc_backend.press("Control+a")
            loc_backend.fill("https://新埋点地址.com")
            time.sleep(1)

            # ==================== 2.后端埋点代理地址 ====================
            loc_event_tracking = frame2.locator('vscode-text-field#portalBackendHost >> input#control')
            loc_event_tracking.click()
            loc_event_tracking.press("Control+a")
            loc_event_tracking.fill("https://abc.com")
            time.sleep(2)

            # ==================== 3.后端登录代理地址 ====================
            loc_login = frame2.locator('vscode-text-field#pluginBackendHost >> input#control')
            loc_login.click()
            loc_login.press("Control+a")
            loc_login.fill("https://abc.com")
            time.sleep(2)

            # ==================== 3.API协作平台自定义鉴权地址 ====================
            loc_api = frame2.locator('vscode-text-field#apiColBackendHost >> input#control')
            loc_api.click()
            loc_api.press("Control+a")
            loc_api.fill("https://abc.com")
            time.sleep(2)

            # ==================== 4.入库率上报地址 ====================
            loc_database_report = frame2.locator('vscode-text-field#storageRateEndpoint >> input#control')
            loc_database_report.click()
            loc_database_report.press("Control+a")
            loc_database_report.fill("https://abc.com")
            time.sleep(2)

            # ==================== 5.mcp市场鉴权地址 ====================
            loc_mcp_report = frame2.locator('vscode-text-field#apiMcpmarketEndpoint >> input#control')
            loc_mcp_report.click()
            loc_mcp_report.press("Control+a")
            loc_mcp_report.fill("https://abc.com")
            time.sleep(2)

            # 点击完成保存配置
            finish_button = frame2.locator('vscode-button:has-text("完成")')
            finish_button.click(force=True)

            time.sleep(10)

        except Exception as e:
            print(f"[ERROR] Failed: {str(e)}")
            page.screenshot(path="/home/coder/project/screenshots/task_error.png")
            with open("/home/coder/project/screenshots/page_source.html", "w", encoding="utf-8") as f:
                f.write(page.content())
        finally:
            context.close()


if __name__ == "__main__":
    run_devagent_task()