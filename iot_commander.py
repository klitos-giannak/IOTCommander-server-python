import commands_service
import discover_service

discover_service.initialise()
commands_service.start()

try:
    discover_service.start()
except KeyboardInterrupt:
    print("Interrupt received, stopping services")

commands_service.stop()
discover_service.stop()
