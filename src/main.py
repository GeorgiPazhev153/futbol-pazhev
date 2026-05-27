import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from src.db import init_db
from src.chatbot import Chatbot

logging.basicConfig(
    filename='commands.log',
    level=logging.INFO,
    format='%(asctime)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)


def main():
    init_db()
    bot = Chatbot()

    print("=== Футболен клуб Chatbot ===")
    print("Напишете 'помощ' за наличните команди или 'изход' за изход.")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nДовиждане!")
            break

        if not user_input:
            continue

        response = bot.process(user_input)
        logging.info("%s | %s", user_input, response)

        if response == "EXIT":
            print("Довиждане!")
            break

        print(response)


if __name__ == '__main__':
    main()
