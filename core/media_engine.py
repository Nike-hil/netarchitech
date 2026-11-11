from dataclasses import dataclass
from core.exceptions import PhysicalDistanceViolationError

@dataclass
class MediaDecision:
    media_name: str
    standard: str
    transceiver: str
    rationale: str

def select_media(distance_m: float, requested_media: str = "auto") -> MediaDecision:
    if requested_media == "copper" and distance_m > 100:
        raise PhysicalDistanceViolationError(
            f"Physical Distance Violation: Copper run of {distance_m}m exceeds "
            "the 100m channel attenuation limit defined by IEEE 802.3an."
        )

    if distance_m <= 100:
        return MediaDecision(
            media_name="Cat6a U/FTP Copper",
            standard="10GBASE-T",
            transceiver="10G RJ-45 Copper Transceiver",
            rationale=f"Selected Cat6a Copper because run length ({distance_m}m) is within the "
                      "100m channel transmission limit of IEEE 802.3an."
        )
    elif distance_m <= 400:
        return MediaDecision(
            media_name="OM4 Multimode Fiber (50/125 um)",
            standard="10GBASE-SR",
            transceiver="850nm VCSEL SFP+",
            rationale=f"Selected OM4 Multimode Fiber because link distance ({distance_m}m) exceeds "
                      "the 100m copper limit but remains within the 400m modal dispersion budget at 850nm."
        )
    else:
        return MediaDecision(
            media_name="OS2 Single-Mode Fiber (9/125 um)",
            standard="10GBASE-LR / 10GBASE-ER",
            transceiver="1310nm / 1550nm DFB Laser SFP+",
            rationale=f"Selected OS2 Single-Mode Fiber because link distance ({distance_m}m) exceeds "
                      "the 400m attenuation threshold of OM4 MMF. Zero-water-peak SMF eliminates modal dispersion."
        )
