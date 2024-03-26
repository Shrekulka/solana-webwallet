# solana_wallet_telegram_bot/logger_config.py

import logging
import traceback

from colorama import Style, Fore, Back, init


class CustomLogger:
    """
        Configures the logging system.

        Attributes:
            level (int): The logging level.
            filemode (str): The mode of writing logs to a file.
            log_to_file (bool): Flag for logging to a file.
    """

    def __init__(self, level: int = logging.DEBUG, filemode: str = 'a', log_to_file: bool = False) -> None:
        """
            Initializes CustomLogger with the specified logging level, file mode, and logging to file option.

            Args:
                level (int): The logging level. Defaults to logging.DEBUG.
                filemode (str): The mode of writing logs to a file. Defaults to 'a' (append).
                log_to_file (bool): The option for logging to a file. Defaults to False.

            Raises:
                ValueError: If the specified logging level is invalid.
        """
        # Проверяем, что уровень логирования, установленный пользователем, является допустимым.
        if level not in [logging.NOTSET, logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL]:
            raise ValueError("Invalid logging level. It must be one of: logging.NOTSET, logging.DEBUG, "
                             "logging.INFO, logging.WARNING, logging.ERROR, logging.CRITICAL")

        self.level = level  # Устанавливает уровень логирования для объекта CustomLogger.
        self.filemode = filemode  # Определяет режим записи логов в файл (добавление или перезапись).
        self.log_to_file = log_to_file  # Определяет, будет ли выполняться логирование в файл.

        # Базовый формат логов
        self.basic_log_format = (
            # Форматирует время записи лога с меткой времени в малиновый цвет.
            f'{Fore.MAGENTA}%(asctime)s{Style.RESET_ALL} | '
            # Добавляет номер строки и уровень логирования с соответствующим цветом.
            f'{Back.GREEN + Style.BRIGHT + Fore.BLACK}%(lineno)04d-%(levelname)-7s{Style.RESET_ALL} | - | '
            # Выводит имя файла, где произошло логирование, в светло-голубом цвете.
            f'{Fore.LIGHTCYAN_EX}%(filename)-20s{Style.RESET_ALL} | - | '
            # Выводит имя логируемого объекта в синем цвете (имя файла).
            f'{Fore.BLUE}%(name)-20s{Style.RESET_ALL} | - | '
            # Выводит имя функции, откуда был вызван логированный объект, в зеленом цвете.
            f'{Fore.GREEN}%(funcName)-20s{Style.RESET_ALL} | - | '
            # Выводит сообщение лога в ярко-голубом цвете.
            f'{Style.BRIGHT + Fore.CYAN}%(message)s{Style.RESET_ALL} |')

        # Формат логов предупреждений
        self.warning_log_format = (
            # Форматирует время записи лога в желтый фон с черным шрифтом.
            f'{Back.YELLOW + Style.BRIGHT + Fore.BLACK}%(asctime)s{Style.RESET_ALL} | '
            # Добавляет номер строки и уровень логирования с желтым фоном и черным шрифтом.
            f'{Back.YELLOW + Style.BRIGHT + Fore.BLACK}%(lineno)04d-%(levelname)-7s{Style.RESET_ALL} | - | '
            # Выводит имя файла с желтым фоном и черным шрифтом.
            f'{Back.YELLOW + Style.BRIGHT + Fore.BLACK}%(filename)-20s{Style.RESET_ALL} | - | '
            # Выводит имя объекта с желтым фоном и черным шрифтом.
            f'{Back.YELLOW + Style.BRIGHT + Fore.BLACK}%(name)-20s{Style.RESET_ALL} | - | '
            # Выводит имя функции с желтым фоном и черным шрифтом.
            f'{Back.YELLOW + Style.BRIGHT + Fore.BLACK}%(funcName)-20s{Style.RESET_ALL} | - | '
            # Выводит сообщение лога с желтым фоном и черным шрифтом.
            f'{Back.YELLOW + Style.BRIGHT + Fore.BLACK}%(message)s{Style.RESET_ALL} |')

        # Формат логов ошибок
        self.error_log_format = (
            # Форматирует время записи лога в фиолетовый цвет с черным шрифтом.
            f'{Back.MAGENTA + Style.BRIGHT + Fore.BLACK}%(asctime)s{Style.RESET_ALL} | '
            # Добавляет номер строки и уровень логирования с соответствующим цветом и черным шрифтом.
            f'{Back.MAGENTA + Style.BRIGHT + Fore.BLACK}%(lineno)04d-%(levelname)-7s{Style.RESET_ALL} | - | '
            # Выводит имя файла, где произошло логирование, в фиолетовом цвете и черным шрифтом.
            f'{Back.MAGENTA + Style.BRIGHT + Fore.BLACK}%(filename)-20s{Style.RESET_ALL} | - | '
            # Выводит имя логируемого объекта в фиолетовом цвете и черным шрифтом.
            f'{Back.MAGENTA + Style.BRIGHT + Fore.BLACK}%(name)-20s{Style.RESET_ALL} | - | '
            # Выводит имя функции, откуда был вызван логированный объект, в фиолетовом цвете и черным шрифтом.
            f'{Back.MAGENTA + Style.BRIGHT + Fore.BLACK}%(funcName)-20s{Style.RESET_ALL} | - | '
            # Выводит сообщение лога в фиолетовом цвете и черным шрифтом.
            f'{Back.MAGENTA + Style.BRIGHT + Fore.BLACK}%(message)s{Style.RESET_ALL} |')

        # Формат критических логов
        self.critical_log_format = (
            # Форматирует время записи лога в красный цвет с черным шрифтом.
            f'{Back.RED + Style.BRIGHT + Fore.BLACK}%(asctime)s{Style.RESET_ALL} | '
            # Добавляет номер строки и уровень логирования с соответствующим цветом и черным шрифтом.
            f'{Back.RED + Style.BRIGHT + Fore.BLACK}%(lineno)04d-%(levelname)-7s{Style.RESET_ALL} | - | '
            # Выводит имя логируемого объекта в красном цвете и черным шрифтом.
            f'{Back.RED + Style.BRIGHT + Fore.BLACK}%(name)s{Style.RESET_ALL} | - | '
            # Выводит имя функции, откуда был вызван логированный объект, в красном цвете и черным шрифтом.
            f'{Back.RED + Style.BRIGHT + Fore.BLACK}%(funcName)s{Style.RESET_ALL} | - | '
            # Выводит сообщение лога в красном цвете и черным шрифтом.
            f'{Back.RED + Style.BRIGHT + Fore.BLACK}%(message)s{Style.RESET_ALL} |')

    def configure_logging(self) -> None:
        """
            Configures the logging system.

            This method configures the logging system by initializing necessary components such as the base logger,
            handlers, and formatters.
            If an exception occurs during configuration, it is handled, and the program exits with a SystemExit code.

            Raises:
                SystemExit: If there is an error during logging configuration. The program exits with code 1.
        """

        try:
            # Инициализация цветов в консоли
            init(autoreset=True)

            # Настройка базового логгера
            logging.basicConfig(filename='val.log' if self.log_to_file else None,
                                format=self.basic_log_format, filemode=self.filemode, level=self.level)
            # Очистка существующих обработчиков базового логгера
            logging.getLogger().handlers = []

            # Создает обработчик для вывода логов в консоль.
            console_handler = logging.StreamHandler()
            # Устанавливает уровень логирования обработчика в соответствии с уровнем, указанным пользователем.
            console_handler.setLevel(self.level)

            # Создает форматтер для форматирования логов перед выводом в консоль.
            console_formatter = logging.Formatter(self.basic_log_format)
            # Назначает созданный форматтер обработчику для логирования в консоль.
            console_handler.setFormatter(console_formatter)

            # Добавление цветов для ошибок и предупреждений
            class ColoredFormatter(logging.Formatter):
                """
                    Formatter for adding color to logs.

                    Attributes:
                        COLORS (dict): Dictionary of colors for different logging levels.

                    Methods:
                        __init__(self, log_formats: dict)
                            Initializes ColoredFormatter.

                        format(self, record: LogRecord) -> str:
                            Formats the log with color.

                            Args:
                                record (logging.LogRecord): The log record.

                            Returns:
                                str: The formatted log message with applied color.
                """
                # Коды цвета
                COLORS: dict = {
                    logging.WARNING: Back.YELLOW + Style.BRIGHT,  # Желтый цвет для предупреждений с ярким стилем.
                    logging.ERROR: Back.MAGENTA + Style.BRIGHT,  # Фиолетовый цвет для ошибок с ярким стилем.
                    logging.CRITICAL: Back.RED + Style.BRIGHT  # Красный цвет для критических ошибок с ярким стилем.
                }

                def __init__(self, log_formats: dict) -> None:
                    """
                        Initializes ColoredFormatter.

                        Args:
                            log_formats (dict): Dictionary of log formats for different levels.
                    """
                    # Устанавливает форматы логов для объекта ColoredFormatter.
                    self.log_formats = log_formats
                    # Вызывает конструктор родительского класса (logging.Formatter) для инициализации объекта
                    # ColoredFormatter.
                    super().__init__()

                def format(self, record: logging.LogRecord) -> str:
                    """
                        Formats the log with color.

                        Args:
                            record (logging.LogRecord): The log record.

                        Returns:
                            str: The formatted log message with applied color.
                    """
                    # Получает формат логов для указанного уровня записи.
                    log_format = self.log_formats.get(record.levelno)
                    # Проверяет, есть ли цвет для указанного уровня логирования.
                    if record.levelno in self.COLORS:
                        # Применяет соответствующий цвет к сообщению лога.
                        record.msg = self.COLORS[record.levelno] + record.msg + Style.RESET_ALL
                    # Форматирует запись лога с использованием полученного формата.
                    return logging.Formatter(log_format).format(record)

            # Создает экземпляр ColoredFormatter с определенными форматами для различных уровней логирования.
            console_formatter = ColoredFormatter({
                logging.NOTSET: self.basic_log_format,
                logging.DEBUG: self.basic_log_format,
                logging.INFO: self.basic_log_format,
                logging.WARNING: self.warning_log_format,
                logging.ERROR: self.error_log_format,
                logging.CRITICAL: self.critical_log_format
            })

            # Установка форматтера для консоли
            console_handler.setFormatter(console_formatter)

            # Добавление обработчика к базовому логгеру
            logging.getLogger().addHandler(console_handler)
        except Exception as e:
            # Логирование ошибки и завершение программы в случае ошибки конфигурации логирования
            detailed_error_traceback = traceback.format_exc()
            logging.error(f"Logging configuration error: {e}\n{detailed_error_traceback}")
            raise SystemExit(1)

    @staticmethod
    def log(level: int, message: str) -> None:
        """
            Logs a message with the specified level.

            Args:
                level (int): The logging level.
                message (str): The message to log.
        """
        logging.log(level, message)

    @staticmethod
    def debug(*args) -> None:
        """
            Logs a debug message.

            Args:
                *args: The messages to log as format string and values.
        """
        message = " ".join(str(x) for x in args)
        logging.debug(f"{message}")

    @staticmethod
    def info(*args) -> None:
        """
            Logs an informational message.

            Args:
                *args: The messages to log as format string and values.
        """
        message = " ".join(str(x) for x in args)
        logging.info(f"{message}")

    @staticmethod
    def warning(*args) -> None:
        """
            Logs a warning message.

            Args:
                *args: The messages to log as format string and values.
        """
        message = " ".join(str(x) for x in args)
        logging.warning(f"{message}")

    @staticmethod
    def error(*args) -> None:
        """
            Logs an error message.

            Args:
                *args: The messages to log as format string and values.
        """
        message = " ".join(str(x) for x in args)
        logging.error(f"{message}")

    @staticmethod
    def critical(*args) -> None:
        """
            Logs a critical message.

            Args:
                *args: The messages to log as format string and values.
        """
        message = " ".join(str(x) for x in args)
        logging.critical(f"{message}")


# Создание экземпляра CustomLogger с включенным логированием в файл
logger = CustomLogger(log_to_file=False)

# Вызов метода для настройки логирования
logger.configure_logging()

# Логирование приветственного сообщения
logger.info(f"{Back.BLUE + Style.BRIGHT + Fore.BLACK}HI! HI! HI!!!{Style.RESET_ALL}")
