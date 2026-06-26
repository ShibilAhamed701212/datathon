import streamlit as st
import requests
import json
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="KSP Crime Intelligence Copilot", page_icon="🛡️", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "lang" not in st.session_state:
    st.session_state.lang = "en"
if "session_context" not in st.session_state:
    st.session_state.session_context = []

def call_api(endpoint, method="GET", data=None, files=None, params=None):
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            resp = requests.get(url, params=params, timeout=15)
        elif method == "POST" and files:
            resp = requests.post(url, files=files, timeout=30)
        elif method == "POST":
            resp = requests.post(url, json=data, timeout=30)
        else:
            return {"error": "Unsupported method"}
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"API error {resp.status_code}: {resp.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to backend. Ensure the API server is running."}
    except Exception as e:
        return {"error": str(e)}

st.sidebar.title("🛡️ KSP Crime Copilot")
st.sidebar.markdown("---")

lang_labels = {"en": "English", "kn": "ಕನ್ನಡ"}
lang_map = {"English": "en", "ಕನ್ನಡ": "kn"}
selected_lang = st.sidebar.selectbox(
    "Language / ಭಾಷೆ",
    options=["English", "ಕನ್ನಡ"],
    index=0 if st.session_state.lang == "en" else 1
)
st.session_state.lang = lang_map[selected_lang]

st.sidebar.markdown("---")
llm_mode = st.sidebar.selectbox(
    "LLM Mode",
    options=["mock", "openai", "gemini"],
    index=0,
    help="mock: uses template response, openai: requires OPENAI_API_KEY, gemini: requires GEMINI_API_KEY"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Actions")
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []
    st.session_state.session_context = []
    st.rerun()

if st.sidebar.button("Export Chat to PDF"):
    if st.session_state.messages:
        conv = [{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages]
        result = call_api("/api/pdf_chat", method="POST", data={"conversation": conv, "title": "KSP Copilot Chat Export"})
        if "error" not in result and isinstance(result, dict):
            pdf_url = f"{API_BASE}/api/pdf_chat"
            st.sidebar.success("Chat exported. Check backend logs or direct download.")
            st.sidebar.markdown(f"Download: [Chat PDF]({pdf_url})")
        else:
            st.sidebar.error(f"Export failed: {result.get('error')}")
    else:
        st.sidebar.warning("No messages to export.")

st.sidebar.markdown("---")
st.sidebar.markdown("**ℹ️ Demo Prototype**")
st.sidebar.markdown("Data is synthetic. Built for KSP Hackathon.")

tab_chat, tab_dashboard, tab_graph, tab_summary = st.tabs(
    ["💬 Chat", "📊 Analytics", "🔗 Network Graph", "📄 Case Summary"]
)

with tab_chat:
    st.title("💬 Crime Query Copilot")
    st.markdown("Ask questions about crimes in Karnataka. Supports English and Kannada.")

    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "sources" in msg and msg["sources"]:
                    st.caption(f"Sources: FIR #{', #'.join(str(s) for s in msg['sources'])}")

    prompt_placeholder = "Ask about crime data..." if st.session_state.lang == "en" else "ಅಪರಾಧ ಡೇಟಾ ಕುರಿತು ಕೇಳಿ..."
    if prompt := st.chat_input(prompt_placeholder):
        st.session_state.messages.append({"role": "user", "content": prompt, "sources": []})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing crime data..."):
                result = call_api("/api/query", method="POST", data={
                    "question": prompt,
                    "lang": st.session_state.lang,
                    "llm_mode": llm_mode
                })
                if "error" in result:
                    answer = f"❌ {result['error']}"
                    sources = []
                else:
                    answer = result.get("answer", "No answer generated.")
                    sources = result.get("source_ids", [])

                st.markdown(answer)
                if sources:
                    st.caption(f"Sources: FIR #{', #'.join(str(s) for s in sources)}")

                st.session_state.messages.append({
                    "role": "assistant", "content": answer, "sources": sources
                })

with tab_dashboard:
    st.title("📊 Crime Analytics Dashboard")
    with st.spinner("Loading analytics..."):
        stats = call_api("/api/stats")

    if "error" in stats:
        st.error(stats["error"])
    else:
        col1, col2, col3, col4 = st.columns(4)
        if stats.get("crimes_by_type"):
            total_firs = sum(item["count"] for item in stats["crimes_by_type"])
            col1.metric("Total FIRs", total_firs)
        if stats.get("crimes_by_type"):
            top_type = max(stats["crimes_by_type"], key=lambda x: x["count"])
            col2.metric("Top Crime", f"{top_type['crime_type']} ({top_type['count']})")
        if stats.get("crimes_by_district"):
            top_dist = max(stats["crimes_by_district"], key=lambda x: x["count"])
            col3.metric("Top District", f"{top_dist['district']} ({top_dist['count']})")
        if stats.get("repeat_offenders"):
            col4.metric("Repeat Offenders", len(stats["repeat_offenders"]))

        st.subheader("Crimes by Type")
        if stats.get("crimes_by_type"):
            df = pd.DataFrame(stats["crimes_by_type"])
            st.bar_chart(df.set_index("crime_type"))

        st.subheader("Crimes by District")
        if stats.get("crimes_by_district"):
            df = pd.DataFrame(stats["crimes_by_district"])
            st.bar_chart(df.set_index("district"))

        st.subheader("Crime Trend (Monthly)")
        if stats.get("crimes_by_month"):
            df = pd.DataFrame(stats["crimes_by_month"])
            st.line_chart(df.set_index("month"))

        st.subheader("Repeat Offenders")
        if stats.get("repeat_offenders"):
            df = pd.DataFrame(stats["repeat_offenders"])
            st.dataframe(df, width='stretch')

with tab_graph:
    st.title("🔗 Criminal Network Graph")
    st.markdown("Visualizing relationships between suspects, victims, and cases.")

    person_filter = st.text_input("Filter by person name (optional)", value="")

    with st.spinner("Loading network data..."):
        params = {"person": person_filter} if person_filter else None
        graph_data = call_api("/api/graph", params=params)

    if "error" in graph_data:
        st.error(graph_data["error"])
    else:
        nodes = graph_data.get("nodes", [])
        edges = graph_data.get("edges", [])

        st.write(f"**Nodes:** {len(nodes)} | **Edges:** {len(edges)}")

        if nodes:
            import networkx as nx
            G = nx.Graph()
            for n in nodes:
                G.add_node(n["id"], label=n.get("label", n["id"]), type=n.get("type", "unknown"))
            for e in edges:
                G.add_edge(e["source"], e["target"], role=e.get("role", "unknown"))

            node_df = pd.DataFrame(nodes)
            edge_df = pd.DataFrame(edges)

            st.subheader("Node Details")
            st.dataframe(node_df[["id", "label", "type"]], width='stretch')

            st.subheader("Edge Details")
            if not edge_df.empty:
                st.dataframe(edge_df, width='stretch')

            st.subgraph_chart = None
            try:
                import streamlit.components.v1 as components
                from networkx.readwrite import json_graph
                data = json_graph.node_link_data(G)
                html = f"""
                <html><body>
                <h3>Network Graph</h3>
                <pre>{json.dumps(data, indent=2)[:2000]}...</pre>
                </body></html>
                """
                st.markdown(html, unsafe_allow_html=True)
            except Exception:
                st.info("Interactive graph visualization available with streamlit-cytoscapejs.")

            st.subheader("Adjacency List")
            for node in G.nodes():
                neighbors = list(G.neighbors(node))
                if neighbors:
                    st.text(f"{node}: {', '.join(neighbors[:8])}")
        else:
            st.info("No graph data available.")

with tab_summary:
    st.title("📄 Case Summary Generator")
    st.markdown("Generate a PDF summary for any FIR case.")

    fir_id_input = st.number_input("Enter FIR ID (101-115)", min_value=101, max_value=115, value=101, step=1)

    if st.button("Generate Summary", type="primary", width='stretch'):
        with st.spinner("Generating case summary..."):
            fir_detail = call_api(f"/api/firs/{fir_id_input}")

        if "error" in fir_detail:
            st.error(fir_detail["error"])
        else:
            fir = fir_detail.get("fir", {})
            persons = fir_detail.get("persons", [])

            st.subheader(f"FIR #{fir.get('fir_id', 'N/A')}")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Date:** {fir.get('date', 'N/A')}")
                st.write(f"**Crime Type:** {fir.get('crime_type', 'N/A')}")
                st.write(f"**Location:** {fir.get('location', 'N/A')}")
            with col2:
                st.write(f"**District:** {fir.get('district', 'N/A')}")
                st.write(f"**Status:** {fir.get('status', 'N/A')}")
            st.write(f"**Description:** {fir.get('description', 'N/A')}")

            if persons:
                st.subheader("Involved Persons")
                df = pd.DataFrame(persons)
                display_cols = [c for c in ["person_name", "role", "age", "gender", "address"] if c in df.columns]
                st.dataframe(df[display_cols] if display_cols else df, width='stretch')

            st.markdown("---")
            pdf_result = call_api("/api/pdf_summary", method="POST", data={"fir_id": fir_id_input})
            if "error" not in pdf_result:
                st.success(f"PDF summary for FIR #{fir_id_input} generated successfully!")
                st.markdown(f"Download: `fir_{fir_id_input}_summary.pdf`")
            else:
                st.warning(f"PDF generation note: {pdf_result.get('error')}")

st.markdown("---")
st.caption("KSP Crime Intelligence Copilot — Hackathon Prototype | Data is synthetic")
