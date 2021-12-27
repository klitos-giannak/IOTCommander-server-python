import asyncio
import json
import os

from MicroWebSrv2 import *

REST_API_PORT = 9977
CONFIG_FILENAME = 'commands_config.json'

PARAM_SHELL_COMMAND = "shellCommand"
PARAM_INTEGER = "int"
PARAM_FLOAT = "float"
PARAM_TEXT = "text"
PARAM_BOOLEAN = "boolean"
ACCEPTED_PARAMETER_TYPES = [PARAM_INTEGER, PARAM_FLOAT, PARAM_BOOLEAN, PARAM_TEXT]
ACCEPTED_BOOLEAN_TRUE_VALUES = ["true", "t", "1"]
ACCEPTED_BOOLEAN_FALSE_VALUES = ["false", "f", "0"]
COMMAND_RESPONSE_OK_BODY = "<html><body><h1>[200] OK</h1><p>Command successful</p></body></html>\n"

should_continue = True
web_server: MicroWebSrv2

supported_commands: dict


def get_boolean_value(value: str):
    if value.lower() in ACCEPTED_BOOLEAN_TRUE_VALUES:
        return True
    elif value.lower() in ACCEPTED_BOOLEAN_FALSE_VALUES:
        return False
    else:
        return None


@WebRoute(GET, '/commands')
def supported_commands_query(server: MicroWebSrv2, request: HttpRequest):
    print("Supported commands requested. Sending Back Commands config.")

    import copy
    commands_dict = copy.deepcopy(supported_commands)
    for command in commands_dict:
        commands_dict[command].pop(PARAM_SHELL_COMMAND)

    body = json.dumps(commands_dict, indent=4) + "\n"
    request.Response.ReturnOk(body)
    return


@WebRoute(GET, '/command/<command_name>')
def command_requested(server: MicroWebSrv2, request: HttpRequest, args: dict):
    command_name = args['command_name']
    print("Command <" + command_name + "> requested. Trying to parse parameters.")

    if not isinstance(command_name, str):
        request.Response.ReturnBadRequest()
        return

    command: dict = supported_commands.get(command_name)
    if command is None:
        # retry but case-insensitive
        for key in supported_commands:
            if key.lower() == command_name:
                command: dict = supported_commands[key]
                break

    if command is None:
        request.Response.ReturnNotFound()
        return
    shell_command: str = command[PARAM_SHELL_COMMAND]

    for param in command:
        if param == PARAM_SHELL_COMMAND:
            continue

        expected_type = command[param]
        try:
            value = request.QueryParams.get(param)
            if value is None:
                reason = "missing param " + param
                print(reason + ". Responding with an error.")
                request.Response.ReturnBadRequest()
                return

            if expected_type == PARAM_INTEGER:
                # we don't want to save the result, just validate the type
                if int(value) is None:
                    reason = "Unable to convert value of param " + param + " to type " + expected_type
                    print(reason + ". Responding with an error.")
                    request.Response.ReturnBadRequest()
                    return

            elif expected_type == PARAM_FLOAT:
                # we don't want to save the result, just validate the type
                if float(value) is None:
                    reason = "Unable to convert value of param " + param + " to type " + expected_type
                    print(reason + ". Responding with an error.")
                    request.Response.ReturnBadRequest()
                    return

            elif expected_type == PARAM_BOOLEAN:
                # we don't want to save the result, just validate the type
                if get_boolean_value(value) is None:
                    reason = "Unable to convert value of param " + param + " to type " + expected_type
                    print(reason + ". Responding with an error.")
                    request.Response.ReturnBadRequest()
                    return

        except ValueError:
            reason = "Invalid param " + param
            print(reason + ". Responding with an error.")
            request.Response.ReturnBadRequest()
            return

        shell_command = shell_command.replace("$" + param, value, 1)

    print("Parameters parsed successfully, responding OK")
    import subprocess
    subprocess.call(shell_command, shell=True)
    print()
    request.Response.ReturnOk(COMMAND_RESPONSE_OK_BODY)


def validate_config() -> bool:
    try:
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        file = os.path.join(__location__, CONFIG_FILENAME)
        with open(file) as json_file:
            global supported_commands
            supported_commands = json.load(json_file)
            for command in supported_commands:
                parameters: dict = supported_commands[command]
                shell_command = parameters.get(PARAM_SHELL_COMMAND)
                if shell_command is None:
                    print('"' + PARAM_SHELL_COMMAND + '" not found for command "' + command + '"')
                    return False

                for (key, value) in parameters.items():
                    if not (key == PARAM_SHELL_COMMAND or ACCEPTED_PARAMETER_TYPES.__contains__(value)):
                        print('Unknown parameter value: "' + value + '" for key "' + key + '"')
                        return False

            return True
    except IOError:
        return False


def print_commands_summary():
    output = "\nSupported commands summary: ["
    # noinspection PyUnboundLocalVariable
    for command in supported_commands:
        output = output + command + ", "
    output = output[:-2]
    output = output + "]"
    print(output)


def start():
    if not validate_config():
        print("commands_config validation failed")
        return
    else:
        print_commands_summary()

    print("-- Running commands server at port " + str(REST_API_PORT) + " --\n")

    global web_server
    web_server = MicroWebSrv2()
    web_server.BindAddress = ('0.0.0.0', REST_API_PORT)
    web_server.StartManaged()


def stop():
    web_server.Stop()
    print("\n-- Commands server terminated --")


async def start_blocking():
    start()
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(start_blocking())
    except KeyboardInterrupt:
        stop()
