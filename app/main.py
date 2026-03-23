import streamlit as st
import pandas as pd
from fbi_api import FBI

st.set_page_config(
    page_title = "fbi-data-api",
    #page_icon = "",
    layout = "wide",
    initial_sidebar_state = "expanded",
)

def build_client(api_key: str | None) -> FBI:
    return FBI(api_key = api_key if api_key else None)


def render_results(df: pd.DataFrame, export_as: str) -> None:
    '''
    Renders a DataFrame as an interactive table with export button 

    df: Query result.
    export_as: File name (without extension) for the exported .csv.
    '''
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="label">Rows</div>
                <div class="value">{len(df):,}</div>
            </div>
        """, unsafe_allow_html = True)

    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="label">Columns</div>
                <div class="">{len(df.columns)}</div>
            </div>
        """, unsafe_allow_html = True)

    with col3:
        st.download_button(
            label = "Export",
            data = df.to_csv(index = False),
            file_name = f"{export_as}.csv",
            mime = "text/csv",
            use_container_width = True,
        )

    st.markdown("<br>", unsafe_allow_html = True)
    st.dataframe(df, use_container_width = True, hide_index = True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## \U0001F511 Configuration")
    st.markdown('<div class="sidebar-label">API Key</div>', unsafe_allow_html = True)
    api_key_input = st.text_input(
        label = "api_key",
        type = "password",
        label_visibility = "collapsed",
    )
    st.caption("Sign up for a key [here](https://api.data.gov/signup/).")

    st.markdown("---")
    st.markdown("## \U00002139 Quick Reference")

    with st.expander("Offenses"):
        offenses = FBI.get_offenses()
        st.dataframe(
            pd.DataFrame(offenses.items(), columns = ["Offense", "API Mapping"]),
            hide_index = True,
            use_container_width = True,
        )

    with st.expander("State Abbreviations"):
        abbrs = FBI.get_state_abbrs()
        st.dataframe(
            pd.DataFrame(abbrs, columns = ["Abbreviation"]),
            hide_index = True,
            use_container_width = True,
        )

    with st.expander("ORIs in the Major Metro Cities"):
        top_city_oris = pd.DataFrame([
            {"City": "New York City, NY", "ORI": "NY0303000"},
            {"City": "Los Angeles, CA",   "ORI": "CA0194200"},
            {"City": "Chicago, IL",       "ORI": "ILCPD0000"},
            {"City": "Houston, TX",       "ORI": "TXHPD0000"},
            {"City": "Phoenix, AZ",       "ORI": "AZ0072300"},
            {"City": "Philadelphia, PA",  "ORI": "PAPEP0000"},
            {"City": "San Antonio, TX",   "ORI": "TXSPD0000"},
            {"City": "San Diego, CA",     "ORI": "CA0371100"},
            {"City": "Dallas, TX",        "ORI": "TXDPD0000"},
            {"City": "San Jose, CA",      "ORI": "CA0431300"},
        ])
        st.dataframe(top_city_oris, hide_index = True, use_container_width = True)

# Headers
st.markdown("""
<div class="main-header">
    <h1>fbi-data-api Demo</h1>
    <p>This is a demo of <a href="https://pypi.org/project/fbi-data-api/" target="_blank">fbi-data-api</a> (v1.0.0), 
    a Python package for programmatically extracting statistics from 19,000+ law enforcement agencies in the FBI Crime Data API. Before using this dashboard, do not forget to sign-up for an API key (linked in the sidebar): it takes < 1 minute! Feel free to export the queries below for your needs. Better yet, use fbi-data-api directly!</p>
    <p>Visit the <a href="https://github.com/teddythepooh/fbi_api" target="_blank">GitHub repo</a> for issues and suggestions.</p>
</div>
""", unsafe_allow_html = True)

tab_metadata, tab_agency_metadata, tab_stats = st.tabs(["Metadata", "Agency Metadata", "Crime Statistics"])

# Metadata Tab
with tab_metadata:
    st.markdown("### Metadata")
    st.markdown(
        "Get the law enforcement agencies (by state) that report to the Uniform Crime Reporting (UCR) program."
    )

    st.markdown("<br>", unsafe_allow_html = True)

    col_state, col_run = st.columns([3, 1])

    with col_state:
        state_options = ["all"] + FBI.get_state_abbrs()
        selected_state = st.selectbox(
            label = "State",
            options = state_options,
            index = 0,
            help = 'Select a state (or "all") to fetch the metadata.',
        )

    with col_run:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html = True)
        run_metadata = st.button("Run Query", use_container_width = True, type = "primary")

    if run_metadata:
        with st.spinner(f"Fetching agencies for **{selected_state.upper()}**..."):
            try:
                client = build_client(api_key_input)
                df_meta = client.get_metadata(state_abbr = selected_state)

                st.session_state["metadata"] = df_meta
                st.session_state["metadata_state"] = selected_state

            except Exception as e:
                st.error(f"Query failed: {e}")

    if "metadata" in st.session_state:
        state_label = st.session_state["metadata_state"].upper()
        st.success(f"Showing agencies for: **{state_label}**")
        render_results(
            df = st.session_state["metadata"],
            export_as = f"fbi_metadata_{state_label.lower()}",
        )
        
# Agency Metadata Tab
with tab_agency_metadata:
    st.markdown("### Agency Metadata")
    st.markdown(
        "Get the number of officers in a law enforcement agency (ORI) and the total population they serve."
    )

    st.markdown("<br>", unsafe_allow_html = True)

    col_ori, col_run = st.columns([3, 1])

    with col_ori:
        agency_ori_raw = st.text_area(
            label = "Enter one ORI per line. The Quick Reference section outlines the ORIs of the 10 largest US cities.",
            placeholder = "ILCPD0000\nNY0303000",
            height = 120,
        )

    with col_run:
        st.markdown("<div style='height:28px'></div>", unsafe_allow_html = True)
        run_agency = st.button("Run Query", key = "run_agency", use_container_width = True, type = "primary")

    col_year_start, col_year_end = st.columns(2)

    with col_year_start:
        agency_year_start = st.number_input(
            label = "Start Year",
            min_value = 2016,
            max_value = 2024,
            value = 2024,
            step = 1,
            key = "agency_year_start",
        )

    with col_year_end:
        agency_year_end = st.number_input(
            label = "End Year",
            min_value = 2016,
            max_value = 2024,
            value = 2024,
            step = 1,
            key = "agency_year_end",
        )

    agency_ori_list = [o.strip() for o in agency_ori_raw.strip().splitlines() if o.strip()]
    agency_year_list = list(range(int(agency_year_start), int(agency_year_end) + 1))

    if run_agency:
        errors = []

        if not agency_ori_list:
            errors.append("Enter at least one ORI code.")
        if agency_year_start > agency_year_end:
            errors.append("Start Year must be <= End Year.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            with st.spinner(f"Fetching agency metrics for **{len(agency_ori_list)} ORI(s)** ({agency_year_start}–{agency_year_end})..."):
                try:
                    client = build_client(api_key_input)
                    df_agency = client.get_agency_metrics(
                        ori = agency_ori_list,
                        year = agency_year_list,
                    )
                    st.session_state["agency_metrics"] = df_agency
                    st.session_state["agency_metrics_params"] = {
                        "oris": agency_ori_list,
                        "years": agency_year_list,
                    }

                except Exception as e:
                    st.error(f"Query failed: {e}")

    if "agency_metrics" in st.session_state:
        params = st.session_state["agency_metrics_params"]
        year_range = f"{min(params['years'])}-{max(params['years'])}"
        st.success(f"Showing agency metrics for: **{len(params['oris'])} ORI(s)** · **{year_range}**")
        render_results(
            df = st.session_state["agency_metrics"],
            export_as = f"fbi_agency_metrics_{year_range}",
        )

# Crime Statistics Tab
with tab_stats:
    st.markdown("### Crime Statistics")
    st.markdown(
        "Query monthly crime counts by agency (ORI), year, and offense. "
        "The universe of ORIs can be found in the **Metadata** tab."
    )

    st.markdown("<br>", unsafe_allow_html = True)

    col_ori, col_offense = st.columns(2)

    with col_ori:
        ori_raw = st.text_area(
            label = "Enter one ORI per line. The Quick Reference section outlines the ORIs of the 10 largest US cities.",
            placeholder = "CA0190200\nNY0303000",
            height = 120,
            #value = "CA0190200\nNY0303000"
            #help = "Enter one ORI per line.",
        )

    with col_offense:
        offense_options = list(FBI.get_offenses().keys())
        selected_offenses = st.multiselect(
            label = "Offense(s)",
            options = offense_options,
            default = [offense_options[0]],
            help = "Select one or more offenses.",
        )

    col_year_start, col_year_end = st.columns(2)
    
    with col_year_start:
        year_start = st.number_input(
            label = "Start Year",
            min_value = 2016,
            max_value = 2025,
            value = 2024,
            step = 1,
        )

    with col_year_end:
        year_end = st.number_input(
            label = "End Year",
            min_value = 2016,
            max_value = 2025,
            value = 2024,
            step = 1,
        )

    ori_list = [o.strip() for o in ori_raw.strip().splitlines() if o.strip()]
    year_list = list(range(int(year_start), int(year_end) + 1))

    n_queries = len(ori_list) * len(year_list) * len(selected_offenses)
    if ori_list and selected_offenses:
        st.caption(f"This will execute **{n_queries}** quer{'y' if n_queries == 1 else 'ies'}.")

    run_stats = st.button("Run Query", use_container_width = False, type = "primary")

    if run_stats:
        errors = []

        if not ori_list:
            errors.append("Enter at least one ORI code.")
        if not selected_offenses:
            errors.append("Select at least one offense.")
        if year_start > year_end:
            errors.append("Start Year must be <= End Year.")

        if errors:
            for err in errors:
                st.error(err)
        else:
            with st.spinner(f"Executing {n_queries} quer{'y' if n_queries == 1 else 'ies'}..."):
                try:
                    client = build_client(api_key_input)
                    df_stats = client.get_crime_statistics(
                        ori = ori_list,
                        year = year_list,
                        offense = selected_offenses,
                    )
                    st.session_state["stats"] = df_stats
                    st.session_state["stats_params"] = {
                        "oris": ori_list,
                        "years": year_list,
                        "offenses": selected_offenses,
                    }

                except KeyError as e:
                    st.error(f"Invalid offense: {e}")
                except Exception as e:
                    st.error(f"Query failed: {e}")

    if "stats" in st.session_state:
        params = st.session_state["stats_params"]
        year_range = f"{min(params['years'])}-{max(params['years'])}"

        st.success(
            f"Results for **{len(params['oris'])} ORI(s)** · "
            f"**{', '.join(params['offenses'])}** · "
            f"**{year_range}**"
        )

        df_display = st.session_state["stats"]

        # Pivot.
        show_pivot = st.toggle("Pivot by month/year", value = False)
        if show_pivot and not df_display.empty:
            try:
                df_display = df_display.pivot_table(
                    index = ["ori", "offense"],
                    columns = ["year", "month"],
                    values = "count",
                    aggfunc = "sum",
                )
                df_display.columns = [f"{y}-{str(m).zfill(2)}" for y, m in df_display.columns]
                df_display = df_display.reset_index()
            except Exception:
                st.warning("Could not pivot — showing flat table.")
                df_display = st.session_state["stats"]

        filename = f"fbi_crime_stats_{'_'.join(params['offenses'])}_{year_range}"
        render_results(df = df_display, export_as = filename)
