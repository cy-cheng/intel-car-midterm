import logging
from typing import Optional

from BT import Bluetooth

log = logging.getLogger(__name__)

# hint: You may design additional functions to execute the input command,
# which will be helpful when debugging :)


class BTInterface:
    def __init__(self, port: Optional[str] = None):
        log.info("Arduino Bluetooth Connect Program.")
        self.bt = Bluetooth()
        if port is None:
            port = input("PC bluetooth port name: ")
        while not self.bt.do_connect(port):
            if port == "quit":
                self.bt.disconnect()
                quit()
            port = input("PC bluetooth port name: ")

    def start(self):
        input("Press enter to start.")
        self.bt.serial_write_string("s")

    def get_UID(self):
        return self.bt.serial_read_byte()

    def send_instruction(self, instruction: str):
        self.bt.serial_write_string(instruction)
        return

    def fetch_info(self):
        return self.bt.serial_read_string()

    def end_process(self):
        self.bt.serial_write_string("Process ended by computer.")
        self.bt.disconnect()


if __name__ == "__main__":
    test = BTInterface()
    test.start()
    test.end_process()
