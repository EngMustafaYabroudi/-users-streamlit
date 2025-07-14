import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# === Load and process data ===
@st.cache_data
def load_data():
    df = pd.read_csv("UserReport.csv")
    df.columns = ['Agent Code', 'Agent Name', 'User ID', 'User Name', 'Role']
    df[['Agent Code', 'Agent Name', 'User ID', 'User Name']] = df[['Agent Code', 'Agent Name', 'User ID', 'User Name']].ffill()
    df = df[df['Role'].notna()].reset_index(drop=True)
    return df

df = load_data()

# === Page 1: General statistics ===
def page_statistics():
    st.title("📊 General Statistics")

    num_users = df['User ID'].nunique()
    num_agents = df['Agent Name'].nunique()
    num_roles = df['Role'].nunique()
    users_per_agent = df.groupby('Agent Name')['User ID'].nunique().sort_values(ascending=False)

    st.metric("Total Unique Users", num_users)
    st.metric("Total Unique Agents", num_agents)
    st.metric("Total Unique Roles", num_roles)

    st.subheader("Number of Unique Users per Agent")
    st.dataframe(users_per_agent.rename("Users Count").to_frame(), height=300)

    st.subheader("Role Counts")
    role_counts = df['Role'].value_counts()
    st.dataframe(role_counts.rename("Role Count").to_frame(), height=300)

# === Page 2: Filter by Role ===
def page_filter_by_role():
    st.title("🔍 Filter Users by Role")

    roles = sorted(df['Role'].unique())
    selected_role = st.selectbox("Select a Role", roles)

    if selected_role:
        filtered_df = df[df['Role'] == selected_role]
        users = filtered_df[['User ID', 'User Name', 'Agent Name']].drop_duplicates()

        st.write(f"### Users assigned to role: {selected_role}")
        st.write(f"Total users: {users.shape[0]}")

        gb = GridOptionsBuilder.from_dataframe(users)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        gb.configure_grid_options(domLayout='autoHeight')
        AgGrid(users, gridOptions=gb.build(), fit_columns_on_grid_load=True)

# === Page 3: Filter by User Name ===
def page_filter_by_user():
    st.title("🔎 Filter Roles by User")

    user_names = sorted(df['User Name'].unique())
    selected_user = st.selectbox("Select a User", user_names)

    if selected_user:
        filtered_df = df[df['User Name'] == selected_user]
        roles = filtered_df['Role'].unique()
        st.write(f"### Roles assigned to user: {selected_user}")
        st.write(f"Total roles: {len(roles)}")
        for role in roles:
            st.markdown(f"- {role}")

# === Page 4: Show Users and Roles per Agent ===
def page_agent_users_roles():
    st.title("Agent → Users → Assigned Roles")

    agent_names = df['Agent Name'].dropna().unique()
    selected_agent = st.selectbox("Select an Agent Name", sorted(agent_names))

    if selected_agent:
        df_filtered = df[df['Agent Name'] == selected_agent]

        grouped = df_filtered.groupby(['User Name'])['Role'].unique().reset_index()
        grouped['Roles'] = grouped['Role'].apply(lambda roles: '\n'.join(sorted(roles)))
        grouped['Number of Roles'] = grouped['Role'].apply(len)
        grouped.drop(columns=['Role'], inplace=True)

        st.subheader(f"All users and their assigned roles under agent: {selected_agent}")
        st.write(f"Total users: {grouped.shape[0]}")

        gb = GridOptionsBuilder.from_dataframe(grouped)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
        gb.configure_column("User Name", header_name="User Name", cellStyle={'color': 'black', 'fontWeight': 'bold'}, width=200)
        gb.configure_column("Roles", header_name="Assigned Roles", wrapText=True, autoHeight=True,
                            cellStyle={'color': 'black', 'whiteSpace': 'pre-line'})
        gb.configure_column("Number of Roles", header_name="Number of Roles", width=120,
                            cellStyle={'color': 'black', 'fontWeight': 'bold'})
        gb.configure_grid_options(domLayout='autoHeight')
        gb.configure_grid_options(rowStyle={"background-color": "white"})

        grid_options = gb.build()
        AgGrid(grouped, gridOptions=grid_options, enable_enterprise_modules=False, fit_columns_on_grid_load=True)

# === Page 5: Table of Agent Names and Number of Users ===
def page_agent_user_counts():
    st.title("Agents and Their Number of Users")

    agent_user_counts = df.groupby('Agent Name')['User ID'].nunique().reset_index()
    agent_user_counts.columns = ['Agent Name', 'Number of Users']

    gb = GridOptionsBuilder.from_dataframe(agent_user_counts)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_column("Agent Name", cellStyle={'fontWeight': 'bold'}, width=250)
    gb.configure_column("Number of Users", width=150)
    gb.configure_grid_options(domLayout='autoHeight')
    grid_options = gb.build()

    AgGrid(agent_user_counts, gridOptions=grid_options, enable_enterprise_modules=False, fit_columns_on_grid_load=True)

# === Sidebar Navigation ===
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "Statistics",
    "Filter by Role",
    "Filter by User",
    "Agent Users & Roles",
    "Agents User Counts"
])

if page == "Statistics":
    page_statistics()
elif page == "Filter by Role":
    page_filter_by_role()
elif page == "Filter by User":
    page_filter_by_user()
elif page == "Agent Users & Roles":
    page_agent_users_roles()
else:
    page_agent_user_counts()
