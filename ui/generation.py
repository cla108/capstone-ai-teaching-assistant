import streamlit as st

def render_chunks(chunks):
    st.subheader("Generated Chunks")
    for i, chunk in enumerate(chunks, start=1):
        with st.expander(f"Chunk {i}"):
            if isinstance(chunk, dict):
                st.write(chunk["text"])
            else:
                st.write(chunk)

def render_rag_context(chunks):
    st.subheader("Retrieved Context (RAG)")
    st.info(f"{len(chunks)} chunks were retrieved for lesson generation.")
    for i, chunk in enumerate(chunks, start=1):
        with st.expander(f"Retrieved Chunk {i}"):
            if isinstance(chunk, dict):
                if "score" in chunk:
                    st.caption(f"Similarity Score: {chunk['score']:.3f}")
                st.write(chunk["text"])
            else:
                st.write(chunk)

def render_evaluation(evaluation):
    st.subheader("📊 Evaluation")
    if not evaluation:
        st.info("No evaluation data available.")
        return

    numeric_metrics = {
        "total_factual_claims": "Total Factual Claims",
        "supported_claims": "Supported Claims",
        "partially_supported_claims": "Partially Supported",
        "unsupported_claims": "Unsupported Claims",
        "hallucination_rate": "Hallucination Rate",
        "coverage_score": "Coverage Score",
        "structure_score": "Structure Score",
        "overall_score": "Overall Score",
    }

    metric_items = []
    for key, label in numeric_metrics.items():
        if key in evaluation:
            value = evaluation[key]
            if isinstance(value, (int, float)):
                metric_items.append((label, value))

    if metric_items:
        num_cols = min(3, len(metric_items))
        cols = st.columns(num_cols)
        for idx, (label, value) in enumerate(metric_items):
            with cols[idx % num_cols]:
                if any(x in label.lower() for x in ["rate", "score"]):
                    display_value = f"{value:.1f}%"
                else:
                    display_value = str(value)
                st.metric(label, display_value)

    if "missing_concepts" in evaluation and evaluation["missing_concepts"]:
        with st.expander("❌ Missing Concepts"):
            missing = evaluation["missing_concepts"]
            if isinstance(missing, list):
                for concept in missing:
                    st.write(f"• {concept}")
            else:
                st.write(missing)

    if "unsupported_claim_examples" in evaluation and evaluation["unsupported_claim_examples"]:
        with st.expander("⚠️ Unsupported Claims"):
            claims = evaluation["unsupported_claim_examples"]
            if isinstance(claims, list):
                for claim in claims:
                    st.write(f"• {claim}")
            else:
                st.write(claims)

    if "feedback" in evaluation and evaluation["feedback"]:
        with st.expander("📝 Feedback"):
            feedback = evaluation["feedback"]
            if isinstance(feedback, list):
                for item in feedback:
                    st.write(f"• {item}")
            else:
                st.write(feedback)

def render_statistics(created_chunks, retrieved_chunks, provider):
    st.subheader("Generation Statistics")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Chunks Created", created_chunks)
    with c2:
        st.metric("Chunks Retrieved", retrieved_chunks)
    with c3:
        st.metric("Embedding Provider", provider)

def render_lesson_editor(instructor_guide):
    st.subheader("✏️ Edit Instructor Guide")
    
    if not instructor_guide:
        st.warning("⚠️ No lesson content found! Please generate a lesson first.")
        return ""
    
    # Show a preview
    st.success(f"✅ Lesson loaded! ({len(instructor_guide)} characters)")
    
    with st.expander("👁️ Preview (first 500 characters)"):
        st.text(instructor_guide[:500] + "...")
    
    # Show the editable text area
    return st.text_area(
        "Edit the lesson below:",
        value=instructor_guide,
        height=700,
        key="lesson_editor"
    )
