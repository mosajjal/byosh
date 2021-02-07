# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab
import sys, socket, argparse
from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE, DNSError
from os import environ
from socketserver import ThreadingUDPServer, DatagramRequestHandler

allow_all = False
w_list = []
args = None


class PacketHandler(DatagramRequestHandler):  # DatagramRequestHandler
    def handle(self) -> None:
        data = self.rfile.read(512)  # Maximum UDP Packet Size is 512 Byte
        if args.debug:  # Show Client Address (if debug)
            print("Accept Request from : ", self.client_address[0])
        try:
            packet = DNSRecord.parse(data)  # Parse DNS Packet
            for question in packet.questions:  # Iterate over questions ( however most of DNS Servers even BIND support single question)
                requested_domain_name = question.get_qname()  # Get the requested name
                reply_packet = packet.reply()  # Generate Reply packet
                if (not allow_all) and (w_list != [] and (
                not any(s[1:] in str(requested_domain_name) for s in w_list))):  # Check the Whitelist
                    try:
                        realip = socket.gethostbyname(requested_domain_name.idna())  # Get Real IP Address
                    except Exception as e:
                        if args.debug:
                            print(e)
                        realip = args.ip
                    reply_packet.add_answer(
                        RR(requested_domain_name, rdata=A(realip), ttl=60))  # Append Address to replies
                    if args.debug:
                        print("Request: %s --> %s" % (requested_domain_name.idna(), realip))
                else:
                    reply_packet.add_answer(RR(requested_domain_name, rdata=A(args.ip), ttl=60))  # Fake the address
                    if args.debug:
                        print("Request: %s --> %s" % (requested_domain_name.idna(), args.ip))
                self.wfile.write(reply_packet.pack())  # send Packed UDP Response to the client
        except DNSError as err:
            if args.debug:
                print(err)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process input')
    parser.add_argument("--ip", help="set listen ip address, set to ENV to get it from PUB_IP Env Variable",
                        action="store", type=str, default="0.0.0.0")
    parser.add_argument("--whitelist",
                        help="Whitelisted Domain. use ALL or DNS_ALLOW_ALL=YES Env variable for access all domain",
                        action="store", type=str, default="Empty")
    parser.add_argument("--port", help="set listen port", action="store", type=int, default=10530)
    parser.add_argument("--debug", help="enable debug logging", action="store_true")
    args = parser.parse_args()

    if str(args.ip).upper() == "ENV":
        args.ip = environ.get("PUB_IP")

    if args.debug:
        print('IP: %s Port: %s' % (args.ip, args.port))

    if environ.get("DNS_ALLOW_ALL") == "YES" or args.whitelist == "ALL":
        allow_all = True
    else:
        if args.whitelist != "Empty":
            with open(args.whitelist) as f:
                w_list.extend(f.read().splitlines())
    try:
        udp_sock = ThreadingUDPServer(("0.0.0.0", args.port), PacketHandler)
        udp_sock.serve_forever()
    except KeyboardInterrupt:
        if args.debug:
            print("done.")
