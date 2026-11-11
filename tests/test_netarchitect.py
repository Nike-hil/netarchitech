import pytest
import ipaddress
from core.exceptions import PhysicalDistanceViolationError, SubnetExhaustionError
from core.media_engine import select_media
from core.vlsm_engine import allocate_vlsm

def test_copper_distance_boundary_violation():
    """Verify that requesting copper media beyond 100m raises an error."""
    with pytest.raises(PhysicalDistanceViolationError):
        select_media(101, requested_media="copper")

def test_media_selection_tiers():
    """Verify standard transmission thresholds."""
    assert "Cat6a" in select_media(90).media_name
    assert "OM4" in select_media(250).media_name
    assert "OS2" in select_media(1500).media_name

def test_subnet_address_exhaustion():
    """Verify that demanding more hosts than available raises SubnetExhaustionError."""
    greedy_request = [
        {"name": "Subnet_Massive", "hosts_needed": 300}
    ]
    with pytest.raises(SubnetExhaustionError):
        allocate_vlsm("192.168.1.0/24", greedy_request)

def test_vlsm_zero_overlap():
    """Verify mathematically that no generated subnets overlap."""
    requests = [
        {"name": "Net_A", "hosts_needed": 120},
        {"name": "Net_B", "hosts_needed": 60},
        {"name": "Net_C", "hosts_needed": 25}
    ]
    results = allocate_vlsm("10.0.0.0/24", requests)
    allocated_networks = [ipaddress.IPv4Network(f"{r['network_ip']}{r['prefix']}") for r in results]

    for i in range(len(allocated_networks)):
        for j in range(i + 1, len(allocated_networks)):
            assert not allocated_networks[i].overlaps(allocated_networks[j]), \
                f"Overlap detected between {allocated_networks[i]} and {allocated_networks[j]}"

def test_wildcard_mask_calculation():
    """Verify bitwise inverse calculation on non-octet boundary."""
    requests = [{"name": "TestNet", "hosts_needed": 50}]
    results = allocate_vlsm("192.168.1.0/24", requests)
    assert results[0]["prefix"] == "/26"
    assert results[0]["wildcard"] == "0.0.0.63"
