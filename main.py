import asyncio
import json
import os

from playwright.async_api import async_playwright


def log_error(profile_id, error_msg):
    os.makedirs("logs", exist_ok=True)
    with open("logs/bug.log", "a", encoding="utf-8") as f:
        f.write(f"profile_{profile_id} ERROR: {error_msg}\n")


async def login_if_needed(page, login, password, profile_id):
    try:
        await asyncio.sleep(0.5)
        sign_in_button = await page.query_selector('button:has-text("Sign in")')
        if sign_in_button:
            print("Кликаю по кнопке Sign in")
            await sign_in_button.click()

            choose_account_btn = await page.query_selector(
                'button[data-testid="chooseAddAccountBtn"]'
            )
            if choose_account_btn:
                print("Кликаю по кнопке выбора другого аккаунта")
                await choose_account_btn.click()

            await asyncio.sleep(0.2)

            await page.wait_for_selector('input[data-testid="loginUsernameInput"]')
            await page.wait_for_selector('input[data-testid="loginPasswordInput"]')

            await page.fill('input[data-testid="loginUsernameInput"]', login)
            await page.fill('input[data-testid="loginPasswordInput"]', password)

            await page.keyboard.press("Enter")
            await page.wait_for_load_state("networkidle")
            print("Логин прошёл")
            return
        print("Вход не требуется, уже залогинен")
    except Exception as e:
        print(f"Ошибка в login_if_needed: {e}")
        log_error(profile_id, f"login_if_needed error: {e}")


async def scroll_and_follow(page, max_follows, profile_id):
    followed = 0
    last_height = await page.evaluate("document.body.scrollHeight")
    no_change_count = 0

    while followed < max_follows:
        buttons = await page.query_selector_all('button:has-text("Follow")')
        new_buttons_found = False

        for btn in buttons:
            if followed >= max_follows:
                break
            try:
                label = await btn.get_attribute("aria-label")
                if label != "Follow":
                    continue

                await btn.click()
                followed += 1
                new_buttons_found = True
                await asyncio.sleep(0.01)
            except Exception as e:
                print(f"Ошибка при клике Follow: {e}")
                log_error(profile_id, f"Follow click error: {e}")

        try:
            await page.evaluate("window.scrollBy(0, 2500)")
            await asyncio.sleep(0.02)
        except Exception as e:
            print(f"Ошибка при скролле: {e}")
            log_error(profile_id, f"Scroll error: {e}")
            break

        try:
            new_height = await page.evaluate("document.body.scrollHeight")
        except Exception as e:
            print(f"Ошибка при получении высоты страницы: {e}")
            log_error(profile_id, f"Get height error: {e}")
            break

        if new_height == last_height and not new_buttons_found:
            no_change_count += 1
            if no_change_count >= 10:
                print("Дошли до конца страницы — новых подписчиков нет")
                os.makedirs("logs", exist_ok=True)
                with open("logs/finish.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"profile_{profile_id} долистал до конца\n")
                break
        else:
            no_change_count = 0

        last_height = new_height

    print(f"Подписался всего: {followed}")


async def process_profile(playwright, profile_id, data):
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=f"profiles/profile_{profile_id}",
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ],
    )

    page = await browser.new_page()

    await page.route(
        "**/*",
        lambda route, request: asyncio.create_task(
            route.abort()
            if request.resource_type in ["image", "media", "font"]
            else route.continue_()
        ),
    )

    await page.goto(data["url"], wait_until="networkidle")

    await login_if_needed(page, data["login"], data["password"], profile_id)

    print(f"Профиль {profile_id} открыт и готов к работе (headless)")
    return browser, page


async def main():
    with open("creds.json", "r") as f:
        creds = json.load(f)

    async with async_playwright() as playwright:
        profiles = []

        for i in range(1, len(creds) + 1):
            profile_key = f"profile_{i}"
            print(f"Открываю профиль {profile_key}")
            browser, page = await process_profile(playwright, i, creds[profile_key])
            profiles.append((browser, page, i))

        print("Все профили открыты и готовы!")

        while True:
            for browser, page, profile_id in profiles:
                creds_key = f"profile_{profile_id}"
                await login_if_needed(
                    page,
                    creds[creds_key]["login"],
                    creds[creds_key]["password"],
                    profile_id,
                )

                print(f"Запускаю подписки для профиля {profile_id}")
                await scroll_and_follow(page, max_follows=1000, profile_id=profile_id)

                await asyncio.sleep(0.1)

            print("Круг подписок окончен. Тайм-аут 10 минут")
            await asyncio.sleep(600)


if __name__ == "__main__":
    asyncio.run(main())
