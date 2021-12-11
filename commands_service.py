import json
import sys

from flask import Flask

REST_API_PORT = 9977
CONFIG_FILENAME = 'commands_config.json'
ACCEPTED_PARAMETER_TYPES = ["integer", "float", "text"]
PARAM_SHELL_COMMAND = "shellCommand"

app = Flask(__name__)


@app.route("/")
def supported_commands_query():
    print("Service root accessed. Sending Back Commands config.")
    try:
        with open(CONFIG_FILENAME) as commands_config:
            return commands_config.read() + "\n"
    except IOError:
        return "500 Internal Server Error"


def validate_config() -> bool:
    try:
        with open(CONFIG_FILENAME) as json_file:
            commands: dict = json.load(json_file)
            for command in commands:
                parameters: dict = commands[command]
                shell_command = parameters.pop(PARAM_SHELL_COMMAND, None)
                if shell_command is None:
                    print('"' + PARAM_SHELL_COMMAND + '" not found for command "' + command + '"')
                    return False

                for (key, value) in parameters.items():
                    if not ACCEPTED_PARAMETER_TYPES.__contains__(value):
                        print('Unknown parameter value: "' + value + '" for key "' + key + '"')
                        return False

            return True
    except IOError:
        return False


if not validate_config():
    print("commands_config validation failed")
    sys.exit(1)

if __name__ == "__main__":
    from waitress import serve

    print("\n-- Running commands server at port " + str(REST_API_PORT) + " --\n")
    serve(app, host="0.0.0.0", port=REST_API_PORT)

    print("\n-- Commands server terminated --")
