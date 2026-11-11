import json
import sys
from pathlib import Path
from core.media_engine import select_media
from core.vlsm_engine import allocate_vlsm
from core.routing_engine import select_routing_protocol
from generators.cisco_ios import generate_cisco_ios

def process_profile(profile_path: Path):
    with open(profile_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"\n==================================================")
    print(f" Processing: {data['name']}")
    print(f"==================================================")

    # 1. Media Engine
    media = select_media(data["link_distance_m"], data.get("requested_media", "auto"))
    print(f"\n[L1 Media Decision]: {media.media_name}")
    print(f" > Justification: {media.rationale}")

    # 2. Routing Engine
    routing = select_routing_protocol(data["topology_type"], data["num_subnets"])
    print(f"\n[L3 Routing Decision]: {routing['protocol']}")
    print(f" > Justification: {routing['rationale']}")

    # 3. VLSM Engine
    allocations = allocate_vlsm(data["root_prefix"], data["subnets"])
    print(f"\n[VLSM Allocations - Root: {data['root_prefix']}]:")
    for a in allocations:
        print(f" - {a['name']}: {a['network_ip']}{a['prefix']} | Gateway: {a['default_gateway']} | Wildcard: {a['wildcard']} (Eff: {a['utilization']})")

    # 4. Generate & Save Cisco IOS Config
    safe_name = data["name"].lower().replace(" ", "_")
    config_output = generate_cisco_ios(safe_name, media, routing, allocations)
    
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    out_file = export_dir / f"{safe_name}.cfg"
    with open(out_file, "w", encoding="utf-8") as out_f:
        out_f.write(config_output)

    print(f"\n[Export Completed]: Saved deployment configuration to {out_file}")

if __name__ == "__main__":
    profiles_to_run = [
        Path("profiles/campus_lan.json"),
        Path("profiles/metro_man.json"),
        Path("profiles/global_wan.json")
    ]
    for p in profiles_to_run:
        process_profile(p)
