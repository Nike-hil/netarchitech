# NetArchitect (CIC-307)

### Algorithmic Network Planning & Self-Explaining Architecture Engine

NetArchitect is an automated network planning engine that ingests
enterprise topologies, performs boundary-validated physical media
selection, executes non-overlapping bitwise VLSM subnetting, determines
autonomous routing domains, and generates Cisco IOS configuration
templates alongside natural-language architectural justifications.

------------------------------------------------------------------------

## 1. Project Overview

Modern network infrastructure planning requires deterministic validation
across multiple layers of the OSI model. NetArchitect replaces
error-prone manual calculations with an algorithmic decision engine
that:

1.  **Layer 1 -- Physical Media Selection:** Enforces physical
    transmission-distance constraints and selects suitable copper or
    optical media.
2.  **Layer 3 -- Dynamic VLSM Allocation:** Performs ordered subnet
    allocation to prevent overlap and reduce address-space waste.
3.  **Routing Domain Selection:** Selects routing approaches such as
    single-area OSPF, multi-area OSPF, or eBGP based on topology scale
    and network boundaries.
4.  **Explainable Architecture Log:** Produces natural-language
    explanations for key engineering decisions, including relevant
    standards and protocol guidance.
5.  **Cisco IOS Configuration Export:** Generates configuration
    templates for switches, routers, SVIs, 802.1Q trunks, and OSPF
    routing.

------------------------------------------------------------------------

## 2. System Architecture & Project Structure

``` text
netarchitect/
├── profiles/                       # Preset enterprise topology profiles
│   ├── campus_lan.json             # 3 buildings, <400m, 1600 endpoints
│   ├── metro_man.json              # FinTech colocation, 15–35km, dual-homed
│   └── global_wan.json             # 4 cities + cloud VPC, 2000 IoT devices
├── core/
│   ├── __init__.py
│   ├── exceptions.py               # PhysicalDistanceViolationError, SubnetExhaustionError
│   ├── media_engine.py             # Physical media selection and distance rules
│   ├── vlsm_engine.py              # VLSM allocator and wildcard calculation
│   └── routing_engine.py           # OSPF and eBGP domain selection
├── generators/
│   ├── __init__.py
│   └── cisco_ios.py                # Cisco IOS configuration generator
├── exports/                        # Generated Cisco IOS configuration files
│   ├── campus_lan.cfg
│   ├── metro_man.cfg
│   └── global_wan.cfg
├── tests/
│   ├── __init__.py
│   └── test_netarchitect.py        # Automated boundary and edge-case tests
├── ai_audit_log.md                 # Mandatory AI defense and code audit report
├── main.py                         # CLI execution entry point
└── README.md                       # Project documentation
```

*Note: This tree describes the intended project organization. Keep
filenames and paths synchronized with the actual repository.*

------------------------------------------------------------------------

## 3. Supported Preset Profiles

  ------------------------------------------------------------------------------
  Profile       Distance &     Target Endpoints Selected Layer 1  Selected
                Scale                           Media             Routing Domain
  ------------- ------------- ----------------- ----------------- --------------
  **Campus      3 buildings,  1,600 endpoints + Access: Cat6a     Single-area
  LAN**         \<400m                  PoE APs (10GBASE-T);      OSPF (Area
                                                backbone: OM4 MMF 0) +
                                                (10GBASE-SR)      Rapid-PVST

  **Metro MAN** 15--35km             450 users, OS2 single-mode   Single-area
                reach                   FinTech fiber             OSPF + BFD
                                     colocation (10GBASE-LR/ER,   failover /
                                                as supported by   EVPL
                                                the link budget)  

  **Global      4 cities +    2,000 IoT devices OS2 single-mode   eBGP at
  WAN**         cloud VPC            / scanners fiber + IPsec     external
                                                overlays          boundaries +
                                                                  multi-area
                                                                  OSPF
  ------------------------------------------------------------------------------

The selected media and routing approach depend on the actual profile
parameters, supported transceivers, link budgets, and platform
capabilities.

------------------------------------------------------------------------

## 4. Algorithmic Decision Rules

### 4.1 Physical Media Selection (Layer 1)

The media engine evaluates link distance and selects an appropriate
medium:

-   **Up to 100m:** Cat6a copper for supported 10GBASE-T channels.
-   **101m--400m:** OM4 multimode fiber for supported 10GBASE-SR links,
    subject to the applicable optical reach and transceiver
    specifications.
-   **Beyond 400m:** OS2 single-mode fiber, with the optical standard
    and transceiver selected according to the required reach and link
    budget.
-   **Boundary validation:** A copper request exceeding the configured
    channel-distance limit raises `PhysicalDistanceViolationError`.

The 100m copper limit is a channel constraint for the applicable
Ethernet cabling standard; actual supported optical distances vary by
Ethernet standard and transceiver.

### 4.2 Dynamic VLSM Subnet Allocator (Layer 3)

The VLSM engine allocates subnets while validating address-space
boundaries.

-   Sorts host requirements in descending order:

    \[ Req_1 `\ge `{=tex}Req_2
    `\ge `{=tex}`\dots `{=tex}`\ge `{=tex}Req_n \]

-   Determines the required address block using the next suitable power
    of two:

    \[ S = 2\^{`\lceil `{=tex}`\log`{=tex}\_2(H+2) `\rceil`{=tex}} \]

    where (H) is the required number of usable host addresses and the
    additional two addresses account for the network and broadcast
    addresses in conventional IPv4 subnets.

-   Calculates wildcard masks using full 32-bit arithmetic:

    \[ Wildcard = (2\^{32}-1)-Netmask \]

-   Validates subnet boundaries to prevent overlapping allocations.

-   Raises `SubnetExhaustionError` if the requested allocations exceed
    the available parent CIDR address space.

### 4.3 Routing Domain Selection

The routing engine selects a routing approach based on network size and
administrative boundaries:

-   **Single-area OSPF:** Suitable for smaller routed domains where a
    single OSPF area is sufficient.
-   **Multi-area OSPF:** Supports larger internal networks that benefit
    from hierarchical routing.
-   **eBGP:** Used at external autonomous-system boundaries, including
    suitable cloud or service-provider connectivity scenarios.

The generated design should be reviewed against the actual topology,
addressing plan, router capabilities, and routing policy.

------------------------------------------------------------------------

## 5. Getting Started & Execution

### Prerequisites

-   Python 3.10 or later
-   `pytest` for running the automated test suite

Install the test dependency:

``` bash
python -m pip install pytest
```

### Run the Engine

From the project root, execute:

``` bash
python main.py
```

This runs the CLI entry point using the profiles and options supported
by the current implementation and generates the corresponding outputs.

If your current version uses profile arguments, run the appropriate
command, for example:

``` bash
python main.py --profile campus
```

Check `python main.py --help` for the exact supported options.

### Run the Automated Test Suite

``` bash
pytest -v tests/test_netarchitect.py
```

The tests are intended to verify physical-distance validation,
address-space exhaustion, subnet overlap prevention, and wildcard-mask
calculations across non-octet prefix boundaries.

------------------------------------------------------------------------

## 6. Verification in Cisco Packet Tracer / GNS3

Generated configuration files should be treated as deployment templates
and reviewed before use. Confirm interface names, VLAN existence,
platform-specific syntax, routing parameters, and security policy before
applying them to a device.

Useful Cisco IOS verification commands include:

``` cisco
show ip interface brief
show ip route
show ip route ospf
show vlan brief
show interfaces trunk
show ip ospf neighbor
```

For OSPF-enabled links, verify that the expected interfaces participate
in the correct area and that neighboring routers reach the expected
adjacency state.

------------------------------------------------------------------------

## 7. Mandatory AI Defense & Audit Summary

As required by the CIC-307 project specification, AI-generated
suggestions were reviewed rather than accepted without validation. The
detailed findings and remediations are documented in
[`ai_audit_log.md`](ai_audit_log.md).

The audit covers the following incidents:

1.  **OSPF Wildcard Mask Generation:** An AI-generated implementation
    incorrectly placed the wildcard value entirely in the fourth octet,
    producing invalid values such as `0.0.0.1023` for larger wildcard
    masks. The corrected approach uses full 32-bit IPv4 integer
    arithmetic.
2.  **Unconstrained 802.1Q Trunking:** An AI-generated trunk
    configuration omitted explicit VLAN restrictions and retained native
    VLAN 1. The hardened template uses an explicit allowed-VLAN list, an
    unused native VLAN (such as VLAN 999), and `switchport nonegotiate`,
    subject to platform support and topology requirements.
3.  **Physical Media Boundary Validation:** A generic copper
    recommendation did not account for Ethernet channel-distance
    constraints. The design now validates the configured distance limit
    and selects an appropriate fiber option when required.

------------------------------------------------------------------------

## 8. Limitations & Deployment Disclaimer

NetArchitect is an academic network-planning and
configuration-generation project. Generated configurations are starting
points for engineering review, not universally deployable
configurations.

Before deployment:

-   Verify all generated commands against the target Cisco IOS / IOS XE
    version and hardware.
-   Confirm VLAN IDs, interface names, IP addresses, subnet masks, and
    routing areas.
-   Validate optical transceiver compatibility, fiber type, connector
    type, and link budget.
-   Review spanning-tree settings and ensure protections such as root
    guard are applied only where appropriate.
-   Test the resulting topology in Packet Tracer, GNS3, or a suitable
    lab environment before production use.

------------------------------------------------------------------------

## 9. Conclusion

NetArchitect demonstrates how algorithmic network planning can reduce
manual configuration errors and make network-design decisions easier to
inspect. By combining physical-distance validation, VLSM allocation,
routing-domain selection, Cisco IOS configuration generation, and a
mandatory AI audit log, the project provides an explainable foundation
for automated enterprise network planning.

**Course:** CIC-307\
**Project:** NetArchitect\
**Primary Entry Point:** `main.py`\
**AI Audit:** `ai_audit_log.md`
