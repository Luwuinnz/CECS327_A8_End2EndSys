import socket #library for server-client connection
import psycopg2 #library for reading SQL queries; connects to SQL database

# Database connection
conn = psycopg2.connect(
    dbname="neondb", #default name for neondb database name
    user="neondb_owner",
    password="npg_MRJOE8Fip3BU", #neondb password in url
    host="ep-summer-credit-a6nmpxnl-pooler.us-west-2.aws.neon.tech", #neondb url
    sslmode="require"
)

#dictionary names attribute for dataniz
#Format - device asset UID (Dataniz): "Device name"
device_names = {
    "dac-izq-a3r-630": "Fridge 1",
    "d9fe4fca-e615-41a5-a1f6-7f0b303e6431" : "Fridge 2",
    "l4s-cir-7xn-hef": "Dishwasher"
}

def handle_query(query):
    #From psycopg2 library; cursor object from the database connection (conn). Execute SQL queries from python
    cur = conn.cursor()

    #query is the entire string options from this menu
    #"1": "What is the average moisture inside my kitchen fridge in the past three hours?",
    #"2": "What is the average water consumption per cycle in my smart dishwasher?",
    #"3": "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"

    if "average moisture" in query: #use string search

        #runs SQL query for fridge1
        cur.execute(""" 
            SELECT reading FROM moisture_readings
            WHERE assetUid = 'dac-izq-a3r-630' AND timestamp >= NOW() - INTERVAL '3 hours';
        """)

        #SQL: SELECT * FROM table;
        rows = cur.fetchall()
        if not rows: #no data fetched or exists in datebase
            return "No moisture data found in the past 3 hours."

        #Average moisture calcualtion from fridge 1
        avg = sum(row[0] for row in rows) / len(rows)
        rel_humid = round((avg / 1023) * 100, 2) #Arduino readings are 0 - 1023 for moisture reading sensor; rounds 2 decimal places

        return (f"Average Relative Humidity inside the kitchen Fridge 1 (past 3 hours): {rel_humid}% RH")

    elif "average water consumption" in query:

        #runs SQL query for dishwasher
        cur.execute("""
            SELECT water_liters FROM dishwasher_cycles
            WHERE assetUid = 'l4s-cir-7xn-hef';
        """)
        #SELECT * FROM database
        rows = cur.fetchall()

        if not rows: #no data fetched or exists in datebase
            return "No water consumption data found."

        #Average calculation for water consumption in dishwasher
        avg = sum(row[0] for row in rows) / len(rows)
        gallons = round(float(avg) * 0.264172, 2) #1 liter = 0.264172 gallons

        return f"Average water consumption per cycle in the smart dishwasher: {gallons} gallons"

    elif "consumed more electricity" in query:
        #electricity consumption for all 3 IoT devices; SQL queries
        cur.execute(""" 
            SELECT assetUid, SUM(energy_kwh)
            FROM electricity_data
            WHERE assetUid IN (
                'dac-izq-a3r-630', 
                'd9fe4fca-e615-41a5-a1f6-7f0b303e6431',
                'l4s-cir-7xn-hef'
            )
            GROUP BY assetUid;
        """)

        #SQL: SELECT * FROM db
        rows = cur.fetchall()

        if not rows: #no data fetched or exists in datebase
            return "No electricity usage data found."

        device_names = {
            "dac-izq-a3r-630": "Fridge 1 (Kitchen)",
            "d9fe4fca-e615-41a5-a1f6-7f0b303e6431": "Fridge 2",
            "l4s-cir-7xn-hef": "Dishwasher"
        }
        #2 days = 2880 minute
        #convert to hour, so * 60 mins
        usage = {device_names.get(row[0], row[0]): round(float(row[1])/2880 * 60, 3)
                 for row in rows}
        #usage is a dict
        #looks similar to this {device name ID to from dictionary : # kwh}

        #finds highest energy usage kwh value
        max_device = max(usage, key=usage.get)

        #formats the string from looping through the usage dictionary into a list
        #"device name: #kwh"
        report = "\n".join([f"{name}: {round(kwh, 3)} kWh" for name, kwh in usage.items()])
        return f"Electricity usage in the last 2 days:\n{report}\n\nDevice with highest usage: {max_device}"

    else: #in case there is no valid queries
        return (
            "Sorry, this query cannot be processed. Please try one of the following:\n"
            "1. What is the average moisture inside my kitchen fridge in the past three hours?\n"
            "2. What is the average water consumption per cycle in my smart dishwasher?\n"
            "3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
        )


def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            # server binding to ip and port
            server_socket.bind((host, port))

        except Exception:
            print("IP address or port was invalid.")
            return None

        server_socket.listen()
        print(f"Server listening on {host}:{port}...") #waiting for client to connect

        conn_client, addr = server_socket.accept() #server-client connection
        with conn_client:
            print(f"Connected by {addr} successfully")

            while True: #continuing until client breaks connection
                data = conn_client.recv(1024) #recieving the queries from client

                if not data: #when there is no valid queries
                    print("Client disconnected.")
                    break

                query = data.decode()
                print(f"Received query: {query}") #outputs successful query

                try:
                    # function to handle query
                    response = handle_query(query)

                except Exception as error:
                    #error handling for when query is invalid
                    print(f"Error while handling query: {error}")
                    response = "Server encountered an error while processing your request."

                # server sends client the response from query
                conn_client.send(response.encode())

if __name__ == "__main__":
    #strip() utilized in case of human error with " " added when copy and pasting IP and Port
    host = input("Enter IP address to bind to (e.g., 127.0.0.1): ").strip()
    port_input = input("Enter port number to bind to (e.g., 65432): ").strip()

    try:
        port = int(port_input)
        start_server(host, port) #function to preform server-client connection

    except ValueError: #in case port input is invalid
        print("Invalid port number. Please enter a valid integer.")
