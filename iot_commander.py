import commands_service
import discover_service

discover_service.initialise()
started = commands_service.start()

if started:
    try:
        discover_service.start()
    except KeyboardInterrupt:
        print("Interrupt received, stopping services")

    commands_service.stop()
    discover_service.stop()
