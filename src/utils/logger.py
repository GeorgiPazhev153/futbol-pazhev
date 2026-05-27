import logging


class Logger:
    def __init__(self, filename='commands.log'):
        self.filename = filename
        formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler(filename, encoding='utf-8')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger('chatbot')
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(handler)

    def log(self, raw_input, intent, params, result):
        params_preview = ', '.join(str(p) for p in params) if params else '-'
        if result == "EXIT":
            status = "OK"
            msg = "exit"
        elif result.startswith("Грешка") or "грешка" in result.lower() or result.startswith("Не разпознах"):
            status = "ERROR"
            msg = result
        else:
            status = "OK"
            msg = result.split("\n")[0] if "\n" in result else result
        self.logger.info("%s | intent=%s | params=[%s] | %s | %s", raw_input, intent, params_preview, status, msg)
