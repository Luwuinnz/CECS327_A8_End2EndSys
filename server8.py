import socket
import psycopg2
import json
from datetime import datetime, timedelta

# connects once
conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_MRJOE8Fip3BU",
    host="ep-summer-credit-a6nmpxnl-pooler.us-west-2.aws.neon.tech",
    sslmode="require"
)
def to_real_amps(raw):
    # normalize based on sensor calibration
    zero_offset = 22.5
    sensor_range = 123  # 84 - (-39)
    full_amp_range = 30  # adjust if it's a ±20A or ±5A sensor
    return ((raw - zero_offset) / sensor_range) * full_amp_range
# matches device meta data to sensor names
sensor_map = {
    "ur2-2og-819-3cu": {#fridge 1
        "moisture": "Moisture Meter - moisture",
        "current": "ACS712 - ammeter"
    },
    "018a6ca3-17b4-4e4a-b8de-6978843f485d": {#fridge 2
        "moisture": "sensor 1 5a921667-93ee-42cf-bf64-1eb685c323d0",
        "current": "sensor 2 5a921667-93ee-42cf-bf64-1eb685c323d0"
    },
    "xa8-r1a-4cj-qua": {#dishwasher
        "water": "YF-S201 - water consumption sensor",
        "current": "ACS712 - ammetor for dishwasher"
    }
}
#matches device asset uid to device names
device_names = {
    "ur2-2og-819-3cu": "Fridge 1",
    "018a6ca3-17b4-4e4a-b8de-6978843f485d": "Fridge 2",
    "xa8-r1a-4cj-qua": "Dishwasher"
}

# load all sensor readings into memory
def load_virtual_data():
    cur = conn.cursor()#opens a cursor object from the database connection. a cursor lets you send SQL commands to the NeonDB database.
    cur.execute('SELECT payload FROM "assignment 8_virtual";')#this retrieves every row from your virtual table but only the payload column
    rows = cur.fetchall()#fetches all rows from the result of the SQL query and into a list

    data = {}#dictionary used to organize data
    for row in rows:
        try:
            payload = json.loads(row[0]) if isinstance(row[0], str) else row[0]# loads the payload json string into a python dictionary.row[0] is the payload.
            asset_uid = payload["asset_uid"]#get device uid
            raw_ts = payload.get("timestamp")#gets time

            if not raw_ts:#if no timestamp skip payload
                continue

            timestamp = datetime.fromtimestamp(int(raw_ts))#Converts the timestamp from unix format into a python datetime object.
            if asset_uid not in data:#if this is the first time seeing this device uid create a blank container
                data[asset_uid] = {"moisture": [], "current": [], "water": []}

            for key, field in sensor_map.get(asset_uid, {}).items():#loops through each sensor type for this specific device.sensor_map tells you what sensor names to expect inside the payload.
                if field in payload:#checks if this specific sensor field actually exists inside the payload.
                    value = float(payload[field])
                    data[asset_uid][key].append((timestamp, value))#binds the device and sensor to its data and time


        except Exception:#If anything fails while parsing a payload, skip that payload
            continue

    return data
#used to print data to see why fridge 2data was off for electricty. no longer needed fixed but keeping it here anyways
def print_simple_staggered(data):
    fridge1 = data.get("ur2-2og-819-3cu", {}).get("current", [])
    fridge2 = data.get("018a6ca3-17b4-4e4a-b8de-6978843f485d", {}).get("current", [])
    dishwasher = data.get("xa8-r1a-4cj-qua", {}).get("current", [])



    max_len = max(len(fridge1), len(fridge2), len(dishwasher))

    for i in range(max_len):
        f1 = fridge1[i][1] if i < len(fridge1) else "---"
        f2 = fridge2[i][1] if i < len(fridge2) else "---"
        dw = dishwasher[i][1] if i < len(dishwasher) else "---"
        print(f"Fridge 1: {f1}\tFridge 2: {f2}\tDishwasher: {dw}")
    print("Fridge 1 readings:", len(fridge1))
    print("Fridge 2 readings:", len(fridge2))
    print("Dishwasher readings:", len(dishwasher))

# Handle queries
def handle_query(query):
    data = load_virtual_data()
    #print_simple_staggered(data)

    if "average moisture" in query:
        asset_uid = "ur2-2og-819-3cu"  # Fridge 1
        now = datetime.now()
        readings = [val for (ts, val) in data.get(asset_uid, {}).get("moisture", [])#filters fridge 1 moisture readings to only keep the ones from the last 3 hours.
                    if ts >= now - timedelta(hours=3)]

        if not readings:
            return "No moisture data found in the past 3 hours."

        avg_raw = sum(readings) / len(readings)#calculates the average raw moisture value.
        rel_humid = round((avg_raw / 39) * 100, 2)#converts the average raw value (range 0–39) into a % relative humidity value.
        return f"Average Relative Humidity inside the kitchen Fridge 1 (past 3 hours): {rel_humid}% RH"

    elif "average water consumption" in query:
        asset_uid = "xa8-r1a-4cj-qua" #Dishwasher
        readings = data.get(asset_uid, {}).get("water", [])

        if not readings:
            return "No water consumption data found."

        avg_liters = sum([val for _, val in readings]) / len(readings)#averages the liters per cycle.
        avg_gallons = round(avg_liters * 0.264172, 2)#convert to gallons
        return f"Average water consumption per cycle: {avg_gallons} gallons"

    elif "consumed more electricity" in query:

        usage_kwh = {}#dictionary to track energy usage for each device
        for asset_uid in sensor_map:
            readings = data.get(asset_uid, {}).get("current", [])#get all current readings for the device
            readings.sort()  # sorts by time

            energy = 0.0
            for i in range(1, len(readings)):
                t1, a1 = readings[i - 1]
                t2, a2 = readings[i]
                hours = (t2 - t1).total_seconds() / 3600
                avg_amp = (to_real_amps(a1) + to_real_amps(a2)) / 2
                power_kw = (avg_amp * 120) / 1000
                energy += power_kw * hours
            #for each pair of readings:
            # calculate time difference in hours.
            #calculate average amps across the two readings.
            # multiply by 120V and scale to kiloWatts.add to total energy used.

            usage_kwh[device_names[asset_uid]] = round(energy, 3)#save the total kWh used by the device into the dictionary

        if not usage_kwh:
            return "No electricity usage data found."

        max_device = max(usage_kwh, key=usage_kwh.get)#find which device used the most energy
        report = "\n".join([f"{name}: {val} kWh" for name, val in usage_kwh.items()])
        return f"Electricity usage in the last 2 days:\n{report}\n\nDevice with highest usage: {max_device}"

    else:
        return (
            "Sorry, this query cannot be processed. Please try one of the following:\n"
            "1. What is the average moisture inside my kitchen fridge in the past three hours?\n"
            "2. What is the average water consumption per cycle in my smart dishwasher?\n"
            "3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
        )

# TCP server loop
def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.bind((host, port))
        except Exception:
            print("IP address or port was invalid.")
            return

        server_socket.listen()
        print(f"Server listening on {host}:{port}...")

        conn_client, addr = server_socket.accept()
        with conn_client:
            print(f"Connected by {addr} successfully")

            while True:
                data = conn_client.recv(1024)
                if not data:
                    print("Client disconnected.")
                    break

                query = data.decode()
                print(f"Received query: {query}")

                try:
                    response = handle_query(query)
                except Exception as e:
                    print(f"Error while handling query: {e}")
                    response = "Server encountered an error while processing your request."

                conn_client.send(response.encode())

if __name__ == "__main__":
    host = input("Enter IP address to bind to (e.g., 127.0.0.1): ").strip()
    port_input = input("Enter port number to bind to (e.g., 65432): ").strip()

    try:
        port = int(port_input)
        start_server(host, port)
    except ValueError:
        print("Invalid port number. Please enter a valid integer.")
