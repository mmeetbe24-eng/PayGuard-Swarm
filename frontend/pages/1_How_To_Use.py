import sys
from pathlib import Path
import streamlit as st

# Ensure root workspace is on pythonpath
BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from frontend.theme import apply_theme, brand_mark
from frontend.views.guide_view import render_guide_page

st.set_page_config(
    page_title="How to Operate | PayGuard Swarm",
    page_icon=":material/menu_book:",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# Top Navigation Bar
nav_brand, nav_col1, nav_col2, nav_col3 = st.columns([1.3, 1, 1, 1], vertical_alignment="center")
with nav_brand:
    brand_mark()
with nav_col1:
    st.page_link("app.py", label="Back to Live Cockpit")
with nav_col2:
    st.page_link("pages/1_How_To_Use.py", label="How to Operate Guide", disabled=True)
with nav_col3:
    st.page_link("pages/2_About_Us.py", label="About Us & PayPal Synergy", disabled=False)

st.markdown('<div style="height: 1.25rem"></div>', unsafe_allow_html=True)

render_guide_page(link_mode="pages")
