import sys
import argparse
import logging
from scapy.all import *
from datetime import datetime
import time

# Set Scapy's TCP reassembly limit to unlimited
conf.contribs['TCPSession'] = {'reassembler': 'nosack'}

query = b''

def parse_mysql_packet(packet):
    global query
    queries = ['select', 'insert', 'update', 'delete']
    if packet.haslayer(TCP) and packet.haslayer(Raw) and packet[TCP].dport == port:
        payload = bytes(packet[Raw].load)

        if payload[4] == 0x03:
            query = payload[5:]
        else:
            query += payload[5:]

        try:
            data = query.decode('utf-8')
        except UnicodeDecodeError:
            try:
                data = query.decode('latin1')
            except UnicodeDecodeError:
                # If both decodings fail, log the error and return
                logger.error("Failed to decode query")
                return

        words = data.strip().split()
        if words and words[0].lower() in queries:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            source_ip = packet[IP].src
            logger.info(f"-- Time: {current_time}")
            logger.info(f"-- Source IP: {source_ip}")
            logger.info(f"{data};")
            logger.info("-- --------------------")

def sniff_mysql_packets(port, runtime):
    start_time = time.time()  # 记录抓取开始时间
    # 创建一个TCPSession对象
    tcp_session = TCPSession()
    while True:
        # 抓取逻辑
        
        # 检查是否达到抓取持续时间
        elapsed_time = time.time() - start_time
        if elapsed_time >= runtime:
            break

        try:
            sniff(filter=f"tcp port {port} and tcp[13] == 24", prn=parse_mysql_packet, session=tcp_session, timeout=1)
        except KeyboardInterrupt:
            print("\nSniffing operation stopped")
            sys.exit(0)

# 解析命令行参数
parser = argparse.ArgumentParser(description='MySQL packet sniffer')
parser.add_argument('-p', '--port', type=int, help='MySQL server port', required=True)
parser.add_argument('-l', '--log', type=str, default='mysql_packet.sql', help='Log file path')
parser.add_argument('-c', '--console', action='store_true', help='Print log to console')
parser.add_argument('-v', '--version', action='version', version='mysql_sniffer工具版本号: 1.0.2，更新日期：2023-10-26')
parser.add_argument('-r', '--runtime', type=int, help='Runtime of packet sniffing in seconds', required=True)
args = parser.parse_args()

port = args.port
log_file = args.log

# 创建日志记录器
logger = logging.getLogger('mysql_packet_logger')
logger.setLevel(logging.INFO)

# 创建文件输出处理器
file_handler = logging.FileHandler(log_file, 'a')
file_handler.setLevel(logging.INFO)
logger.addHandler(file_handler)

# 如果设置了-c参数，创建并添加终端输出处理器
if args.console:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)

try:
    sniff_mysql_packets(port, args.runtime)
except KeyboardInterrupt:
    print("\nSniffing operation stopped")
    sys.exit(0)

