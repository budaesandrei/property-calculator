import streamlit as st
import math
from utils import *


st.set_page_config(
    page_title="Property Calculator",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


load_css("style.css")


def get_initial_rate():
    if 'current_rate' not in st.session_state:
        st.session_state.current_rate = get_current_rate()


get_initial_rate()


st.title("🏡 Property Calculator")

with st.container(border=True):
    st.subheader("Basic Information", anchor="basic-info")
    col1, col2, col3, col4 = st.columns(4)
    col1.selectbox("Holding Type", options=["Freehold", "Leasehold"], index=0, key="holding_type", disabled=True)
    col2.selectbox("Building Type", options=["Residential", "Non-residential"], index=0, key="building_type", disabled=True)
    col3.selectbox("Non-UK Resident", options=["No", "Yes"], index=0, key="is_non_uk_resident")
    col4.selectbox("Buying Options", options=["Company", "Individual - First Time Buyer", "Individual - Multiple - Replaces Residence", "Individual - Multiple - Not Replaces Residence"], index=0, key="buying_options")
    col1.text_input("Post Code", key="post_code", help="Enter the post code of the property.", placeholder="e.g. SW1A 1AA").upper()
    if st.session_state.post_code and not validate_post_code(st.session_state.post_code):
        st.error("Invalid post code. Please enter a valid UK post code.")
    col2.selectbox("Property Type", options=property_types.keys(), index=1, key="property_type")
    col3.number_input("# Bedrooms", key="bedrooms", min_value=0, value=2)
    col4.number_input("# Bathrooms", key="bathrooms", min_value=0, value=1)

main_col1, main_col2 = st.columns(2)

with main_col1:
    with st.container(border=True):
        st.subheader(f"💰 Mortgage", anchor="mortgage")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.number_input("Home Value (£)", key="home_val_aq", min_value=0, value=125000)
        col2.number_input("LTV (%)", key="ltv_aq", min_value=0.0, max_value=100.0, value=75.0)
        col3.number_input("Interest Rate (%)", key="rate_aq", min_value=0.0, max_value=100.0, value=st.session_state.current_rate)
        col4.number_input("Term (years)", key="term_aq", min_value=0, max_value=100, value=35)
        col5.checkbox("Interest Only", key="is_interest_only_aq", value=True)
        st.session_state.monthly_rate_aq = monthly_rate(st.session_state.home_val_aq, st.session_state.ltv_aq, st.session_state.rate_aq, st.session_state.term_aq, st.session_state.is_interest_only_aq)
        col5.markdown(f"💡 £ {st.session_state.monthly_rate_aq:,.2f} /month")


with main_col2:
    with st.container(border=True):
        st.subheader("🛒 Acquisition", anchor="acquisition")
        col1, col2, col3, col4 = st.columns(4)
        col1.number_input("Broker Fee (£)", key="broker", min_value=0.0, value=600.0)
        col2.number_input("Solicitor Fee (£)", key="solicitor", min_value=0.0, value=800.0)
        col3.number_input("Sourcing Fee (£)", key="sourcing_fee", min_value=0.0, value=0.0)
        col4.number_input("Other Fees (£)", key="other_fees", min_value=0.0, value=0.0, help="Do not include stamp duty or deposits here.")


with main_col1:
    with st.container(border=True):
        st.subheader("🛠 Renovation", anchor="renovation")
        col1, col2, col3, col4 = st.columns(4)
        col1.selectbox("Renovation Tier", key="renovation_tier", options=renovation_tiers_dict, index=0, help="\n\n".join([x.description for x in renovation_tiers]))
        renovation_tier = [x for x in renovation_tiers if x.name == st.session_state.renovation_tier][0]
        col2.number_input("Renovation Costs (£)", key="renovation_cost", min_value=0.0, value=renovation_tier.cost_percentage * st.session_state.home_val_aq, help="The below is only for reference. Adjust as needed.")
        col3.number_input("Vacant Period (weeks)", key="vacant_period", min_value=0, value=renovation_tier.weeks, help="The below is only for reference. Adjust as needed.")
        col4.number_input("Value Increase (%)", key="value_increase", min_value=0.0, value=renovation_tier.value_increase_percentage * st.session_state.home_val_aq, help="The below is only for reference. Adjust as needed.")


with main_col2:
    with st.container(border=True):
        st.subheader(f"🏦 Remortgage", anchor="remortgage")
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.number_input("New Home Value (£)", key="home_val_rm", min_value=0.0, value=st.session_state.home_val_aq + st.session_state.value_increase)
        col2.number_input("LTV (%)", key="ltv_rm", min_value=0.0, max_value=100.0, value=75.0)
        col3.number_input("Interest Rate (%)", key="rate_rm", min_value=0.0, max_value=100.0, value=st.session_state.rate_aq)
        col4.number_input("Term (years)", key="term_rm", min_value=0, max_value=100, value=st.session_state.term_aq)
        col5.checkbox("Interest Only", key="is_interest_only_rm", value=st.session_state.is_interest_only_aq)
        st.session_state.monthly_rate_rm = monthly_rate(st.session_state.home_val_rm, st.session_state.ltv_rm, st.session_state.rate_rm, st.session_state.term_rm, st.session_state.is_interest_only_rm)
        col5.markdown(f"💡 £ {st.session_state.monthly_rate_rm:,.2f} /month")


with st.container(border=True):
    st.subheader("🔧 Utilities (monthly)", anchor="utilities")
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)
    col1.number_input("Gas (£)", key="gas", min_value=0.0, value=50.0)
    col2.number_input("Electricity (£)", key="electricity", min_value=0.0, value=50.0)
    col3.number_input("Water (£)", key="water", min_value=0.0, value=50.0)
    col4.number_input("Council Tax (£)", key="council_tax", min_value=0.0, value=100.0)
    col5.number_input("Insurance (£)", key="insurance", min_value=0.0, value=50.0)
    col6.number_input("Service Charge (£)", key="service_charge", min_value=0.0, value=0.0)
    col7.number_input("Ground Rent (£)", key="ground_rent", min_value=0.0, value=0.0)
    col8.number_input("Other (£)", key="other_utilities", min_value=0.0, value=0.0)

st.header("🧮 Summary")

with st.container():
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    payload = sldt_payload(st.session_state.home_val_aq, st.session_state.holding_type, st.session_state.building_type, st.session_state.is_non_uk_resident, st.session_state.buying_options)
    sdlt_response = get_sldt(payload)
    sdlt = sdlt_response.get("result", [{}])[0]
    sdlt_val = sdlt.get('totalTax', None)
    monthly_rate_aq = monthly_rate(st.session_state.home_val_aq, st.session_state.ltv_aq, st.session_state.rate_aq, st.session_state.term_aq, st.session_state.is_interest_only_aq)
    col1.metric("Stamp Duty Land Tax", value=f"£ {sdlt_val:,.2f}")

    deposit = math.ceil(st.session_state.home_val_aq * (100 - st.session_state.ltv_aq) / 100)
    col2.metric("Deposit", value=f"£ {deposit:,.2f}")

    aquisition = sum([st.session_state.broker, st.session_state.solicitor, st.session_state.sourcing_fee, st.session_state.other_fees]) * 2 # For both purchase and remortgage
    col3.metric("Acquisition Costs", value=f"£ {aquisition:,.2f}", help="Includes broker, solicitor, sourcing, and other fees multiplied by 2 (purchase and remortgage).")

    renovation = st.session_state.renovation_cost
    col4.metric("Renovation Costs", value=f"£ {renovation:,.2f}")

    mortgage_waste = st.session_state.vacant_period / 4 * st.session_state.monthly_rate_aq
    col5.metric("Mortgage Waste", value=f"£ {mortgage_waste:,.2f}", help="The amount of money wasted on mortgage payments during the renovation period.")

    utilities_waste = sum([st.session_state.gas, st.session_state.electricity, st.session_state.water, st.session_state.council_tax, st.session_state.insurance, st.session_state.service_charge, st.session_state.ground_rent, st.session_state.other_utilities]) * st.session_state.vacant_period / 4
    col6.metric("Utilities Waste", value=f"£ {utilities_waste:,.2f}", help="The amount of money wasted on utilities during the renovation period.")

    investment_cost = sum([sdlt_val, deposit, aquisition, renovation, mortgage_waste, utilities_waste])
    col7.metric("Total Investment", value=f"£ {investment_cost:,.2f}")

    investment_w_deposit = sum([sdlt_val, aquisition, renovation, mortgage_waste, utilities_waste])
    col8.metric("Total Investment (w/o Deposit)", value=f"£ {investment_w_deposit:,.2f}")


with st.container():
    col1, col2, col3, col4, col5, col6, col7, col8 = st.columns(8)

    capital_recovered = (st.session_state.home_val_rm * st.session_state.ltv_rm / 100) - (st.session_state.home_val_aq * st.session_state.ltv_aq / 100)
    col1.metric("Capital Recovered", value=f"£ {capital_recovered:,.2f}", help="The amount of capital recovered from the remortgage.")

    remaining_investment = investment_cost - capital_recovered
    col2.metric("Remaining Investment", value=f"£ {remaining_investment:,.2f}")

    estimated_rent = get_estimated_rent(st.session_state.post_code, st.session_state.property_type, st.session_state.bedrooms, st.session_state.bathrooms, renovation_tier.property_quality_id)
    bounds = estimated_rent.get("Estimate", {})
    low_est_rent = bounds.get("RoundedLowerBound", 0)
    avg_est_rent = bounds.get("RoundedEstimate", 0)
    high_est_rent = bounds.get("RoundedUpperBound", 0)
    annual_rent = avg_est_rent * 12
    col3.metric("Annual Rent", value=f"£ {annual_rent:,.2f}", help=f"Estimated rent for the property in the {st.session_state.post_code} area.\n\n**Monthly**: Low: £ {low_est_rent:,.2f}, Avg: £ {avg_est_rent:,.2f}, High: £ {high_est_rent:,.2f}")

    noi = annual_rent - sum([st.session_state.insurance, st.session_state.service_charge, st.session_state.ground_rent, st.session_state.monthly_rate_rm * 12])
    col4.metric("Net Operating Income (NOI)", value=f"£ {noi:,.2f}", help="The net operating income after deducting expenses.")

    roe = annual_rent / remaining_investment
    col5.metric("Gross ROE", value=f"{roe:.2%}", help="The return on equity.")

    net_roe = noi / remaining_investment
    col6.metric("Net ROE", value=f"{net_roe:.2%}", help="The net return on equity.")

    roi = annual_rent / (st.session_state.home_val_rm + investment_w_deposit)
    col7.metric("Gross ROI", value=f"{roi:.2%}", help="The return on investment.")

    net_roi = noi / (st.session_state.home_val_rm + investment_w_deposit)
    col8.metric("Net ROI", value=f"{net_roi:.2%}", help="The net return on investment.")
    