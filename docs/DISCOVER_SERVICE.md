## How to test discover_service script

#### You will need:
1. a "server" device that is python 3 capable
2. a "client" computer with a linux shell and the nc command installed
   > For testing this can be the same device as the "server"
   
   > You will need two terminals in this device, one for listening for responses and one for broadcasting commands, see #2 and #3 in instructions below
   
3. the broadcast address of your local network where both the "server" and the "client" are connected.
   > if your ip is something like 192.168.1.2 and your netmask is 255.255.255.0 then your broadcast address will be 192.168.1.255
   
4. the port the discover_service is bound. If you havent altered this script, this will be 9977


#### Instructions
1. Under a linux shell run `python3 discover_service.py` on your server device
2. On your "client" computer with on terminal 1 run `nc -v -u -l -p 65000`
   > This is going to give verbose output ***-v*** while listening ***-l*** for responses in UDP protocol ***-u*** in localport ***-p*** 65000
   
3. On your "client" computer, from terminal 2 run `nc -u -b -p 65000 192.168.1.255 9977`
   > this is going to open a connection with UPD protocol ***-u*** allowing broadcast ***-b*** from localport ***-p*** 65000 in the broadcast address 192.168.1.255 on port 9977
   
   > please change the broadcast address and the bound port accordingly
   
4. Now that the connection is made with step #3, on the same terminal 2, write and send the json string ***{"action":"discover"}***
5. Check your terminal 1 for the output. You will be able to see the "server" ip address and a json response giving you the _deviceName_ of the "server"
