   
from pythonosc import udp_client
import time

def main():
    
 #   client = udp_client.SimpleUDPClient('127.0.0.1', 9999)
    client = udp_client.SimpleUDPClient('255.255.255.255', 9999, True)
   
    client.EnableBroadcast = 1;

    client.send_message('/plantoid/255/255/capa/0', 1024)
    print("activated for seconds: " + str(5))
    time.sleep(int(5))
    client.send_message('/plantoid/255/255/capa/0', 1024)
    print("de-activated")


if __name__ == '__main__':
    main()
