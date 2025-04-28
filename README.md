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

This is some example input and output of a successful run of both server and client programs. 
<img width="936" alt="image" src="https://github.com/user-attachments/assets/9152b8b7-1f09-4af9-842a-b2fd21b1a109" />

<img width="959" alt="image" src="https://github.com/user-attachments/assets/d2b4c466-5b99-4ca6-ac4d-a84adff68e9f" />

---  
      
4. A menu is shown. Select (1-3) to access these options:
    1. The Average moisture in a refrigerator
    2. The Average water consumption per cycle in a dishwasher
    3. The Largest energy consumption of 3 IoT devices.

<img width="938" alt="image" src="https://github.com/user-attachments/assets/94b6b252-541d-481e-bddf-64424f079fe1" />  

<img width="717" alt="image" src="https://github.com/user-attachments/assets/ca1df96f-30d5-456c-83b8-476dc1a093bb" />  

---  
  
  
#### Type "exit" to end the program and server-client connection.

