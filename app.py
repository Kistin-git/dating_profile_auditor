from __future__ import annotations

import random

import streamlit as st

from src.config import LABEL_LOCALIZATION_KEYS, LABELS
from src.heuristics import Diagnostic
from src.inference import DatingProfileAuditor
from src.localization import LOCALIZATION, SAMPLE_BIOS, LocalizationBundle


st.set_page_config(page_title="Dating Profile Auditor", layout="wide")


HERO_VARIANTS = {
    "ru": [
        {
            "before_img": "https://images.unsplash.com/photo-1524504388940-b1c1722653e1?auto=format&fit=crop&w=600&q=40&sat=-80",
            "before_text": "«Эй, я тут ради мемов и вообще ничего рассказывать не собираюсь.»",
            "after_img": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=600&q=80",
            "after_text": "«Инженер из Казани, бегаю вечерами, собираю джазовые винилы и ищу человека с самоиронией.»",
        },
        {
            "before_img": "https://images.unsplash.com/photo-1463453091185-61582044d556?auto=format&fit=crop&w=600&q=60",
            "before_text": "«Напиши, если точно знаешь, что хочешь, иначе не отвлекай.»",
            "after_img": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?auto=format&fit=crop&w=600&q=60",
            "after_text": "«Сочиняю гитарные мини-концерты на кухне, люблю походы и честные разговоры без прессинга.»",
        },
    ],
    "en": [
        {
            "before_img": "https://images.unsplash.com/photo-1504593811423-6dd665756598?auto=format&fit=crop&w=600&q=40&sat=-80",
            "before_text": "\"Here for drama, swipe if you can fix me.\"",
            "after_img": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80",
            "after_text": "\"Product designer, sunrise runner, hopeless fan of vinyl cafés and low-key adventures.\"",
        },
        {
            "before_img": "https://images.unsplash.com/photo-1445052693476-5134dfe40f37?auto=format&fit=crop&w=600&q=60",
            "before_text": "\"Bored. Impress me or move on.\"",
            "after_img": "https://images.unsplash.com/photo-1544723795-3fb6469f5b39?auto=format&fit=crop&w=600&q=60",
            "after_text": "\"Curator of modern art, loves rooftop picnics and meaningful debates.\"",
        },
    ],
}


@st.cache_resource(show_spinner=False)
def load_auditor() -> DatingProfileAuditor:
    return DatingProfileAuditor()


def _get_hero_variant(lang: str) -> dict:
    key = f"hero_variant_{lang}"
    stored = st.session_state.get(key)
    if not stored:
        variant = random.choice(HERO_VARIANTS.get(lang, HERO_VARIANTS["ru"]))
        st.session_state[key] = variant
        return variant
    return stored


def render_hero(bundle: LocalizationBundle) -> None:
    variant = _get_hero_variant(bundle.lang)
    col_bad, col_arrow, col_good = st.columns([3, 1, 3])
    with col_bad:
        st.image(variant["before_img"], use_column_width=True)
        st.caption(bundle.t("hero_bad_title"))
        st.write(variant["before_text"])
    with col_arrow:
        st.markdown(f"### {bundle.t('hero_arrow')}")
    with col_good:
        st.image(variant["after_img"], use_column_width=True)
        st.caption(bundle.t("hero_good_title"))
        st.write(variant["after_text"])


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


def apply_rewrite_variant(text: str, variant_name: str) -> None:
    st.session_state["bio_editor"] = text
    st.session_state.pop("analysis_result", None)
    st.session_state["applied_variant"] = variant_name


def main() -> None:
    st.title("Dating Profile Auditor")

    st.caption("Transformer-based assistant for dating bios / Анализатор био профилей.")

    language = st.sidebar.radio(
        "Language / Язык",
        options=["ru", "en"],
        format_func=lambda code: LOCALIZATION[code]["language_ru"] if code == "ru" else LOCALIZATION[code]["language_en"],
        index=0,
    )
    bundle = LocalizationBundle(language)

    if "analysis_result" not in st.session_state:
        render_hero(bundle)

    with st.spinner(bundle.t("loading_model")):
        auditor = load_auditor()

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
    if "analysis_result" not in st.session_state:
        render_hero(bundle)

    if st.session_state.get("applied_variant"):
        st.success(bundle.t("rewrite_applied", variant=st.session_state["applied_variant"]))
        st.session_state.pop("applied_variant")

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
    st.caption(bundle.t("rewrite_hint"))
    rewrites = analysis_result.rewrites
    rewrite_data = [
        ("rewrite_warmer", rewrites.warmer),
        ("rewrite_funny", rewrites.funny),
        ("rewrite_confident", rewrites.confident),
    ]
    for key_name, content in rewrite_data:
        st.write(f"**{bundle.t(key_name)}**")
        st.write(content)
        st.button(
            bundle.t("rewrite_apply"),
            key=f"apply_{key_name}",
            on_click=apply_rewrite_variant,
            args=(content, bundle.t(key_name)),
        )

    st.caption(bundle.t("disclaimer"))


if __name__ == "__main__":
    main()
