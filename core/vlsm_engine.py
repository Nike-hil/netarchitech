import ipaddress
import math
from core.exceptions import SubnetExhaustionError

def allocate_vlsm(root_cidr: str, host_requests: list[dict]) -> list[dict]:
    # Sort host requests descending
    sorted_requests = sorted(host_requests, key=lambda x: x["hosts_needed"], reverse=True)
    root_net = ipaddress.IPv4Network(root_cidr)
    
    current_ip_int = int(root_net.network_address)
    max_ip_int = int(root_net.broadcast_address)
    allocations = []

    for item in sorted_requests:
        needed = item["hosts_needed"]
        total_required = needed + 2  # Network ID + Directed Broadcast
        host_bits = math.ceil(math.log2(total_required))
        prefix_len = 32 - host_bits
        block_size = 1 << host_bits

        # Natural boundary alignment
        if current_ip_int % block_size != 0:
            current_ip_int = ((current_ip_int // block_size) + 1) * block_size

        if current_ip_int + block_size - 1 > max_ip_int:
            raise SubnetExhaustionError(
                f"Address exhaustion in prefix {root_cidr}: Cannot allocate "
                f"{needed} hosts for '{item['name']}'."
            )

        subnet = ipaddress.IPv4Network((current_ip_int, prefix_len))
        wildcard_int = (1 << 32) - 1 - int(subnet.netmask)
        wildcard_str = str(ipaddress.IPv4Address(wildcard_int))

        allocations.append({
            "name": item["name"],
            "network_ip": str(subnet.network_address),
            "prefix": f"/{prefix_len}",
            "netmask": str(subnet.netmask),
            "wildcard": wildcard_str,
            "default_gateway": str(subnet.network_address + 1),
            "usable_range": f"{subnet.network_address + 1} - {subnet.broadcast_address - 1}",
            "broadcast_ip": str(subnet.broadcast_address),
            "capacity": block_size - 2,
            "utilization": f"{(needed / (block_size - 2)) * 100:.2f}%",
            "rationale": f"Allocated /{prefix_len} ({block_size} total addresses) to satisfy "
                         f"{needed} hosts with minimum residual address waste."
        })

        current_ip_int += block_size

    return allocations