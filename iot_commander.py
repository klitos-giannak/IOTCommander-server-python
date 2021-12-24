from threading import Thread

import commands_service
import discover_service

discover_service.initialise()
discover_thread = Thread(target=discover_service.start)
commands_thread = Thread(target=commands_service.start)

discover_thread.start()
commands_thread.start()
