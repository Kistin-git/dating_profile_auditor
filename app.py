from __future__ import annotations

import streamlit as st

from src.config import LABEL_LOCALIZATION_KEYS, LABELS
from src.heuristics import Diagnostic
from src.inference import DatingProfileAuditor
from src.localization import LOCALIZATION, SAMPLE_BIOS, LocalizationBundle


st.set_page_config(page_title="Dating Profile Auditor", layout="wide")


@st.cache_resource(show_spinner=False)
def load_auditor() -> DatingProfileAuditor:
    return DatingProfileAuditor()


def render_diagnostics(diags: list[Diagnostic], bundle: LocalizationBundle) -> None:
    if not diags:
        st.success(bundle.t("diagnostic_none"))
        return
    for diag in diags:
        st.warning(bundle.t(diag.key))


def render_probabilities(probabilities: dict[str, float], bundle: LocalizationBundle) -> None:
    cols = st.columns(2)
    for idx, label in enumerate(LABELS):
        col = cols[idx % 2]
        localized_label = bundle.t(LABEL_LOCALIZATION_KEYS[label])
        value = probabilities.get(label, 0.0)
        col.write(f"**{localized_label}** — {value:.0%}")
        col.progress(min(max(value, 0.0), 1.0))


def main() -> None:
    st.title("Dating Profile Auditor")

    st.caption("Transformer-based assistant for dating bios / Анализатор био профилей.")

    auditor = load_auditor()

    language = st.sidebar.radio(
        "Language / Язык",
        options=["ru", "en"],
        format_func=lambda code: LOCALIZATION[code]["language_ru"] if code == "ru" else LOCALIZATION[code]["language_en"],
        index=0,
    )
    bundle = LocalizationBundle(language)
    st.sidebar.markdown(f"**{bundle.t('samples_title')}**")
    st.sidebar.caption(bundle.t("samples_hint"))

    if "bio_editor" not in st.session_state:
        st.session_state["bio_editor"] = ""

    for idx, (name, sample_text) in enumerate(SAMPLE_BIOS.get(language, {}).items()):
        if st.sidebar.button(name, key=f"sample_{language}_{idx}"):
            st.session_state["bio_editor"] = sample_text

    st.sidebar.divider()
    st.sidebar.caption(bundle.t("disclaimer"))

    st.subheader(bundle.t("app_subtitle"))

    text = st.text_area(
        bundle.t("input_label"),
        key="bio_editor",
        height=180,
        placeholder=bundle.t("input_placeholder"),
    )

    analyze = st.button(bundle.t("analyze_button"), type="primary")

    analysis_result = None

    if analyze:
        if not text.strip():
            st.warning(bundle.t("empty_input_warning"))
        else:
            with st.spinner("Анализируем..." if language == "ru" else "Analyzing..."):
                analysis_result = auditor.analyze(text, ui_language=language)
                st.session_state["analysis_result"] = analysis_result
    elif "analysis_result" in st.session_state:
        analysis_result = st.session_state["analysis_result"]

    if not analysis_result:
        return

    if len(text.strip()) < 40:
        st.info(bundle.t("short_input_warning"))

    if analysis_result.truncated:
        st.info(bundle.t("long_input_warning"))

    detected_lang = analysis_result.language_detection.language
    st.caption(bundle.t("detected_language", language=detected_lang.upper()))
    if detected_lang == "other":
        st.warning(bundle.t("unsupported_language_warning"))

    score_col, classifier_col = st.columns([2, 1])
    score_col.metric(bundle.t("score_title"), f"{analysis_result.score.score}/100")
    classifier_col.caption(f"Model: {analysis_result.predictions.classifier_name}")

    st.subheader(bundle.t("tone_section"))
    render_probabilities(analysis_result.predictions.probabilities, bundle)

    st.subheader(bundle.t("diagnostics_section"))
    render_diagnostics(analysis_result.heuristics.diagnostics, bundle)

    if analysis_result.heuristics.cliche_hits:
        st.info(" / ".join(analysis_result.heuristics.cliche_hits))

    st.subheader(bundle.t("explanation_section"))
    st.write(analysis_result.score.explanation.get(language, analysis_result.score.explanation["ru"]))

    st.subheader(bundle.t("rewrites_section"))
    rewrites = analysis_result.rewrites
    st.write(f"**{bundle.t('rewrite_warmer')}**")
    st.write(rewrites.warmer)
    st.write(f"**{bundle.t('rewrite_funny')}**")
    st.write(rewrites.funny)
    st.write(f"**{bundle.t('rewrite_confident')}**")
    st.write(rewrites.confident)

    st.caption(bundle.t("disclaimer"))


if __name__ == "__main__":
    main()
