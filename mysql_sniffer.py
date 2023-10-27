import re
import sys
import argparse
import logging
from scapy.all import *
from datetime import datetime
import time

# Set Scapy's TCP reassembly limit to unlimited
conf.contribs['TCPSession'] = {'reassembler': 'nosack'}

query = b''

def parse_mysql_packet(packet, table_names):
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

            if table_names:
                for table_name in table_names:
                    regex_pattern = r'FROM\s+\b{}\b'.format(table_name)
                    match = re.search(regex_pattern, data, re.IGNORECASE)
                    if match:
                        logger.info(f"{data};")
            else:
                logger.info(f"{data};")

            logger.info("-- --------------------")

def sniff_mysql_packets(port, table_names, runtime=0):
    # 创建一个TCPSession对象
    tcp_session = TCPSession()
    try:
        sniff(filter=f"tcp port {port} and tcp[13] == 24", prn=lambda pkt: parse_mysql_packet(pkt, table_names), session=tcp_session, timeout=runtime)
    except KeyboardInterrupt:
        logger.info("\nSniffing operation stopped")
        sys.exit(0)

# 解析命令行参数
parser = argparse.ArgumentParser(description='MySQL packet sniffer')
parser.add_argument('-p', '--port', type=int, help='MySQL server port', required=True)
parser.add_argument('-t', '--tables', nargs='+', help='Table names to capture')
parser.add_argument('-l', '--log', type=str, default='mysql_packet.sql', help='Log file path')
parser.add_argument('-c', '--console', action='store_true', help='Print log to console')
parser.add_argument('-v', '--version', action='version', version='mysql_sniffer工具版本号: 1.0.3，更新日期：2023-10-27')
parser.add_argument('-r', '--runtime', type=int, help='Runtime of packet sniffing in seconds')
args = parser.parse_args()

port = args.port
table_names = args.tables
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

start_time = time.time()  # 记录抓取开始时间

if table_names:
    try:
        sniff_mysql_packets(port, table_names, args.runtime)
    except KeyboardInterrupt:
        logger.info("\nSniffing operation stopped")
        sys.exit(0)
else:
    logger.info("No table names specified. Capturing all tables...")
    try:
        sniff_mysql_packets(port, [], args.runtime)
    except KeyboardInterrupt:
        logger.info("\nSniffing operation stopped")
        sys.exit(0)

end_time = time.time()  # 记录抓取结束时间
total_time = end_time - start_time  # 计算抓取总时间

logger.info(f"Packet sniffing completed. Total time: {total_time:.2f} seconds.")

