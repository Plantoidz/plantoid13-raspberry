from pythonosc import dispatcher
from pythonosc import osc_server

def print_handler(unused_addr, *args):
    print(f"Address: {unused_addr}, Args: {args}")

dispatcher = dispatcher.Dispatcher()
dispatcher.map("/*", print_handler)  # Catch all messages

server = osc_server.ThreadingOSCUDPServer(("0.0.0.0", 9999), dispatcher)
print("Serving on {}".format(server.server_address))
server.serve_forever()
