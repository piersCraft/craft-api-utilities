from typing import Any, ClassVar
from enum import Enum
import os
from dotenv import load_dotenv
from pydantic import (
    BaseModel,
    Field,
    computed_field,
    model_serializer,
    model_validator,
    PydanticUndefinedAnnotation,
    field_validator,
)

_ = load_dotenv()


class CompanyIdentifier(Enum):
    """Possible values for company identifier in query variables"""

    DUNS = "duns"
    CRAFT_ID = "id"
    DOMAIN = "domain"


class ApiConfig(BaseModel):
    """Configuration for API client"""

    api_key: str = os.getenv("KEY_CRAFT_SOLENG", "DEFAULT")
    base_url: str = "https://api.craft.co/v1"
    company_id_field: CompanyIdentifier = CompanyIdentifier.CRAFT_ID
    headers: dict[str, str] = {
        "x-craft-api-key": os.getenv("KEY_CRAFT_SOLENG", "DEFAULT"),
        "Content-Type": "application/json",
    }
    query_string: str


class Fragment(BaseModel):
    """GraphQL fragment definition"""

    query_type: str
    name: str
    definition: str
    spread: str


class Fragments(BaseModel):
    """List of GraphQL fragment definitions"""

    fragments: list[Fragment]

    def included_fragments(self, condition) -> list[Fragment]:
        """Select fragments to include"""
        return [fragment for fragment in self.fragments if condition(fragment)]

    @model_serializer(mode="plain")
    def export_graphql(self) -> dict[str, str]:
        """Export fragment definitions and spreads as strings for use in graphQL query"""

        return {
            "definitions": " ".join(
                [fragment.definition for fragment in self.fragments]
            ),
            "spreads": " ".join([fragment.spread for fragment in self.fragments]),
        }


class CraftPayload(BaseModel):
    query: str
    variables: dict[str, str | int]


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


# CRAFT COMPANY
class CurrentCreditRating(BaseModelReplaceNone):
    """Level 2 creditsafe data object"""

    common_value: str | None = Field(default="Not available", alias="commonValue")
    common_description: str | None = Field(
        default="Not available", alias="commonDescription"
    )


class CreditScore(BaseModelReplaceNone):
    """Level 1 creditsafe data object"""

    current_credit_rating: CurrentCreditRating | None = Field(
        default_factory=lambda: CurrentCreditRating(), alias="currentCreditRating"
    )


# Company compliance data
class ComplianceData(BaseModelReplaceNone):
    """Base class with tag transformation."""

    request_status: str | None = Field(default="NOT_REQUESTED", alias="requestStatus")
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


class SecurityRating(BaseModelReplaceNone):
    score: int | None = Field(default=0, alias="score")
    grade: str | None = Field(default="Not Available", alias="grade")
    datetime: str | None = Field(default="Not Available", alias="datetime")


class SustainabilityRating(BaseModelReplaceNone):
    overall: float | None = Field(default=0, alias="overall")
    employee: float | None = Field(default=0, alias="employee")
    environment: float | None = Field(default=0, alias="environment")
    governance: float | None = Field(default=0, alias="governance")
    last_updated_date: str | None = Field(default="Unknown", alias="lastUpdatedDate")


class Period(BaseModelReplaceNone):
    period_type: str | None = Field(default="Unknown", alias="periodType")
    period_end_date: str | None = Field(default="Unknown", alias="endDate")


class Ratios(BaseModelReplaceNone):
    period: Period | None = Field(default_factory=Period, alias="period")
    debt_to_assets_ratio: float | None = Field(default=0, alias="debtToAssetsRatio")
    debt_to_equity_ratio: float | None = Field(default=0, alias="debtToEquityRatio")
    quick_ratio: float | None = Field(default=0, alias="quickRatio")
    current_ratio: float | None = Field(default=0, alias="currentRatio")


class CraftCompany(BaseModelReplaceNone):
    """Primary company object"""

    # FIXED: Using modern Python union syntax with '|'
    id: int | str | None = Field(default=None, alias="id")
    duns: int | str | None = Field(default=None, alias="duns")
    display_name: str = Field(default="None Found", alias="displayName")
    country_of_registration: str = Field(
        default="None Found", alias="countryOfRegistration"
    )
    homepage: str | None = Field(default="None Found", alias="homepage")
    short_description: str | None = Field(
        default="None found", alias="shortDescription"
    )
    company_type: str = Field(default="None Found", alias="companyType")
    credit_score: CreditScore | None = Field(
        default_factory=CreditScore, alias="creditScore"
    )
    compliance_data: ComplianceData | None = Field(
        default_factory=ComplianceData, alias="complianceData"
    )
    security_ratings: list[SecurityRating] | None = Field(
        alias="securityRatings", default_factory=lambda: [SecurityRating()]
    )
    sustainability_rating: SustainabilityRating | None = Field(
        alias="sustainabilityRating", default=None
    )
    # FIXED: Changed from single Ratios object to list of Ratios objects
    financial_ratios: list[Ratios] | None = Field(alias="ratios", default_factory=list)

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_int(cls, v):
        """Convert string ID to integer"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return v  # Keep as string if conversion fails
        return v

    @field_validator("financial_ratios", mode="before")
    @classmethod
    def handle_ratios_array(cls, v):
        """Handle ratios field that can be an empty array or array of objects"""
        if v is None:
            return []
        if isinstance(v, list):
            if len(v) == 0:
                return []
            # Convert each item in the list to a Ratios object
            ratios_list = []
            for item in v:
                if isinstance(item, dict):
                    ratios_list.append(item)  # Let Pydantic handle the conversion
                else:
                    ratios_list.append(item)
            return ratios_list
        return v


class CraftCompanyLite(BaseModelReplaceNone):
    """Lite profile company object"""

    # FIXED: Using modern Python union syntax with '|'
    id: int | str | None = Field(default=None, alias="id")
    display_name: str = Field(default="None Found", alias="displayName")
    homepage: str | None = Field(default="None Found", alias="homepage")
    short_description: str | None = Field(
        default="None found", alias="shortDescription"
    )
    company_type: str = Field(default="None Found", alias="companyType")
    country_of_registration: str = Field(
        default="Not Available", alias="countryOfRegistration"
    )

    @field_validator("id", mode="before")
    @classmethod
    def convert_id_to_int(cls, v):
        """Convert string ID to integer"""
        if v is None:
            return None
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                return v  # Keep as string if conversion fails
        return v


# DNB COMPANY
class DnbPrimaryAddress(BaseModelReplaceNone):
    country_code: str | None = Field(default="Not Available", alias="countryCode")


class DnbBusinessEntityType(BaseModelReplaceNone):
    """Business entity type for D&B company"""

    description: str | None = Field(default="Not Available", alias="description")


class DnbCompanyBase(BaseModelReplaceNone):
    """D&B Company object"""

    duns: str = Field(default="None Found", alias="duns")
    display_name: str | None = Field(default="Not Available", alias="displayName")
    line_of_business: str | None = Field(
        default="Not Available", alias="lineOfBusiness"
    )
    company_type: str | None = Field(default="Not Available", alias="companyType")
    business_entity_type: DnbBusinessEntityType | None = Field(
        default=None, alias="businessEntityType"
    )
    primary_address: DnbPrimaryAddress | None = Field(
        default_factory=DnbPrimaryAddress, alias="primaryAddress"
    )
    craft_company: CraftCompanyLite | None = Field(alias="craftCompany")


class DnbCompany(DnbCompanyBase):
    """D&B Company object"""

    dnb_ultimate_parent: DnbCompanyBase | None = Field(alias="globalUltimateParent")


class CompanyData(BaseModel):
    """API response Data wrapper for a Craft company"""

    company: CraftCompany | None = Field(alias="company")


class Companies(BaseModel):
    dnb_companies: list[CompanyData]


class ApiException(BaseModel):
    variable_key: str | None = None
    data: dict[str, Any] | None = None
    error: str | None = None


class ApiResponse(BaseModel):
    """Top-level API response"""

    data: CompanyData | None = None
    error: str | None = None


class ApiResults(BaseModel):
    """List of responses"""

    results: list[ApiResponse | ApiException | None]
