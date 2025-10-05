import datetime
from pathlib import Path
import random

# Submodule of GLady Core, responsible for creating and writing execution logs.
class Logger:

    def __init__(self, core):
        self.core = core

        self.dir = "../Logs/"

        Path(self.dir).mkdir(parents=True, exist_ok=True)
        self.fileName = "Log_" + datetime.datetime.now().strftime("%I_%M%p - %B_%d_%Y -- ") + str(
            random.randint(10000, 99999)) + ".txt"


    # Writes a message to the log
    # Types: 0 - Normal message, 1 - Error
    def log(self, message : str, message_type : int = 0, should_print : bool = True):

        # Adding time stamp
        now = datetime.datetime.now()
        time_str = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}.{str(now.microsecond)[:2]}"
        log_message = time_str + "   :   " + message

        # Processing message types
        if message_type == 1:
            log_message = "ERROR   :   " + log_message

        # Writing log into file
        try:
            with open(self.dir + self.fileName, 'a', encoding="utf-8") as File:
                File.write(log_message + "\n")

        except Exception as e:
            self.log("Failed to write log file: " + str(e), message_type = 1)
            pass

        # Printing log into console
        if should_print:
            print(log_message)