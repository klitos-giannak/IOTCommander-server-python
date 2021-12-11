from flask import Flask

REST_API_PORT = 9977

app = Flask(__name__)


@app.route("/")
def supported_commands_query():
    print("Service root accessed. Sending Back Commands config.")
    try:
        with open('commands_config.json') as commands_config:
            return commands_config.read() + "\n"
    except IOError:
        return "500 Internal Server Error"


if __name__ == "__main__":
    from waitress import serve

    print("\n-- Running commands server at port " + str(REST_API_PORT) + " --\n")
    serve(app, host="0.0.0.0", port=REST_API_PORT)

    print("\n-- Commands server terminated --")
