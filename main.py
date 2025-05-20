import logging

import streamlit as st

from utils.logging_config import setup_logging

st.set_page_config(
    page_title='INP - Report Management System',
    page_icon='images/favicon.ico',
    # layout='wide',  # Usar layout 'wide' para dashboards
    # initial_sidebar_state='expanded',  # Manter sidebar aberta por padrão
)
# st.logo('images/inp_international_news_portugal.png', icon_image='images/favicon.ico')
st.logo('images/inp_international_news_portugal.png', icon_image='images/inp_international_news_portugal.png')

setup_logging()

logger = logging.getLogger(__name__)

# Initialize the Session State
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user' not in st.session_state:
    st.session_state.user = None

# Home page
home_page = st.Page('home.py', title='Home', icon=':material/home:', default=True)

# Authentication pages
login_page = st.Page('auth/login.py', title='Login', icon=':material/login:')
reset_page = st.Page('auth/reset.py', title='Reset Password', icon=':material/key:')
logout_page = st.Page('auth/logout.py', title='Logout', icon=':material/logout:')

auth_pages = [reset_page, logout_page]

# # Reports pages
sales_boards_page = st.Page('reports/sales-boards.py', title='Sales Boards', icon=':material/bar_chart:')

reports_pages = [sales_boards_page]

# Define navigation
page_dict = {}

logger.info(f'User {st.session_state.user} is authenticated: {st.session_state.authenticated}')

if st.session_state.authenticated:
    page_dict['Home'] = [home_page]
    page_dict['Authentication'] = auth_pages
    page_dict['Reports'] = reports_pages
else:
    st.title('INP - Acesso ao Sistema')

    page_dict['Authentication'] = [login_page]

# Execute navigation
pg = st.navigation(page_dict)

pg.run()
