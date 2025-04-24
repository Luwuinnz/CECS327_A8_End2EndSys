import socket
import psycopg2
from datetime import datetime, timedelta

# Database connection
conn = psycopg2.connect(
    dbname="neondb",
    user="neondb_owner",
    password="npg_MRJOE8Fip3BU",
    host="ep-summer-credit-a6nmpxnl-pooler.us-west-2.aws.neon.tech",
    sslmode="require"
)

# Friendly names for each device
device_names = {
    "dac-izq-a3r-630": "Fridge 1",
    "l4s-cir-7xn-hef": "Dishwasher"
}

def handle_query(query):
    cur = conn.cursor()

    if "average moisture" in query:
        cur.execute("""
            SELECT reading FROM moisture_readings
            WHERE assetUid = 'dac-izq-a3r-630' AND timestamp >= NOW() - INTERVAL '3 hours';
        """)
        rows = cur.fetchall()
        if not rows:
            return "No moisture data found in the past 3 hours."
        avg = sum(row[0] for row in rows) / len(rows)
        rh = round((avg / 1023) * 100, 2)
        return f"Average Relative Humidity inside the kitchen fridge (past 3 hours): {rh}% RH"

    elif "average water consumption" in query:
        cur.execute("""
            SELECT water_liters FROM dishwasher_cycles
            WHERE assetUid = 'l4s-cir-7xn-hef';
        """)
        rows = cur.fetchall()
        if not rows:
            return "No water consumption data found."
        avg = sum(row[0] for row in rows) / len(rows)
        gallons = round(float(avg) * 0.264172, 2)
        return f"Average water consumption per cycle in the smart dishwasher: {gallons} gallons"

    elif "consumed more electricity" in query:
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
        rows = cur.fetchall()
        if not rows:
            return "No electricity usage data found."
        device_names = {
            "dac-izq-a3r-630": "Fridge 1 (Kitchen)",
            "d9fe4fca-e615-41a5-a1f6-7f0b303e6431": "Fridge 2",
            "l4s-cir-7xn-hef": "Dishwasher"
        }
        usage = {device_names.get(row[0], row[0]): float(row[1]) for row in rows}
        max_device = max(usage, key=usage.get)
        report = "\n".join([f"{name}: {round(kwh, 3)} kWh" for name, kwh in usage.items()])
        return f"Electricity usage in the last 2 days:\n{report}\n\nDevice with highest usage: {max_device}"

    else:
        return (
            "Sorry, this query cannot be processed. Please try one of the following:\n"
            "- What is the average moisture inside my kitchen fridge in the past three hours?\n"
            "- What is the average water consumption per cycle in my smart dishwasher?\n"
            "- Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
        )


def start_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        try:
            server_socket.bind((host, port))
        except Exception:
            print("IP address or port was invalid.")
            return None

        server_socket.listen()
        print(f"Server listening on {host}:{port}...")

        conn_client, addr = server_socket.accept()
        with conn_client:
            print(f"Connected by {addr}")
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
