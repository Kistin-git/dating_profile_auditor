from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


SUPPORTED_LANGS = ("ru", "en")


LOCALIZATION: Dict[str, Dict[str, str]] = {
    "ru": {
        "app_title": "Dating Profile Auditor",
        "app_subtitle": "Анализируем тексты био для дейтинга, чтобы тон звучал теплее и осознаннее.",
        "language_toggle": "Переключить язык на английский",
        "input_label": "Текст bio",
        "input_placeholder": "Например: Люблю утренние пробежки, готовлю ризотто и ищу человека с самоиронией...",
        "analyze_button": "Анализировать",
        "samples_title": "Примеры",
        "samples_hint": "Выберите пример или введите свой текст ниже.",
        "loading_model": "Загружаем модель...",
        "score_title": "Первое впечатление",
        "tone_section": "Тон и стиль",
        "diagnostics_section": "Замеченные сигналы",
        "explanation_section": "Короткое объяснение",
        "rewrites_section": "Альтернативные версии",
        "rewrite_apply": "Применить эту версию",
        "rewrite_hint": "Выберите понравившуюся вариацию, и мы перепишем текст в поле ввода.",
        "rewrite_applied": "Версия '{variant}' подставлена в текстовое поле.",
        "disclaimer": "Инструмент оценивает только текст и не делает выводы о личности.",
        "empty_input_warning": "Пожалуйста, введите хотя бы одно предложение.",
        "short_input_warning": "Текст довольно короткий, выводы могут быть менее точными.",
        "long_input_warning": "Текст был обрезан до 600 символов для анализа.",
        "unsupported_language_warning": "Модель оптимизирована для русского и английского языков. Результаты могут быть неточными.",
        "detected_language": "Определённый язык: {language}",
        "analysis_ready": "Результаты анализа ниже.",
        "diagnostic_none": "Явных проблем не обнаружено.",
        "rewrite_warmer": "Более тёплая версия",
        "rewrite_funny": "Более смешная версия",
        "rewrite_confident": "Более уверенная версия",
        "hero_bad_title": "До аудита",
        "hero_good_title": "После аудита",
        "hero_arrow": "Auditor → enhanced",
        "label_friendly": "Дружелюбный",
        "label_confident": "Уверенный",
        "label_arrogant": "Высокомерный",
        "label_sincere": "Искренний",
        "label_humorous": "С юмором",
        "label_cliche": "Шаблонный",
        "label_aggressive": "Агрессивный",
        "label_awkward": "Кринжовый/неловкий",
        "diag_too_short": "Слишком короткий",
        "diag_too_long": "Слишком длинный",
        "diag_too_generic": "Слишком общий",
        "diag_too_negative": "Слишком негативный",
        "diag_too_demanding": "Слишком много требований",
        "diag_overloaded_with_cliches": "Много клише",
        "diag_not_enough_personality": "Мало индивидуальности",
        "diag_too_many_emojis": "Слишком много эмодзи",
        "diag_excessive_punctuation": "Слишком много знаков препинания",
        "diag_not_a_bio": "Похоже на статью или новость, а не на анкету",
        "language_ru": "Русский",
        "language_en": "Английский",
    },
    "en": {
        "app_title": "Dating Profile Auditor",
        "app_subtitle": "Analyze dating bios to understand tone, clichés, and ways to improve.",
        "language_toggle": "Switch interface to Russian",
        "input_label": "Bio text",
        "input_placeholder": "Example: Morning run addict, proud pasta maker and looking for someone kind...",
        "analyze_button": "Analyze",
        "samples_title": "Samples",
        "samples_hint": "Pick a sample or enter your own text below.",
        "loading_model": "Loading model...",
        "score_title": "First impression score",
        "tone_section": "Tone & style",
        "diagnostics_section": "Detected signals",
        "explanation_section": "Explanation",
        "rewrites_section": "Rewrite suggestions",
        "rewrite_apply": "Apply this rewrite",
        "rewrite_hint": "Pick a variant you like and we will replace the input text.",
        "rewrite_applied": "The '{variant}' rewrite was applied to the editor.",
        "disclaimer": "This tool evaluates the writing, not the person behind it.",
        "empty_input_warning": "Please enter at least one sentence.",
        "short_input_warning": "The bio is very short, results may be less stable.",
        "long_input_warning": "Input was trimmed to 600 characters for analysis.",
        "unsupported_language_warning": "The model is optimized for Russian and English. Results for other languages may be unreliable.",
        "detected_language": "Detected language: {language}",
        "analysis_ready": "Analysis complete.",
        "diagnostic_none": "No red flags detected.",
        "rewrite_warmer": "Warmer version",
        "rewrite_funny": "Funnier version",
        "rewrite_confident": "More confident version",
        "hero_bad_title": "Before auditing",
        "hero_good_title": "After auditing",
        "hero_arrow": "Auditor → enhanced",
        "label_friendly": "Friendly",
        "label_confident": "Confident",
        "label_arrogant": "Arrogant",
        "label_sincere": "Sincere",
        "label_humorous": "Humorous",
        "label_cliche": "Cliché",
        "label_aggressive": "Aggressive",
        "label_awkward": "Awkward / cringe",
        "diag_too_short": "Too short",
        "diag_too_long": "Too long",
        "diag_too_generic": "Too generic",
        "diag_too_negative": "Too negative",
        "diag_too_demanding": "Too demanding",
        "diag_overloaded_with_cliches": "Too many clichés",
        "diag_not_enough_personality": "Not enough personality",
        "diag_too_many_emojis": "Too many emojis",
        "diag_excessive_punctuation": "Excessive punctuation",
        "diag_not_a_bio": "Looks more like an article than a dating bio",
        "language_ru": "Russian",
        "language_en": "English",
    },
}


SAMPLE_BIOS: Dict[str, Dict[str, str]] = {
    "ru": {
        "Тёплая Анна": "Люблю ранние завтраки, велопрогулки у реки и говорить о книгах без спешки. Ищу человека, который ценит маленькие радости.",
        "Шутливый Илья": "Делаю лучший борщ, спорю о ситкомах и верю, что самоирония спасает даже в скучный понедельник.",
        "Общий шаблон": "Люблю путешествовать, вкусно поесть и проводить выходные с друзьями. В активном поиске.",
        "Требовательная Екатерина": "Не трать моё время: без вредных привычек, высокий, амбициозный. Не пиши, если не готов развиваться.",
        "Эмодзи": "Люблю море!!! 🌊🌊🌊 Хочу найти того, кто будет радоваться жизни так же, как я!!! 😍✨",
    },
    "en": {
        "Warm Lily": "Morning coffee nerd, urban gardener and fan of open-air concerts. Looking for someone kind and curious.",
        "Sarcastic Dan": "Recovering meme addict, will judge your playlist but cook pancakes. Say hi if you enjoy dry jokes.",
        "Demanding Olivia": "Swipe left unless you are 6ft+, have a PhD, play tennis every weekend and hate drama.",
    },
}


def get_text(lang: str, key: str) -> str:
    lang = lang if lang in SUPPORTED_LANGS else "ru"
    return LOCALIZATION[lang].get(key, LOCALIZATION["ru"].get(key, key))


@dataclass
class LocalizationBundle:
    lang: str

    def t(self, key: str, **kwargs) -> str:
        template = get_text(self.lang, key)
        return template.format(**kwargs) if kwargs else template
