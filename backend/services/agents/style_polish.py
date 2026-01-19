"""Style Polish Agent (Redaktor) - performs professional text stylization and commercial polish."""

import json
import logging
from datetime import datetime
from uuid import uuid4

from models.schemas.agent import StyleRequest, StyleResponse
from services.model_policy import ModelPolicy, PipelineStage
from services.openai_client import OpenAIClient

logger = logging.getLogger(__name__)


class StylePolishAgent:
    """
    Style Polish Agent (Redaktor) - performs professional text stylization.

    This agent uses gpt-4o (HIGH MODEL) to:
    - Polish prose to professional publication standards
    - Adapt text to Polish language nuances
    - Apply target writing style (literary, commercial, genre-specific)
    - Perform commercial editing (sentence flow, clarity, engagement)
    - Fix grammar, punctuation, and style inconsistencies

    Uses PipelineStage.STYLE with gpt-4o for high-quality stylization.
    """

    SYSTEM_PROMPT = """Jesteś profesjonalnym Redaktorem literackim specjalizującym się w polskim języku.

Twoim zadaniem jest stylizacja i redakcja prozy do standardów publikacji komercyjnej.

## Twoje Obszary Pracy:

**1. Język Polski - Niuanse i Styl**
- Naturalne brzmienie w języku polskim (nie tłumaczenie z angielskiego)
- Poprawna składnia i szyku wyrazów (nie kalki językowe)
- Bogaty, literacki język (nie kolokwializmy, chyba że w dialogach)
- Właściwe użycie czasów i trybów (aspekt dokonany/niedokonany)
- Zgodność z zasadami interpunkcji polskiej (przecinki, myślniki, cudzysłowy)

**2. Styl Literacki**
- Płynność narracji i rytm zdań
- Różnorodność konstrukcji zdań (krótkie i długie, proste i złożone)
- Unikanie powtórzeń (synonimizacja, elipsa)
- Spójność tonu i rejestru językowego
- Elegancja stylistyczna (nie sztampowość)

**3. Redakcja Komercyjna**

**Light (lekka redakcja):**
- Korekta błędów gramatycznych i ortograficznych
- Poprawa oczywistych niezręczności stylistycznych
- Zachowanie oryginalnego stylu autora
- Minimalne ingerencje

**Standard (standardowa redakcja):**
- Korekta językowa i stylistyczna
- Poprawa płynności narracji
- Eliminacja powtórzeń i niezręczności
- Wzmocnienie obrazowania
- Dopracowanie dialogów

**Intensive (intensywna redakcja):**
- Głęboka przebudowa stylistyczna
- Maksymalizacja literackiej jakości
- Wzmocnienie emocjonalnego oddziaływania
- Perfekcyjna płynność i rytm
- Komercyjna atrakcyjność (page-turner quality)

**4. Gatunki i Style**

**Fantasy:**
- Epicka narracja, poetyckie opisy
- Terminologia fantastyczna (naturalnie wpleciona)
- Atmosphere i worldbuilding w języku
- Dystans narracyjny (trzecia osoba często)

**Sci-Fi:**
- Precyzyjny, techniczny język (ale dostępny)
- Nowoczesna składnia
- Koncepcje naukowe w języku potocznym
- Tempo narracji

**Thriller/Kryminał:**
- Krótkie, dynamiczne zdania w akcji
- Budowanie napięcia rytmem
- Ekonomia środków (każde słowo celowe)
- Present tense lub past tense - spójność

**Literary Fiction:**
- Najbogatszy język i metaforyka
- Głębia psychologiczna w stylu
- Eksperymentalne konstrukcje (dozwolone)
- Subtelność i wieloznaczność

**Horror:**
- Atmosfera w języku (niepokój, lęk)
- Sugestia zamiast ekspozycji
- Rytm narastającego napięcia
- Zmysłowe opisy (zwłaszcza nieprzyjemne)

## Czego UNIKAĆ:

❌ **Anglicyzmy i kalki językowe:**
- "Był w procesie" → "Był w trakcie" lub po prostu "Właśnie..."
- "Realizował" (z angielskiego "realize") → "Zdał sobie sprawę"
- "Brał prysznic" → "Wziął prysznic" (aspekt dokonany)

❌ **Sztampowość:**
- "Ciemność jak smoła", "biały jak śnieg" → oryginalne porównania
- "Serce waliło jak młot" → świeże metafory

❌ **Overwriting:**
- Zbyt wiele przymiotników
- Zbyt kwiecisty język w dynamicznych scenach
- Nadmierne wyjaśnianie

❌ **Niezręczności:**
- Nieczytelne długie zdania (rozdziel)
- Powtórzenia tego samego słowa w zdaniu/akapicie
- Niejasne odniesienia anaforyczne (kto to "on"?)

## Output Format:

Zwróć TYLKO poprawny JSON:

{
  "polished_prose": "Cała wypolerowana proza tutaj...",
  "changes_count": 42,
  "style_score": 0.92,
  "changes_summary": "Główne zmiany: poprawiono anglicyzmy (5), wzmocniono obrazowanie (12), dopracowano rytm (8), usunięto powtórzenia (17)",
  "commercial_notes": "Tekst gotowy do publikacji. Wzmocniono page-turner quality poprzez poprawę dynamiki w scenach akcji."
}

**Pole `polished_prose`:**
- Kompletny, wypolerowany tekst
- Zachowaj oryginalną długość (+/- 10%)
- Wszystkie poprawki już wprowadzone
- Gotowy do publikacji

**Pole `changes_count`:**
- Liczba istotnych zmian (nie liczyć przecinków)
- Uwzględnij: wymienione słowa, przebudowane zdania, poprawki gramatyczne

**Pole `style_score` (0.0-1.0):**
- 0.95-1.0: Publikacja premium, perfekcyjny styl
- 0.85-0.94: Profesjonalna jakość, gotowy do druku
- 0.70-0.84: Dobry standard, drobne niedoskonałości
- 0.50-0.69: Wymaga dalszej pracy
- <0.50: Znaczące problemy stylistyczne

## Przykład (Fantasy, Standard):

**Input:**
"Kael był chodząc przez las. Drzewa były wysokie i ciemne. Czuł że coś jest nie tak. 'Musimy iść szybciej' powiedział do Lyry. Ona skinęła głową. Las był ciemny i straszny."

**Output:**
{
  "polished_prose": "Kael przedzierał się przez gęstwinę. Drzewa wznosiły się ponad nim niczym kamienne kolumny pradawnej świątyni, ich korony ginęły w mroku. Skóra na karku zjeżyła mu się – w powietrzu wisiało coś niewłaściwego, niewidzialnego, ale namacalnego jak ostrze przy gardle.\\n\\n– Musimy przyspieszyć – szepnął do Lyry, nie odrywając wzroku od plątaniny cieni.\\n\\nSkinęła głową, zacisnęła dłoń na rękojeści noża. Wiedziała.",
  "changes_count": 18,
  "style_score": 0.88,
  "changes_summary": "Poprawiono anglicyzm 'był chodząc' → 'przedzierał się'. Wzmocniono obrazowanie drzew (metafora kolumn). Dodano zmysłowy opis niepokoju. Dopracowano dialog (naturalne polski). Usunięto powtórzenie 'ciemny'. Rozbudowano zakończenie (ekonomia środków – 'Wiedziała' zamiast wyjaśnienia).",
  "commercial_notes": "Tekst zyskał na atmosferze i napięciu. Rytm jest dobry, obrazowanie epickie. Gotowy do publikacji w gatunku fantasy."
}

## Twoje Zadanie:

Otrzymasz:
1. Tekst do wypolerowania (prose)
2. Docelowy styl (target_style)
3. Język (language) - domyślnie "pl"
4. Poziom redakcji (commercial_level) - light/standard/intensive

Wykonaj profesjonalną redakcję zgodnie z poziomem i stylem.
Zachowaj intencję autora, ale podnieś jakość do standardów komercyjnych.
"""

    def __init__(self, openai_client: OpenAIClient | None = None) -> None:
        """
        Initialize Style Polish Agent.

        Args:
            openai_client: OpenAI client for API calls (creates new if None)
        """
        self.client = openai_client or OpenAIClient()
        self.stage = PipelineStage.STYLE
        self.model = ModelPolicy.get_model_for_stage(self.stage)
        self.temperature = ModelPolicy.get_temperature_for_stage(self.stage)
        self.token_budget = ModelPolicy.get_token_budget_for_stage(self.stage)

    async def polish_prose(
        self, request: StyleRequest, original_prose: str
    ) -> StyleResponse:
        """
        Polish prose to professional publication standards.

        Args:
            request: StyleRequest with prose_id, target_style, language, commercial_level
            original_prose: The original prose text to polish

        Returns:
            StyleResponse with polished prose and statistics

        Raises:
            ValueError: If response cannot be parsed or is invalid
        """
        logger.info(
            "StylePolishAgent starting",
            extra={
                "job_id": str(request.job_id),
                "prose_id": str(request.prose_id),
                "target_style": request.target_style,
                "language": request.language,
                "commercial_level": request.commercial_level,
                "stage": self.stage.value,
                "model": self.model,
            },
        )

        # Build user prompt
        user_prompt = f"""Wypoleruj następującą prozę do standardów publikacji komercyjnej.

**Docelowy styl:** {request.target_style}
**Język:** {request.language}
**Poziom redakcji:** {request.commercial_level}

**Proza do wypolerowania:**

{original_prose}

---

Wykonaj profesjonalną redakcję zgodnie z podanym poziomem i stylem.
Zwróć JSON z polished_prose, changes_count, style_score, changes_summary, commercial_notes.
"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ]

        # Call OpenAI with HIGH MODEL (gpt-4o)
        result = await self.client.chat_completion(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            token_budget=self.token_budget,
        )

        # Parse JSON response
        try:
            style_data = json.loads(result["content"])
        except json.JSONDecodeError as exc:
            logger.error(
                "Failed to parse StylePolishAgent response",
                extra={"response": result["content"][:500]},
            )
            raise ValueError(
                f"Invalid JSON response from StylePolishAgent: {exc}"
            ) from exc

        # Validate required fields
        if "polished_prose" not in style_data or not style_data["polished_prose"]:
            raise ValueError(
                "StylePolishAgent response missing or empty 'polished_prose' field"
            )

        # Extract data
        polished_prose = style_data["polished_prose"]
        changes_count = style_data.get("changes_count", 0)
        style_score = float(style_data.get("style_score", 0.7))

        # Validate style_score range
        if not 0.0 <= style_score <= 1.0:
            logger.warning(
                "Style score out of range, clamping",
                extra={"original": style_score},
            )
            style_score = max(0.0, min(1.0, style_score))

        # Verify polished prose has reasonable length
        original_length = len(original_prose.split())
        polished_length = len(polished_prose.split())
        length_diff = abs(polished_length - original_length) / max(original_length, 1)

        if length_diff > 0.5:  # More than 50% change
            logger.warning(
                "Polished prose length differs significantly from original",
                extra={
                    "original_words": original_length,
                    "polished_words": polished_length,
                    "diff_percent": int(length_diff * 100),
                },
            )

        # Determine if polishing succeeded (style_score >= 0.7)
        polished = style_score >= 0.7

        # Generate new prose artifact ID
        polished_prose_id = uuid4() if polished else None

        logger.info(
            "StylePolishAgent completed",
            extra={
                "job_id": str(request.job_id),
                "prose_id": str(request.prose_id),
                "polished": polished,
                "changes_count": changes_count,
                "style_score": style_score,
                "original_words": original_length,
                "polished_words": polished_length,
                "cost_usd": result["cost"],
                "model": self.model,
            },
        )

        # Build response
        response = StyleResponse(
            id=uuid4(),
            job_id=request.job_id,
            agent="redaktor",
            stage=self.stage,
            prose_id=request.prose_id,
            polished=polished,
            polished_prose_id=polished_prose_id,
            changes_count=changes_count,
            style_score=style_score,
            created_at=result.get("created_at") or datetime.utcnow(),
        )

        return response
