from __future__ import annotations

import os

import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "API_URL = https://brand-guardian-ai-ikct.onrender.com/api/v1/analyze")

st.set_page_config(
    page_title="Brand Guardian",
    layout="wide",
)

st.title("Real-Time Multimodal Brand Guardian System")
st.caption("Monitor brand threats from text, images, and memes in one place.")

with st.sidebar:
    st.subheader("Backend")
    st.code(API_BASE_URL)
    if st.button("Check health"):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=10)
            response.raise_for_status()
            st.success(response.json())
        except Exception as exc:
            st.error(f"Backend unavailable: {exc}")

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Analyze Social Content")
    text = st.text_area(
        "Post text",
        placeholder="Paste a tweet, caption, complaint, meme text, or suspected fake news here...",
        height=220,
    )
    image = st.file_uploader(
        "Optional image or meme",
        type=["png", "jpg", "jpeg", "webp"],
    )

    if st.button("Run analysis", type="primary", use_container_width=True):
        if not text.strip():
            st.warning("Please enter some text to analyze.")
        else:
            files = {}
            if image is not None:
                files["image"] = (image.name, image.getvalue(), image.type or "image/png")
            try:
                with st.spinner("Analyzing multimodal content..."):
                    response = requests.post(
                        f"{API_BASE_URL}/api/v1/analyze",
                        data={"text": text},
                        files=files or None,
                        timeout=60,
                    )
                    response.raise_for_status()
                    result = response.json()

                st.success("Analysis complete")
                metric_cols = st.columns(3)
                metric_cols[0].metric("Category", result["category"].replace("_", " ").title())
                metric_cols[1].metric("Sentiment", result["sentiment"].title())
                metric_cols[2].metric("Risk Score", f'{result["risk_score"]:.2f}')

                st.markdown("### Summary")
                st.write(result["summary"])

                st.markdown("### Reasoning")
                st.write(result["reasoning"])

                st.markdown("### Suggested Response")
                st.info(result["suggested_response"])

                st.markdown("### Retrieval Memory")
                memories = result.get("related_memories", [])
                if memories:
                    for item in memories:
                        st.write(
                            f"- {item['category']} | {item['sentiment']} | "
                            f"{item['content'][:120]}"
                        )
                else:
                    st.write("No similar past interactions found yet.")

                st.caption(f"Analysis mode: {result['mode']}")
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

with right:
    st.subheader("Recent Memory")
    if st.button("Refresh memory", use_container_width=True):
        st.rerun()

    try:
        response = requests.get(f"{API_BASE_URL}/api/v1/memory", timeout=10)
        response.raise_for_status()
        memory_items = response.json().get("items", [])
    except Exception:
        memory_items = []

    if memory_items:
        for item in memory_items:
            with st.container(border=True):
                st.write(item["content"])
                st.caption(
                    f"{item['category']} | {item['sentiment']} | {item['created_at']}"
                )
                st.code(item["response"])
    else:
        st.write("No memory entries yet. Run an analysis to seed context.")
