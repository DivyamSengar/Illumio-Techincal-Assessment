import csv
import sys
from collections import defaultdict

def main():
    if len(sys.argv) != 3:
        print("Usage: python log_parser.py <lookup_file.csv> <flow_logs.txt>")
        sys.exit(1)

    lookup_file = sys.argv[1]
    flow_logs_file = sys.argv[2]

    # Read protocol mappings from protocols.csv
    protocol_mapping = {}
    try:
        with open('protocols.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row in reader:
                if len(row) < 2:
                    continue
                decimal = row[0].strip()
                keyword = row[1].strip().lower() if row[1].strip() else decimal
                protocol_mapping[decimal] = keyword
    except FileNotFoundError:
        print("Protocols file not found: protocols.csv")
        sys.exit(1)

    # Read lookup CSV
    lookup_dict = {}
    try:
        with open(lookup_file, 'r') as f:
            reader = csv.reader(f)
            next(reader)  # Skip the header line
            for row in reader:
                if len(row) < 3:
                    continue
                dstport, protocol, tag = [field.strip() for field in row[:3]]
                key = (dstport, protocol.lower())
                lookup_dict[key] = tag.lower()
    except FileNotFoundError:
        print(f"Lookup file not found: {lookup_file}")
        sys.exit(1)

    # Process flow logs
    tag_counts = defaultdict(int) 
    port_protocol_counts = defaultdict(int)
    try:
        with open(flow_logs_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 8:
                    continue  # Skip invalid lines
                # Extract destination port and protocol
                dstport = parts[6]
                protocol_num = parts[7]
                protocol_name = protocol_mapping.get(protocol_num, protocol_num)
                # Update port/protocol counts
                port_protocol_key = (dstport, protocol_name)
                port_protocol_counts[port_protocol_key] += 1
                # Check lookup
                lookup_key = (dstport, protocol_name)
                tag = lookup_dict.get(lookup_key, 'untagged')
                tag_counts[tag] += 1
    except FileNotFoundError:
        print(f"Flow logs file not found: {flow_logs_file}")
        sys.exit(1)

    # Write tag counts
    tag_counts_iter = tag_counts.items()
    with open('tag_counts.csv', 'w') as f:
        f.write("Tag Counts:\n")
        f.write("Tag,Count\n")
        for tag, count in tag_counts_iter:
            f.write(f"{tag},{count}\n")

    # Write port/protocol counts, sorted by port as integer, then protocol
    port_protocol_iter = port_protocol_counts.items()
    with open('port_protocol_counts.csv', 'w') as f:
        f.write("Port/Protocol Combination Counts:\n")
        f.write("Port,Protocol,Count\n")
        for (port, proto), count in port_protocol_iter:
            f.write(f"{port},{proto},{count}\n")

if __name__ == '__main__':
    main()