import streamlit as st
import pandas as pd
import os

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="Complaint Management System",
    layout="centered"
)

DATA_PATH = "data/complaints.csv"

# ------------------ ADMIN CREDENTIALS (Demo) ------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# ------------------ LIGHT THEME CSS ------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #f5f7fb;
        color: #1f2937;
    }

    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e5e7eb;
    }

    h1, h2, h3 {
        color: #1f2937;
    }

    .card {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        text-align: center;
    }

    section[data-testid="stForm"] {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }

    input, textarea, select {
        border-radius: 8px !important;
    }

    button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border-radius: 8px !important;
        font-weight: 600;
    }

    button[kind="primary"]:hover {
        background-color: #1d4ed8 !important;
    }

    div[data-testid="stDataFrame"] {
        background-color: #ffffff;
        border-radius: 14px;
        padding: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ Helper Functions ------------------

def load_data():
    if os.path.exists(DATA_PATH):
        df = pd.read_csv(DATA_PATH)
    else:
        df = pd.DataFrame(columns=["name", "issue_type", "description", "priority", "status"])

    if "priority" not in df.columns:
        df["priority"] = "Medium"
    if "status" not in df.columns:
        df["status"] = "Open"

    return df


def save_data(df):
    df.to_csv(DATA_PATH, index=False)


def style_priority(val):
    if val == "High":
        return "background-color:#fee2e2"
    elif val == "Medium":
        return "background-color:#fef3c7"
    else:
        return "background-color:#dcfce7"


def style_status(val):
    if val == "Resolved":
        return "color:#16a34a;font-weight:bold"
    else:
        return "color:#dc2626;font-weight:bold"


# ------------------ Session State ------------------

if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False


# ------------------ App Header ------------------

st.markdown(
    "<h1 style='text-align:center;'>📝 Complaint & Issue Management</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:#6b7280;'>Track, prioritize, and resolve issues efficiently</p>",
    unsafe_allow_html=True
)
st.divider()

menu = st.sidebar.radio("Navigation", ["Raise Complaint", "Admin Dashboard"])
df = load_data()

# ------------------ Raise Complaint ------------------

if menu == "Raise Complaint":
    st.subheader("Raise a Complaint")

    with st.form("complaint_form"):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Your Name")

        with col2:
            issue_type = st.selectbox(
                "Issue Type",
                ["Technical", "Infrastructure", "Academic", "Other"]
            )

        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        description = st.text_area("Describe the issue")

        submit = st.form_submit_button("Submit Complaint")

        if submit:
            if name.strip() == "" or description.strip() == "":
                st.warning("Please fill all required fields.")
            else:
                new_data = {
                    "name": name,
                    "issue_type": issue_type,
                    "description": description,
                    "priority": priority,
                    "status": "Open"
                }
                df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
                save_data(df)
                st.success("Complaint submitted successfully!")

# ------------------ Admin Dashboard ------------------

else:
    if not st.session_state.admin_logged_in:
        st.subheader("Admin Login")

        with st.form("admin_login"):
            username = st.text_input("Admin ID")
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login")

            if login:
                if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                    st.session_state.admin_logged_in = True
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

    else:
        # ---- Top Bar (Title + Logout) ----
        col_title, col_logout = st.columns([6, 1])

        with col_title:
            st.markdown(
                "<h2 style='margin-bottom:0;'>Admin Dashboard</h2>",
                unsafe_allow_html=True
            )

        with col_logout:
            if st.button("Logout", type="primary"):
                st.session_state.admin_logged_in = False
                st.rerun()

        st.divider()

        if df.empty:
            st.info("No complaints submitted yet.")
        else:
            # Dashboard Cards
            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(
                    f"<div class='card'><h2>{len(df)}</h2><p>Total</p></div>",
                    unsafe_allow_html=True
                )

            with col2:
                st.markdown(
                    f"<div class='card' style='background:#fff7ed;'><h2>{len(df[df['status']=='Open'])}</h2><p>Open</p></div>",
                    unsafe_allow_html=True
                )

            with col3:
                st.markdown(
                    f"<div class='card' style='background:#ecfeff;'><h2>{len(df[df['status']=='Resolved'])}</h2><p>Resolved</p></div>",
                    unsafe_allow_html=True
                )

            st.divider()

            search_term = st.text_input("Search by name or description")
            status_filter = st.selectbox("Filter by Status", ["All", "Open", "Resolved"])

            filtered_df = df.copy()

            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["status"] == status_filter]

            if search_term.strip():
                filtered_df = filtered_df[
                    filtered_df["name"].str.contains(search_term, case=False, na=False) |
                    filtered_df["description"].str.contains(search_term, case=False, na=False)
                ]

            priority_order = {"High": 1, "Medium": 2, "Low": 3}
            filtered_df["rank"] = filtered_df["priority"].map(priority_order)
            filtered_df = filtered_df.sort_values("rank").drop(columns="rank")

            styled_df = filtered_df.style.applymap(style_priority, subset=["priority"]) \
                                          .applymap(style_status, subset=["status"])

            st.dataframe(styled_df, use_container_width=True)

            st.divider()
            st.markdown("### Update Complaint Status")

            idx = st.number_input(
                "Enter complaint index",
                min_value=0,
                max_value=len(df) - 1,
                step=1
            )

            new_status = st.selectbox("Change status to", ["Open", "Resolved"])

            if st.button("Update Status"):
                df.at[idx, "status"] = new_status
                save_data(df)
                st.success("Status updated successfully!")
