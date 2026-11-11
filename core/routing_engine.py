def select_routing_protocol(topology_type: str, subnet_count: int) -> dict:
    if topology_type == "multi_region_cloud" or subnet_count > 50:
        return {
            "protocol": "eBGP + Multi-Area OSPF",
            "areas": ["Area 0 (Backbone)", "Area 10 (Remote Branches)"],
            "rationale": "Selected Multi-Area OSPF and eBGP to isolate routing domains across regions, "
                         "enforce BGP path attributes, and prevent global SPF recalculation storms."
        }
    elif topology_type == "metro_colo":
        return {
            "protocol": "Single-Area OSPF with Dual-Homed BFD Failover",
            "areas": ["Area 0"],
            "rationale": "Selected Single-Area OSPF coupled with Bidirectional Forwarding Detection (BFD) "
                         "to achieve sub-second path failover across Metro Ethernet/EVPL connections."
        }
    else:
        return {
            "protocol": "OSPFv2 Single-Area (Area 0)",
            "areas": ["Area 0"],
            "rationale": "Selected Single-Area OSPF Area 0 because network scale is <50 subnets within a "
                         "single autonomous system, maximizing link-state convergence speed without ABR complexity."
        }