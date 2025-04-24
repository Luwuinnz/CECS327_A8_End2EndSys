import socket

# Valid queries
valid_queries = {
    "1": "What is the average moisture inside my kitchen fridge in the past three hours?",
    "2": "What is the average water consumption per cycle in my smart dishwasher?",
    "3": "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
}


def print_menu():
    print("\nSelect a query:")
    for key, query in valid_queries.items():
        print(f"{key}. {query}")
    print("Type 'exit' to quit.\n")


def start_client(server_ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((server_ip, port))
        except Exception:
            print("Connection failed. Check IP/port.")
            return

        print(f"Connected to server at {server_ip}:{port}")

        while True:
            print_menu()
            user_input = input("Enter your choice (1-3): ").strip()

            if user_input.lower() == "exit":
                print("Closing connection...")
                break
            elif user_input in valid_queries:
                client_socket.send(valid_queries[user_input].encode())
                response = client_socket.recv(1024).decode()
                print(f"\nServer Response:\n{response}")
            else:
                print("\n Sorry, this query cannot be processed.")
                print("Please try one of the following:")
                for q in valid_queries.values():
                    print(f"- {q}")
if __name__ == "__main__":
    host = input("Enter IP address to connect to (e.g., 127.0.0.1): ").strip()
    port_input = input("Enter port number to connect to (e.g., 65432): ").strip()

    try:
        port = int(port_input)
        start_client(host, port)
    except ValueError:
        print(" Invalid port number. Please enter a valid integer.")


