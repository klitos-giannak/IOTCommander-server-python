## How to test commands_service script with curl

The commands service has two endpoints.
1. /commands - this is called as is and is returning a json response describing the server's supported commands
2. /command/{commandName} - this is called with a valid commandName and can be optionally followed with query parameters

#### You will need:
1. a "server" device that is python 3 capable
2. a "client" computer with curl command installed
   > For testing purposes, you can use the same device for server and client
3. the server's ip address.
   > You can find this out by your system or by using the [Discover service](DISCOVER_SERVICE.md)
   > If you are using the same device for server and client just use 127.0.0.1 as your ip address
4. the port the commands_service is running on. If you haven't altered the script, this will be 9977


#### Instructions
1. Under a shell run `python3 commands_service.py` on your server device
2. On your "client" computer with on terminal 1 run `curl <ip:port>/commands`
   > You will receive a json response which looks similar to your [commands_config.json](../commands_config.json)
   > although missing the "shellCommand" from each supported command
3. Based on your [commands_config.json](../commands_config.json) you can also try the second endpoint. A correct command
will return a 200 response, and you will be able to see relevant logs on your server device shell.
If you are using the default config file you can try the following:
   > `curl <ip:port>/command/testNoParams`
   >
   > `curl <ip:port>/command/testString?myText=Testing_Text`
   >
   > `curl <ip:port>/command/testInt?myInt=4`
   >
   > `curl <ip:port>/command/testFloat?myFloat=3.14`
   >
   > `curl <ip:port>/command/testBoolean?myBoolean=true`
   >
   > `curl "<ip:port>/command/testAllTypes?myInt=4&myText=Testing_Text&myBoolean=true&myFloat=3.14"`
   
   > Note: when in need to pass more than one query parameters, enclose the whole curl argument in double quotes OR escape the & character with \