import argparse
import time

from pythonosc import udp_client



def main():

	print('staritng\n')
	parser = argparse.ArgumentParser()
	parser.add_argument("--ip", default="127.0.0.1")
	parser.add_argument("--port", default=9999)
	args = parser.parse_args()
	
	client = udp_client.SimpleUDPClient(args.ip, args.port, True)

	
	x = ""
	while(x != 'quit'):
		x = input()
		client.send_message('/filename', x)
		client.send_message('/plantoid/255/255/capa/0', 1024)
		time.sleep(2)
		client.send_message('/plantoid/255/255/capa/0', 1024)
		print('sent osc')



if __name__ == "__main__":
    main()
