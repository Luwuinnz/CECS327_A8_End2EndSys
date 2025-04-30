SOCKET AND PSYCOPG2 LIBRARIES MUST HAVE BEEN INSTALLED IN THE USED PYTHON IDE FOR THE PROGRAM TO WORK

(Pycharm IDE was used)

Group #3 Tiffany Lin & Chris Garibay
___
1. Download the client8.py and server8.py Python files. 

2. Run the server Python file first. You should be prompted to input a valid IP address and a port number.

#### For local run of this program, use your private IP and an arbitrary port number for the Server Program.
* Private IP: 10.39.57.168  
* Port: 12345
```
#Prompts user to input a IP address and port number:

Enter IP address to bind to (e.g., 127.0.0.1): 
Enter port number to bind to (e.g., 65432):
```
---
It should output this if successful binding:
```
(The x and p are valid entry numbers for IP address and port number)
Server listening on xxx.xxx.xxx.xxx:ppppp...
```
---

3. Then run the client Python program. Input the same IP address and port number used for the server program for the local run of this program.
```
Enter IP address to bind to (e.g., 127.0.0.1): 
Enter port number to bind to (e.g., 65432):
```
---
This is the output when there is a successful Server and Client connection.

---
```
Connected by ('xxx.xxx.xxx.xxx', ppppp) successfully.
```

A menu is shown. Select (1-3) to access these options:
    1. The Average moisture in a refrigerator
    2. The Average water consumption per cycle in a dishwasher
    3. The Largest energy consumption of 3 IoT devices.

The input is a (1-3) according to the menu options. Otherwise, the program will not accept it.

This is some example input and output of a successful run of both server and client programs. 

<img width="691" alt="image" src="https://github.com/user-attachments/assets/2901b537-bc12-43ad-94b0-293603669eea" />
<img width="687" alt="image" src="https://github.com/user-attachments/assets/5f62e3dc-51d8-4df2-b613-2e03cc519561" />
<img width="652" alt="image" src="https://github.com/user-attachments/assets/46a014db-2b1e-4537-b543-885366a326d1" />

---  
  
  
#### Type "exit" to end the program and server-client connection.

