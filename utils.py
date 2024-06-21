from pydantic import BaseModel
from datetime import datetime
import requests
import pandas as pd
import io
import re

class RenovationTier(BaseModel):
    name: str
    description: str
    cost_percentage: float
    weeks: int
    value_increase_percentage: float
    property_quality_id: int

# Define renovation tiers
renovation_tiers = [
    RenovationTier(
        name="Basic",
        description=(
            "Basic renovations typically include cosmetic updates such as painting, minor repairs, updating fixtures, replacing flooring, and light remodeling. These projects are quick and cost-effective.\n\n"
            "Cost Percentage: 5-10% of the property value.\n\n"
            "Duration: 2-4 weeks.\n\n"
            "Value Increase: 10-15% yield."
        ),
        cost_percentage=0.075,
        weeks=3,
        value_increase_percentage=0.125,
        property_quality_id = 2
    ),
    RenovationTier(
        name="Mid-Range",
        description=(
            "Mid-range renovations involve more significant changes such as kitchen and bathroom remodels, new flooring, moderate structural changes, and upgrading appliances. These projects add more functional space and improve the home's livability.\n\n"
            "Cost Percentage: 10-20% of the property value.\n\n"
            "Duration: 4-8 weeks.\n\n"
            "Value Increase: 15-25% yield."
        ),
        cost_percentage=0.15,
        weeks=6,
        value_increase_percentage=0.20,
        property_quality_id = 3
    ),
    RenovationTier(
        name="High-End",
        description=(
            "High-end renovations include major structural changes, extensive remodeling, high-end finishes, and possibly additions. These projects often involve luxury materials and significant improvements to the home's layout and functionality.\n\n"
            "Cost Percentage: 20-40% of the property value.\n\n"
            "Duration: 8-16 weeks or more.\n\n"
            "Value Increase: 25-50% yield."
        ),
        cost_percentage=0.30,
        weeks=12,
        value_increase_percentage=0.375,
        property_quality_id = 4
    )
]

# Create a dictionary for quick lookup
renovation_tiers_dict = {tier.name: tier for tier in renovation_tiers}

def sldt_payload(home_value, holding_type, property_type, is_non_uk_resident, buying_options):
    now = datetime.now()
    payload = {
        "premium": home_value,
        "holdingType": holding_type,
        "propertyType": property_type,
        "effectiveDateDay": now.day,
        "effectiveDateMonth": now.month,
        "effectiveDateYear": now.year,
        "highestRent": 0,
        "nonUKResident": is_non_uk_resident,
        "propertyDetails": {}
    }

    if buying_options == "Company":
        payload["propertyDetails"]["individual"] = "No"
    if buying_options == "Individual - First Time Buyer":
        payload["firstTimeBuyer"] = "Yes"
        payload["propertyDetails"]["individual"] = "Yes"
        payload["propertyDetails"]["twoOrMoreProperties"] = "No"
    if buying_options == "Individual - Multiple - Replaces Residence":
        payload["propertyDetails"]["individual"] = "Yes"
        payload["propertyDetails"]["twoOrMoreProperties"] = "Yes"
        payload["propertyDetails"]["replaceMainResidence"] = "Yes"
    if buying_options == "Individual - Multiple - Not Replaces Residence":
        payload["propertyDetails"]["individual"] = "Yes"
        payload["propertyDetails"]["twoOrMoreProperties"] = "Yes"
        payload["propertyDetails"]["replaceMainResidence"] = "No"

    return payload


def get_sldt(payload):
    url = "https://www.tax.service.gov.uk/calculate-stamp-duty-land-tax/calculate"
    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.json()
    else:
        return {}


def monthly_rate(home_value, ltv, interest_rate, term, is_interest_only):
    loan_amount = home_value * (ltv / 100)
    
    monthly_interest_rate = (interest_rate / 100) / 12
    
    total_payments = term * 12
    
    if is_interest_only:
        monthly_payment = loan_amount * monthly_interest_rate
    else:
        if monthly_interest_rate == 0:
            monthly_payment = loan_amount / total_payments
        else:
            monthly_payment = loan_amount * (monthly_interest_rate * (1 + monthly_interest_rate) ** total_payments) / ((1 + monthly_interest_rate) ** total_payments - 1)
    
    return monthly_payment


def get_current_rate():
    url = "https://www.bankofengland.co.uk/boeapps/database/Bank-Rate.asp"
    r = requests.get(url)

    if r.status_code == 200:
        tables = pd.read_html(io.StringIO(r.text))
        return tables[0].iloc[0, 1]
    return 5.00


property_types = {
    "Flat": 4,
    "House - Terraced": 2,
    "House - End Terrace": 12,
    "House - Semi-Detached": 1,
    "House - Detached": 0
}


def validate_post_code(post_code):
    pattern = re.compile(r'^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$')
    if pattern.match(post_code):
        return True
    return False


def get_estimated_rent(post_code, property_type, bedrooms, bathrooms, property_quality_id):
    property_type_id = property_types[property_type]

    session = requests.Session()
    url = "https://www.openrent.co.uk/rent-calculator-property-value-by-postcode"
    r = session.get(url)
    token_pattern = r'window\.setupAntiForgeryToken\(\s*"<input name=\\"__RequestVerificationToken\\" type=\\"hidden\\" value=\\"([^\"]+)\\"'

    match = re.search(token_pattern, r.text)

    if match:
        token = match.group(1)
    else:
        print("Token not found")

    cookie = f"__RequestVerificationToken={session.cookies.get('__RequestVerificationToken')}"
    headers = {
        "__requestverificationtoken": token,
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": cookie
    }

    payload = {
        "PostCode": post_code,
        "select-address": "Please Select ->",
        "Address1": None,
        "Address2": None,
        "Address3": None,
        "Town": None,
        "PropertyType": property_type_id,
        "Bedrooms": bedrooms,
        "Bathrooms": bathrooms,
        "IsFurnished": False,
        "ListingQuality": 2,
        "PropertyQuality": property_quality_id
    }

    url = "https://www.openrent.co.uk/PricePrediction/PriceWithAssumptions"
    r = session.post(url, headers=headers, data=payload)

    return r.json()