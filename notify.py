import asyncio
import os
import threading

import aiohttp
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

TELEGRAM_BOT_TOKEN = "Telegram_bot_token_here"  # Replace with your actual bot token
CHAT_ID = "Yout_telegram_id"


async def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with aiohttp.ClientSession() as session:
        await session.post(url, json={"chat_id": CHAT_ID, "text": text})


class LogHandler(FileSystemEventHandler):
    def __init__(self, filepath, loop):
        self.filepath = filepath
        self.loop = loop
        self.last_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0

    def on_modified(self, event):
        if event.src_path == self.filepath:
            new_size = os.path.getsize(self.filepath)
            if new_size > self.last_size:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    f.seek(self.last_size)
                    new_lines = f.read()
                self.last_size = new_size
                asyncio.run_coroutine_threadsafe(
                    send_telegram_message(
                        f"Новые логи из {os.path.basename(self.filepath)}:\n{new_lines}"
                    ),
                    self.loop,
                )


def start_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


def main():
    loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_loop, args=(loop,), daemon=True)
    t.start()

    paths_to_watch = ["logs/bug.log", "logs/finish.log"]
    for path in paths_to_watch:
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "a", encoding="utf-8").close()

    observer = Observer()
    for path in paths_to_watch:
        event_handler = LogHandler(path, loop)
        observer.schedule(
            event_handler, path=os.path.dirname(path) or ".", recursive=False
        )

    observer.start()
    print("Watcher запущен и следит за логами")

    asyncio.run_coroutine_threadsafe(
        send_telegram_message("Watcher логов запущен — программа работает!"), loop
    )

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    loop.stop()


if __name__ == "__main__":
    main()
