# Import registry and base classes so they're available at the package level
from dda.registry import registry
from dda.base_dda import BaseDDAAlgorithm

# Import all algorithm implementations to ensure they're registered
# Only importing algorithms that actually exist in the project

from dda.opportunity_dda import OpportunityDDA

# The following modules are referenced but don't exist in the project:
# from dda.threshold_dda import ThresholdDDA
# from dda.static_dda import StaticDDA
# from dda.interval_dda import IntervalDDA
# from dda.metrics_dda import MetricsDDA