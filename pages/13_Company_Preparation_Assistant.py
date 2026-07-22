import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import streamlit as st
from src import storage
from src.ui import header, provider_badge
from src.career_tools import company_prep

st.set_page_config(page_title="Company Preparation Assistant",  layout="wide")
header(" Company Preparation Assistant", "Get a prep brief tailored to a specific company and role.")

company = st.text_input("Company")
role = st.text_input("Role")

if st.button("Generate prep brief", type="primary", disabled=not (company.strip() and role.strip())):
    with st.spinner("Preparing your brief..."):
        result = company_prep(company, role)
    storage.append_record("company_prep", {"company": company, "role": role, "provider": result["provider"]})
    st.write(result["text"])
    provider_badge(result["provider"])
