"""Provider-neutral task profiles used to compare synthetic AI candidates."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TextTaskProfile:
    """A versioned text task and its human-scored quality dimensions."""

    profile_id: str
    task_id: str
    output_contract_id: str
    minimum_repetitions_per_case: int
    manual_review_dimensions: tuple[str, ...]


CREATIVE_COPY_PROFILE = TextTaskProfile(
    profile_id="creative-copy-v1",
    task_id="campaign-copy-generation",
    output_contract_id="creative-variants-v1",
    minimum_repetitions_per_case=3,
    manual_review_dimensions=(
        "usefulness",
        "source-grounding",
        "variant-diversity",
        "brand-fit",
        "correction-effort",
    ),
)

# Separate offline brand-bound envelope; no provider or production promotion.
BRAND_COPY_PROFILE = TextTaskProfile(
    profile_id="brand-copy-candidate-v1",
    task_id="brand-bound-copy-candidate",
    output_contract_id="brand-copy-task-result-v1",
    minimum_repetitions_per_case=3,
    manual_review_dimensions=CREATIVE_COPY_PROFILE.manual_review_dimensions,
)
