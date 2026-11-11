class PhysicalDistanceViolationError(Exception):
    """Raised when physical transmission constraints are violated."""
    pass

class SubnetExhaustionError(Exception):
    """Raised when total host requirements exceed available address space."""
    pass