import logging
from config import LOG_FILE


def setup_logger():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
        ]
    )
    # Устанавливаем уровень для консольного вывода (если нужен)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(
        logging.Formatter('[%(levelname)s] %(name)s: %(message)s')
    )
    logging.getLogger().addHandler(console)


def get_logger(name):
    return logging.getLogger(name)
    
