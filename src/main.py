import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

from src.database.db import init_db
from src.chatbot.nlu import NLU
from src.chatbot.router import Router
from src.utils.logger import Logger


def main():
    init_db()
    nlu = NLU()
    router = Router()
    logger = Logger()

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

        intent, params = nlu.process(user_input)
        response = router.route(intent, params)
        logger.log(user_input, intent, params, response)

        if response == "EXIT":
            print("Довиждане!")
            break

        print(response)


if __name__ == '__main__':
    main()
