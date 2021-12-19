import json
import sys

from flask import Flask

REST_API_PORT = 9977
CONFIG_FILENAME = 'commands_config.json'

PARAM_SHELL_COMMAND = "shellCommand"
PARAM_INTEGER = "int"
PARAM_FLOAT = "float"
PARAM_TEXT = "text"
ACCEPTED_PARAMETER_TYPES = [PARAM_INTEGER, PARAM_FLOAT, PARAM_TEXT]

app = Flask(__name__)
supported_commands: dict


@app.route("/")
def supported_commands_query():
    print("Service root accessed. Sending Back Commands config.")

    import copy
    commands_dict = copy.deepcopy(supported_commands)
    for command in commands_dict:
        commands_dict[command].pop(PARAM_SHELL_COMMAND)

    return json.dumps(commands_dict, indent=4) + "\n"


@app.route("/command/<command_name>")
def command_requested(command_name):
    from flask import request

    command: dict = supported_commands[command_name]
    shell_command: str = command[PARAM_SHELL_COMMAND]

    for param in command:
        if param == PARAM_SHELL_COMMAND:
            continue

        expected_type = command[param]
        try:
            value = request.args.get(param)
            if value is None:
                return "400 Bad Request\nmissing param " + param + "\n"

            if expected_type == PARAM_INTEGER:
                # we don't want to save the result, just validate the type
                if int(value) is None:
                    response = "400 Bad Request\nUnable to convert value of param "
                    response = response + param + " to type " + expected_type + "\n"
                    return response

            elif expected_type == PARAM_FLOAT:
                # we don't want to save the result, just validate the type
                if float(value) is None:
                    response = "400 Bad Request\nUnable to convert value of param "
                    response = response + param + " to type " + expected_type + "\n"
                    return response

        except ValueError:
            return "400 Bad Request\ninvalid param " + param + "\n"

        shell_command = shell_command.replace("$" + param, value, 1)

    import subprocess
    subprocess.call(shell_command, shell=True)
    print()
    return "200 OK\n"


def validate_config() -> bool:
    try:
        with open(CONFIG_FILENAME) as json_file:
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


if not validate_config():
    print("commands_config validation failed")
    sys.exit(1)
else:
    print_commands_summary()

if __name__ == "__main__":
    from waitress import serve

    print("-- Running commands server at port " + str(REST_API_PORT) + " --\n")
    serve(app, host="0.0.0.0", port=REST_API_PORT)

    print("\n-- Commands server terminated --")
