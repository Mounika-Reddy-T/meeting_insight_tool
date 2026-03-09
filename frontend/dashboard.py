import streamlit as st
import requests

API_ENDPOINT = "http://localhost:8000/analyze-document"

st.set_page_config(
    page_title="AI Text Insight Tool",
    layout="wide"
)

st.title("AI Document Analyzer")

st.write(
    "Paste a long document, meeting transcript, or notes. "
    "The system will summarize it and extract tasks and decisions."
)

st.caption("Tip: Include speaker names and clear meeting context for better extraction quality.")

text_data = st.text_area("Input Document", height=300, placeholder="Paste meeting transcript or notes...")

analyze = st.button("Run Analysis")


def render_items(title: str, items: list[str], empty_message: str) -> None:
    st.subheader(title)
    if items:
        for idx, item in enumerate(items, start=1):
            st.markdown(f"{idx}. {item}")
    else:
        st.info(empty_message)


if analyze:

    if text_data.strip() == "":
        st.warning("Please provide some text")
    else:

        with st.spinner("Analyzing text..."):
            try:
                response = requests.post(
                    API_ENDPOINT,
                    json={"text": text_data},
                    timeout=90
                )
            except requests.RequestException as exc:
                st.error(f"Failed to reach backend API: {exc}")
                st.stop()

            try:
                result = response.json()
            except ValueError:
                st.error(
                    f"Backend returned non-JSON response (HTTP {response.status_code}): "
                    f"{response.text[:300]}"
                )
                st.stop()

            if not response.ok:
                error_detail = result.get("detail", "Unknown backend error")
                st.error(f"Analysis failed (HTTP {response.status_code}): {error_detail}")
                st.stop()

        st.success("Analysis completed")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Prompt Tokens", result["prompt_tokens"])

        with col2:
            st.metric("Completion Tokens", result["completion_tokens"])

        with col3:
            st.metric("Action Items", len(result.get("action_items", [])))

        with col4:
            st.metric("Key Decisions", len(result.get("key_decisions", [])))

        st.divider()

        summary_tab, actions_tab, decisions_tab = st.tabs(
            ["Summary", "Action Items", "Key Decisions"]
        )

        with summary_tab:
            st.subheader("Summary")
            st.write(result["summary"])

        with actions_tab:
            render_items(
                title="Action Items",
                items=result.get("action_items", []),
                empty_message="No actions detected",
            )

        with decisions_tab:
            render_items(
                title="Key Decisions",
                items=result.get("key_decisions", []),
                empty_message="No decisions detected",
            )
