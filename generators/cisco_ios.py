def generate_cisco_ios(hostname: str, media_info, routing_info, allocations) -> str:
    cfg = []
    cfg.append(f"! ===============================================")
    cfg.append(f"! NetArchitect Auto-Generated Config: {hostname}")
    cfg.append(f"! Physical Layer: {media_info.media_name} ({media_info.standard})")
    cfg.append(f"! Protocol: {routing_info['protocol']}")
    cfg.append(f"! ===============================================")
    cfg.append("enable")
    cfg.append("configure terminal")
    cfg.append(f"hostname {hostname}")
    cfg.append("no ip domain-lookup")
    cfg.append("spanning-tree mode rapid-pvst")
    cfg.append("!")

    # VLANs and SVIs
    vlan_id = 10
    for alloc in allocations:
        cfg.append(f"vlan {vlan_id}")
        cfg.append(f" name {alloc['name']}")
        cfg.append(f"interface Vlan{vlan_id}")
        cfg.append(f" description Gateway for {alloc['name']}")
        cfg.append(f" ip address {alloc['default_gateway']} {alloc['netmask']}")
        cfg.append(" no shutdown")
        cfg.append("!")
        vlan_id += 10

    # Routing
    cfg.append("router ospf 1")
    cfg.append(" router-id 1.1.1.1")
    for alloc in allocations:
        cfg.append(f" network {alloc['network_ip']} {alloc['wildcard']} area 0")
    cfg.append("exit")
    cfg.append("!")

    # Trunk Port Hardening
    cfg.append("interface GigabitEthernet0/1")
    cfg.append(" description Backbone Trunk Link")
    cfg.append(" switchport mode trunk")
    cfg.append(" switchport trunk native vlan 999")
    cfg.append(" switchport trunk allowed vlan 10-100")
    cfg.append(" switchport nonegotiate")
    cfg.append(" no shutdown")
    cfg.append("!")
    cfg.append("end")
    cfg.append("write memory\n")

    return "\n".join(cfg)