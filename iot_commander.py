from threading import Thread

import commands_service
import discover_service

discover_service.initialise()
discover_thread = Thread(target=discover_service.start, daemon=True)
commands_thread = Thread(target=commands_service.start, daemon=True)

discover_thread.start()
commands_thread.start()

timeout = 5
while discover_thread.is_alive() and commands_thread.is_alive():
    discover_thread.join(timeout)
    commands_thread.join(timeout)

commands_service.stop()
discover_service.stop()

commands_thread.join()  # wait for commands service to shut down
discover_thread.join()  # wait for discover service to shut down
