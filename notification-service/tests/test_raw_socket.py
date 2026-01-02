import socket
import ssl
import base64
import os

HOST = "localhost"
PORT = 9005
PATH = "/ws/v1/notification-service/notifications/users/a532384b-65f3-4fd1-a66f-a1e2d43c7777"

def test_raw_socket():
    print(f"Connecting to {HOST}:{PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    
    # Generate WebSocket Key
    key = base64.b64encode(os.urandom(16)).decode('utf-8')
    
    # Construct HTTP Upgrade Request
    request = (
        f"GET {PATH} HTTP/1.1\r\n"
        f"Host: {HOST}:{PORT}\r\n"
        "Upgrade: websocket\r\n"
        "Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        "\r\n"
    )
    
    print("--- Sending Request ---")
    print(request)
    sock.sendall(request.encode('utf-8'))
    
    print("--- Receiving Response ---")
    response_data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response_data += chunk
        # If we received the full headers (end with \r\n\r\n), we can stop reading headers
        if b"\r\n\r\n" in response_data:
            break
            
    print(response_data.decode('utf-8', errors='replace'))
    
    # Check if we got 101 Switching Protocols
    if b"101 Switching Protocols" in response_data:
        print("\n✅ Handshake SUCCESS!")
        
        # Now try to read one frame from server (if any)
        print("--- Waiting for Frames ---")
        sock.settimeout(5.0)
        try:
            frame = sock.recv(1024)
            print(f"Received frame bytes: {frame}")
            if not frame:
                print("Server closed connection immediately (FIN).")
        except socket.timeout:
            print("No data received from server (Timeout). Connection is OPEN.")
    else:
        print("\n❌ Handshake FAILED!")

    sock.close()

if __name__ == "__main__":
    test_raw_socket()
