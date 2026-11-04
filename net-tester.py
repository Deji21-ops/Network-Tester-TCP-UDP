# implement an iperf client in Python using sockets

import socket
import time
import threading
import argparse
import sys
from typing import Optional
import csv
from typing import List
import select

""""
    Usage
    -----
    - Instantiate with an optional CSV file path. Use none to disable, or a path
      like "results.csv" to enable CSV output. By default the class output performance results to "results.csv".
    - Call log_stat() to record individual measurements.
    - Call summary() to print aggregated statistics.
    - Call close() to close any open CSV resource before program exit.

    Example
    -------
    logger = Logger("out.csv")
    logger.log_info("Starting test")
    logger.log_stat(time.time(), "192.0.2.1", 5201, bandwidth=12.34)
    logger.summary()
    logger.close()
"""


class Logger:
    """
    Logger
    ------
    Logger class for recording and displaying network test metrics"""

    INFO = '\033[94m[INFO]\033[0m '
    ERROR = '\033[91m[ERROR]\033[0m '

    class Stat:
        """A class to model a single measurement record"""

        def __init__(self, timestamp: float, bandwidth: Optional[float] = None,
                     loss: Optional[float] = None, jitter: Optional[float] = None):
            self.timestamp = timestamp
            self.bandwidth = bandwidth
            self.loss = loss
            self.jitter = jitter

    def __init__(self, csv_output: Optional[str] = "results.csv"):
        """Initialize Logger with optional CSV output"""
        self.stats: List[Logger.Stat] = []  # List to store measurements
        self.csv_output = csv_output        # CSV file path or None
        self.csv_file = None               # File handle for CSV
        self.csv_writer = None             # CSV writer object

        # If the csv parameter is None, then disable CSV output
        if csv_output:
            self.csv_file = open(csv_output, 'w', newline='')
            self.csv_writer = csv.writer(self.csv_file)
            self.csv_writer.writerow(
                ['timestamp', 'elapsed', 'bandwidth_mbps', 'loss_percent', 'jitter_ms'])

    def log_stat(self, timestamp: float, ip: str, port: int, bandwidth: Optional[float] = None,
                 loss: Optional[float] = None, jitter: Optional[float] = None) -> None:
        """
        Log a measurement (all parameters optional)
        - timestamp: Time of measurement (float)
        - ip: Client IP address (str)
        - port: Client port number (int)
        - bandwidth: Bandwidth in Mbps (float, optional)
        - loss: Packet loss in percent (float, optional)
        - jitter: Jitter in milliseconds (float, optional)
        """
        stat = Logger.Stat(timestamp, bandwidth, loss, jitter)
        self.stats.append(stat)
        elapsed = 0.0
        if len(self.stats) > 1:
            elapsed = timestamp - self.stats[0].timestamp

        # Write to CSV if enabled
        if self.csv_writer:
            self.csv_writer.writerow([
                ip, port,
                timestamp,
                f"{elapsed:.3f}",
                f"{bandwidth:.2f}" if bandwidth is not None else "",
                f"{loss:.2f}" if loss is not None else "",
                f"{jitter:.2f}" if jitter is not None else ""
            ])
            self.csv_file.flush()

        parts = [f"[{int(elapsed):03d}s] [Client:{ip}:{port}]"]

        if bandwidth is not None:
            parts.append(f"Bandwidth: {bandwidth:.2f} Mbps")
        if loss is not None:
            parts.append(f"Loss: {loss:.2f}%")
        if jitter is not None:
            parts.append(f"Jitter: {jitter:.6f} ms")

        print(" ".join(parts))

    def summary(self) -> None:
        """
        Print summary statistics
        1. Duration of the test
        2. Number of measurements
        3. For each metric (bandwidth, loss, jitter):
           - Average
           - Minimum
           - Maximum
        4. If CSV output was enabled, print the path to the CSV file
        """
        if not self.stats:
            print(f"{Logger.INFO}No statistics recorded")
            return

        print(f"\n{Logger.INFO}=== Test Summary ===")
        print(
            f"  Duration: {int(self.stats[-1].timestamp - self.stats[0].timestamp)}s")
        print(f"  Measurements: {len(self.stats)}")

        # Calculate averages
        bw_values = [
            s.bandwidth for s in self.stats if s.bandwidth is not None]
        loss_values = [s.loss for s in self.stats if s.loss is not None]
        jitter_values = [s.jitter for s in self.stats if s.jitter is not None]

        if bw_values:
            print(f"  Bandwidth: avg={sum(bw_values)/len(bw_values):.2f} Mbps, "
                  f"min={min(bw_values):.2f}, max={max(bw_values):.2f}")
        if loss_values:
            print(f"  Loss: avg={sum(loss_values)/len(loss_values):.2f}%, "
                  f"min={min(loss_values):.2f}, max={max(loss_values):.2f}")
        if jitter_values:
            print(f"  Jitter: avg={sum(jitter_values)/len(jitter_values):.6f} ms, "
                  f"min={min(jitter_values):.6f}, max={max(jitter_values):.6f}")

        if self.csv_output:
            self.log_info(f"Results saved to {self.csv_output}")

    def close(self) -> None:
        """Close CSV file if open"""
        if self.csv_file:
            self.csv_file.close()

    def log_info(self, message: str) -> None:
        """
        Print an info message to stdout
        """
        print(f"{Logger.INFO}{message}")

    def log_error(self, message: str) -> None:
        """
        Print an info message to stdout
        """
        print(f"{Logger.ERROR}{message}")

# Below you can find sample function signatures for the net-tester client and server.
# You can modify them as needed.


# ---------------------- TCP stubs (Task 2) ----------------------

def tester_tcp_client(log: Logger, server_ip: str, server_port: int,
                      duration: int, interval: int) -> None:
    """TCP client (Task 2)
    TODO:
      - Connect and send for 'duration' seconds (chunks of 'window')
      - Every 'interval' seconds, compute and log bandwidth
    """
    log.log_info(f"Starting TCP client to {server_ip}:{server_port} "
                 f"for {duration}s")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, server_port))

    payload = b"x" * 16000
    start_time = time.time()
    last_report = start_time
    bytes_sent = 0

    while True:
        current = time.time()
        elapsed = current - start_time

        if elapsed >= duration:
            break
# continuos send
        sock.sendall(payload)
        bytes_sent += len(payload)

        if current - last_report >= interval:
            bw_mbps = (bytes_sent * 8) / (current - last_report) / 1e6
            log.log_stat(time.time(), server_ip,
                         server_port, bandwidth=bw_mbps)
            bytes_sent = 0
            last_report = current

    sock.close()
    # Skeleton only; safe no-op if not implemented.


def tester_tcp_server(log: Logger, port: int) -> None:
    """TCP server (Task 2)
   #TODO:

      - Listen on 'port'; accept multiple clients
      - Receive/discard bytes; optionally log per-client bandwidth
    """
    log.log_info(f"Starting TCP server on port {port}")

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("0.0.0.0", port))
    server_sock.listen()

    def handle_client(connect, address):
        log.log_info(f"Accepted connection from {address}")
        try:
            while True:
                data = connect.recv(65536)
                if not data:
                    break
        except Exception as e:
            log.log_error(f"client {address} error: {e}")
        finally:
            connect.close()
            log.log_info(f"client {address} disconnected")

    while True:
        connect, address = server_sock.accept()
        thread = threading.Thread(
            target=handle_client, args=(connect, address), daemon=True)
        thread.start()

    # Skeleton only; safe no-op if not implemented.


# ---------------------- UDP stubs (Tasks 3 & 4) ----------------------

def tester_udp_client(log: Logger, server_ip: str, server_port: int,
                      duration: int, interval: int,
                      rate_kbps: int, ack: bool) -> None:
    """UDP client
    Task 3 (ack == False):
      - Send datagrams at 'rate_kbps'
      - First 4 bytes = big-endian ID; start at 1; send ID=0 to end
      - Client may log sending rate, but server computes metrics
    Task 4 (ack == True):
      - Receive acks (ID + server receive timestamp)
      - Compute client-side BW / loss (via timeout) / jitter from acks and log
    """
    log.log_info(f"Starting UDP client to {server_ip}:{server_port} "
                 f"for {duration}s at {rate_kbps} Kbps (ack={ack})")

    # Common setup (safe if left unused):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Do not forger to bind the client socket to a port if you want to receive ACKs
    if not ack:
        # -------------------- Task 3: UDP without acks --------------------
        # TODO:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        pkt_size = 1024  # 1kb pakets
        bits_per_sec = rate_kbps * 1000
        pkt_interval = (pkt_size * 8) / bits_per_sec  # seconds between sends

        pkt_id = 1
        start = time.time()
        last_log = start
        bytes_sent = 0

        while time.time() - start < duration:

            pkt = pkt_id.to_bytes(4, "big") + b"x" * (pkt_size - 4)
            sock.sendto(pkt, (server_ip, server_port))
            bytes_sent += pkt_size
            pkt_id += 1

            current = time.time()
            if current - last_log >= interval:
                bw_mbps = (bytes_sent * 8) / (current-last_log) / 1e6
                log.log_stat(current, server_ip,
                             server_port, bandwidth=bw_mbps)
                bytes_sent = 0
                last_log = current

            time.sleep(pkt_interval)

        sock.sendto((0).to_bytes(4, "big"), (server_ip, server_port))
        sock.close()

    #   - Compute packet trasnmission interval to match rate_kbps using you datagram size
    #   - Loop until 'duration' elapsed:
    #       * Build payload: 4B ID (big-endian) + (pkt_size-4) bytes
    #       * sendto(...)
    #       * sleep until next send (pkt_interval)
    #       * every 'interval' seconds, optionally log sending rate
    #   - Send ID=0 to signal end; close socket
    else:

        # -------------------- Task 4: UDP with acks --------------------
        # TODO:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 0))
        sock.setblocking(False)

        pkt_size = 1000
        pkt_interval = (pkt_size*8) / (rate_kbps * 1000)
        pkt_interval = max(pkt_interval, 0.0001)

        start = time.time()
        next_log = start + interval

        pkt_id = 1

        sent_times = {}
        rtt_list = []
        jitter_list = []
        lost = 0
        received = 0
        last_rtt = None

        while True:
            current = time.time()

            if current - start >= duration:
                break

            # send packets

            payload = pkt_id.to_bytes(4, "big") + b"A" * (pkt_size - 4)
            sock.sendto(payload, (server_ip, server_port))
            sent_times[pkt_id] = current

            pkt_id += 1

            # read acks

            try:
                ack_data, address = sock.recvfrom(2048)
                ack_id = int.from_bytes(ack_data[:4], "big")
                ts = float(ack_data[4:].decode())

                received += 1

                rtt = (time.time() - sent_times.get(ack_id, time.time())) * 1000.0
                rtt_list.append(rtt)

                # jitter
                if last_rtt is not None:
                    jitter = abs(rtt - last_rtt)
                    jitter_list.append(jitter)
                last_rtt = rtt

            except:
                pass

            if current >= next_log:
                total_sent = pkt_id - 1
                lost = total_sent - received

                avg_jitter = sum(jitter_list) / \
                    len(jitter_list) if jitter_list else 0.0

                bw = (total_sent * pkt_size * 8 / 1e6) / (current - start)

                log.log_stat(current, server_ip, server_port, bw,
                             (lost/total_sent) * 100 if total_sent else 0, avg_jitter)

                next_log = current + interval

            time.sleep(pkt_interval)

        sock.sendto((0).to_bytes(4, "big"), (server_ip, server_port))
        sock.close()

        #   - Keep track of pending ACKs and received ACK timestamps
        #   - Non-blocking recv for acks:
        #       * parse 4B ID + server-timestamp (specify your chosen encoding)
        #       * compute RTT / arrival deltas; update metrics
        #   - Every 'interval' seconds, log client-side BW/loss/jitter via log.log_stat(...)
        #   - End with ID=0; close socket


def tester_udp_server(log: Logger, port: int, rate: int, interval: int, ack: bool) -> None:
    """UDP server
    Task 3 (ack == False):
      - Receive datagrams from multiple clients (track by (ip,port))
      - Compute per-client bandwidth / jitter / loss from arrivals
      - Periodically log per-client metrics via log.log_stat(...)
    Task 4 (ack == True):
      - Same as Task 3, plus send an ack for each received datagram:
        4B ID (big-endian)
    """
    log.log_info(f"Starting UDP server on port {port} (ack={ack})")
    # Common setup (safe if left unused):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.bind(("0.0.0.0", port))

    if not ack:
        # -------------------- Task 3: server-only metrics --------------------
        # TODO:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", port))
# dict to store stats for each clietns
# key = (clinets_ip, client_port)
# value = dict with bytes, ids, jitter trackign
        clients = {}
        last_log_time = time.time()

        while True:
            try:
                data, address = sock.recvfrom(2048)
                client_ip, client_port = address
                current = time.time()

                pkt_id = int.from_bytes(data[:4], "big")

                if pkt_id == 0:
                    log.log_info(
                        f"client {client_ip}: {client_port} finished sending")
                    continue

                if (client_ip, client_port) not in clients:
                    clients[(client_ip, client_port)] = {
                        "bytes": 0,
                        "ids": set(),
                        "last_time": 0,
                        "jitters": []
                    }

                stats = clients[(client_ip, client_port)]
                # count bytes that it gets
                stats["bytes"] += len(data)

                # save packet ID for the loss calc
                stats["ids"].add(pkt_id)

                if stats["last_time"] != 0:
                    diff = current - stats["last_time"]
                    stats["jitters"].append(diff)

                stats["last_time"] = current

                if current - last_log_time >= interval:
                    for (ip, port_num), s in clients.items():

                        # calc bw
                        bandwidth = (s["bytes"]*8 / (interval * 1e6))

                        # calc loss %
                        if len(s["ids"]) > 0:
                            highest_id = max(s["ids"])
                            received = len(s["ids"])
                            loss_ratio = 1 - (received / highest_id)
                            loss_percent = loss_ratio * 100
                        else:
                            loss_percent = 0.0

                        # calc jitter
                        if len(s["jitters"]) > 0:
                            jitter_ms = (sum(s["jitters"]) /
                                         len(s["jitters"])) * 1000

                        else:
                            jitter_ms = 0.0

                        # Log results
                        log.log_stat(time.time(
                        ), ip, port_num, bandwidth=bandwidth, loss=loss_percent, jitter=jitter_ms)

                        s["bytes"] = 0
                        s["jitters"] = []

                    last_log_time = current
            except KeyboardInterrupt:
                log.log_info("UDP server stopped")
                break

        #   - recvfrom(...) loop
        #   - Parse ID from first 4B; update per-client stats
        #   - When elapsed >= interval (per client), compute:
        #       * bandwidth (bytes/elapsed)
        #       * loss = 1 - (recv_count / (max_id - min_id + 1))
        #       * jitter from consecutive arrival deltas
        #     then log via: log.log_stat(ip, port, bandwidth=..., loss=..., jitter=...)
    else:
        # -------------------- Task 4: add acknowledgements --------------------
        # TODO:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", port))

        clients = {}
        last_log_time = time.time()
        while True:

            current = time.time()
            try:
                data, address = sock.recvfrom(2048)
            # creating entry for new client
                if address not in clients:
                    clients[address] = {
                        "bytes": 0,
                        "count": 0,
                        "last_id": 0,
                        "jitter_list": [],
                        "last_arrival": None,
                        "last_time": current
                    }

                client = clients[address]

                pkt_id = int.from_bytes(data[:4], "big")

                # if ID 0 temrinate
                if pkt_id == 0:
                    log.log_info(
                        f"client {address[0]}:{address[1]} done sending")
                    continue

                # update stats
                client["bytes"] += len(data)
                client["count"] += 1

                # jitter calc
                if client["last_arrival"] is not None:
                    delta = (current - client["last_arrival"]) * 1000.0
                    client["jitter_list"].append(delta)

                client["last_arrival"] = current
                client["last_id"] = max(client["last_id"], pkt_id)

                # sned ack

                ts_bytes = str(current).encode()
                ack_packet = data[:4] + ts_bytes
                sock.sendto(ack_packet, address)

                # interval logginf

                if current - last_log_time >= interval:
                    last_log_time
                    for (ip, port_num), c in clients.items():
                        elapsed = current - c["last_time"]

                        bw = (c["bytes"] * 8/1e6/elapsed if elapsed > 0 else 0)
                        if c["last_id"] > 0:
                            loss = 1 - (c["count"] / c["last_id"])
                        else:
                            loss = 0.0

                        jitter = sum(
                            c["jitter_list"]) / len(c["jitter_list"]) if c["jitter_list"] else 0.0

                        log.log_stat(current, ip, port_num,
                                     bw, loss * 100, jitter)

                        # reset
                        c["bytes"] = 0
                        c["count"] = 0
                        c["jitter_list"] = []
                        c["last_time"] = current

                    last_log_time = current
            except KeyboardInterrupt:
                break
        #   - Same as above, and for each received datagram:
        #       * Build ack: 4B ID + timestamp (e.g., float via struct.pack)
        #       * sendto(ack, (ip, port))
        #   - Continue periodic logging as in Task 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="SCC.231 net-tester application")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("-s", "--server", action="store_true",
                      help="Run in server mode")
    mode.add_argument("-c", "--client", metavar="ADDR",
                      help="Run in client mode, connect to ADDR")

    parser.add_argument("-p", "--port", type=int,
                        default=5001, help="Port (default 5001)")
    parser.add_argument("-u", "--udp", action="store_true",
                        help="Use UDP (default TCP)")
    parser.add_argument("-a", "--ack", action="store_true",
                        help="(UDP) Enable acknowledgements")
    parser.add_argument("-t", "--duration", type=int,
                        default=60, help="Test duration seconds (default 60)")
    parser.add_argument("-i", "--interval", type=int, default=1,
                        help="Report interval seconds (default 1)")
    parser.add_argument("-r", "--rate", type=int, default=1000,
                        help="(UDP) send rate Kbps (default 1000)")
    parser.add_argument('-l', '--log', type=str, default=None,
                        help='Path to CSV log file (default: None)')

    args = parser.parse_args()
    log = Logger(csv_output=args.log)

    if args.server:
        if args.udp:
            # Task 3/4 (no-op until implemented)
            tester_udp_server(log, args.port, args.rate,
                              args.interval, args.ack)
        else:
            # Task 2 (no-op until implemented)
            tester_tcp_server(log, args.port)
    else:
        if args.udp:
            tester_udp_client(log, args.client, args.port,
                              args.duration, args.interval,
                              args.rate, args.ack)        # Task 3/4 (no-op until implemented)
        else:
            tester_tcp_client(log, args.client, args.port,
                              args.duration, args.interval)  # Task 2 (no-op until implemented)
    log.summary()
    log.close()
