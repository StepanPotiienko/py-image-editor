import logging


class Logger:
    def __init__(self, prefix="log"):
        self.prefix = prefix
        logging.basicConfig(
            level=logging.DEBUG,
            format=(
                "%(filename)s: "
                "%(levelname)s: "
                "%(funcName)s(): "
                "%(lineno)d:\t"
                "%(message)s"
            ),
        )
        with open("log.txt", "w") as file:
            file.write("")

    def append_to_log(self, data):
        with open("log.txt", "a") as file:
            file.write(data)

    def error(self, data):
        logging.error(f"{self.prefix}: {data}")
        self.append_to_log(f"{self.prefix}: {data}\n")

    def warning(self, data):
        logging.warning(f"{self.prefix}: {data}")
        self.append_to_log(f"{self.prefix}: {data}\n")

    def info(self, data):
        logging.info(f"{self.prefix}: {data}")
        self.append_to_log(f"{self.prefix}: {data}\n")
