from typing import Any, ClassVar
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    model_validator,
    PydanticUndefinedAnnotation,
)


# GraphQL fragment definitions
class Fragment(BaseModel):
    """GraphQL fragment definition"""

    name: str
    definition: str
    query_string: str


class Fragments(BaseModel):
    """List of GraphQL fragment definitions"""

    fragments: list[Fragment]


# Company creditsafe data


# Base class that handles values of None in fields replacing them with the field default value
class BaseModelReplaceNone(BaseModel):
    """Base class that replaces None with defaults."""

    @model_validator(mode="before")
    @classmethod
    def replace_none_with_defaults(cls, data: Any) -> Any:
        """Replace None values with field defaults."""
        if not isinstance(data, dict):
            return data

        for field_name, field_info in cls.model_fields.items():
            if field_name in data and data[field_name] is None:
                if field_info.default is not PydanticUndefinedAnnotation:
                    data[field_name] = field_info.default

        return data


class CurrentCreditRating(BaseModelReplaceNone):
    """Level 2 creditsafe data object"""

    common_value: str = Field(default="Not available", alias="commonValue")
    common_description: str = Field(default="Not available", alias="commonDescription")


class CreditScore(BaseModelReplaceNone):
    """Level 1 creditsafe data object"""

    current_credit_rating: CurrentCreditRating = Field(
        default_factory=lambda: CurrentCreditRating(), alias="currentCreditRating"
    )


# Company compliance data
class ComplianceEvidence(BaseModelReplaceNone):
    title: str = Field(default="Not Available", alias="title")
    summary: str = Field(default="Not Available", alias="summary")
    credibility: str = Field(default="Not Available", alias="credibility")
    asset_url: str = Field(default="Not Available", alias="assetUrl")
    original_url: str = Field(default="Not Available", alias="originalUrl")
    capture_date: str = Field(default="Not Available", alias="captureDateIso")
    publication_date: str = Field(default="Not Available", alias="publicationDateIso")
    language: str = Field(default="Not Available", alias="language")
    keywords: str = Field(default="Not Available", alias="keywords")


class ComplianceEvent(BaseModelReplaceNone):
    """Level 3 compliance data events"""

    event_type: str = Field(default="Not Available", alias="type")
    currency_code: str = Field(default="Not Available", alias="currencyCode")
    event_date: str = Field(default="Not Available", alias="dateIso")
    evidences: list[ComplianceEvidence] = Field(
        default_factory=list[ComplianceEvidence], alias="evidences"
    )


class ComplianceRelEntry(BaseModelReplaceNone):
    """Level 2 compliance regulatory list entries"""

    category: str = Field(default="Not Available", alias="category")
    subcategory: str = Field(default="Not Available", alias="subcategory")
    events: list[ComplianceEvent] = Field(
        default_factory=list[ComplianceEvent], alias="events"
    )


class ComplianceAdvMediaEntry(BaseModelReplaceNone):
    """Level 2 compliance adverse media entries"""

    category: str = Field(default="Not Available", alias="category")
    subcategory: str = Field(default="Not Available", alias="subcategory")
    events: list[ComplianceEvent] = Field(
        default_factory=list[ComplianceEvent], alias="events"
    )


class ComplianceIndividual(BaseModelReplaceNone):
    """Level 3 compliance linked individual"""

    first_name: str = Field(default="Not Available", alias="firstName")
    last_name: str = Field(default="Not Available", alias="lastName")
    relationship: str = Field(default="Not Available", alias="relationship")
    ownership_percentage: float = Field(default=0, alias="ownershipPercentage")
    datasets: list[str] = Field(default=["None"], alias="datasets")


class CompliancePepEntry(BaseModelReplaceNone):
    """Level 2 compliance pep list entries"""

    position: str = Field(default="Not Available", alias="position")
    segment: str = Field(default="Not Available", alias="segment")
    status: str = Field(default="Not Available", alias="status")
    tier: str = Field(default="Not Available", alias="tier")
    country_code: str = Field(default="Not Available", alias="countryIsoCode")
    date_from: str = Field(default="Not Available", alias="dateFrom")
    date_to: str = Field(default="Not Available", alias="dateTo")
    individual: ComplianceIndividual = Field(
        default_factory=ComplianceIndividual, alias="individual"
    )


class BaseCompliance(BaseModelReplaceNone):
    """Base class with tag transformation."""

    datasets: list[str] = Field(default_factory=list, alias="datasets")
    # Define possible dataset item values and exclude from model export
    POSSIBLE_DATASETS: ClassVar[list[str]] = [
        "RRE",
        "REL",
        "SOE",
        "POI",
        "INS",
        "SAN-CURRENT",
        "SAN-FORMER",
        "PEP-FORMER",
        "PEP-CURRENT",
    ]

    # Create boolean fields for each dataset and set to True if present
    @computed_field
    @property
    def compliance_flag_adverse_media(self) -> bool:
        return "RRE" in self.datasets

    @computed_field
    @property
    def compliance_flag_enforcements(self) -> bool:
        return "REL" in self.datasets

    @computed_field
    @property
    def compliance_flag_state_owned(self) -> bool:
        return "SOE" in self.datasets

    @computed_field
    @property
    def compliance_flag_persons_of_interest(self) -> bool:
        return "POI" in self.datasets

    @computed_field
    @property
    def compliance_flag_current_sanctions(self) -> bool:
        return "SAN-CURRENT" in self.datasets

    @computed_field
    @property
    def compliance_flag_former_sanctions(self) -> bool:
        return "SAN-FORMER" in self.datasets

    @computed_field
    @property
    def compliance_flag_current_peps(self) -> bool:
        return "PEP-CURRENT" in self.datasets

    @computed_field
    @property
    def compliance_flag_former_peps(self) -> bool:
        return "PEP-FORMER" in self.datasets


class ComplianceData(BaseCompliance):
    """Level 1 compliance data object"""

    id: int = Field(default=0, alias="id")


class SecurityRating(BaseModelReplaceNone):
    grade: str = Field(default="Not Available", alias="grade")
    datetime: str = Field(default="Not Available", alias="datetime")


class Company(BaseModelReplaceNone):
    """Primary company object"""

    id: int
    display_name: str = Field(default="None found", alias="displayName")
    homepage: str | None = Field(default="None found", alias="homepage")
    short_description: str | None = Field(
        default="None found", alias="shortDescription"
    )
    company_type: str = Field(default="None found", alias="companyType")
    credit_score: CreditScore = Field(default_factory=CreditScore, alias="creditScore")
    compliance_data: ComplianceData = Field(
        default_factory=ComplianceData, alias="complianceData"
    )
    security_ratings: list[SecurityRating] = Field(
        alias="securityRatings", default_factory=lambda: [SecurityRating()]
    )


class CompanyData(BaseModelReplaceNone):
    """API response Data wrapper"""

    company: Company


class Companies(BaseModelReplaceNone):
    """Flat list of companies"""

    companies: list[Company]


class ApiResponse(BaseModelReplaceNone):
    """Top-level API response"""

    data: CompanyData


class ApiResults(BaseModelReplaceNone):
    """List of responses"""

    results: list[ApiResponse]
