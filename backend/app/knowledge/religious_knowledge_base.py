"""
Religious Knowledge Base for NarraForge 2.0

Authentic religious sources for religious genre literature.
Only verified, approved sources from Church teaching.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ScriptureBook(str, Enum):
    """Books of the Bible"""
    # Old Testament (selected)
    GENESIS = "Rdz"
    EXODUS = "Wj"
    PSALMS = "Ps"
    PROVERBS = "Prz"
    ISAIAH = "Iz"
    JEREMIAH = "Jr"
    EZEKIEL = "Ez"
    DANIEL = "Dn"
    # New Testament
    MATTHEW = "Mt"
    MARK = "Mk"
    LUKE = "Łk"
    JOHN = "J"
    ACTS = "Dz"
    ROMANS = "Rz"
    CORINTHIANS_1 = "1 Kor"
    CORINTHIANS_2 = "2 Kor"
    GALATIANS = "Ga"
    EPHESIANS = "Ef"
    PHILIPPIANS = "Flp"
    COLOSSIANS = "Kol"
    THESSALONIANS_1 = "1 Tes"
    HEBREWS = "Hbr"
    JAMES = "Jk"
    PETER_1 = "1 P"
    JOHN_1 = "1 J"
    REVELATION = "Ap"


@dataclass
class ScriptureReference:
    """A Scripture reference with text"""
    book: str
    chapter: int
    verses: str
    text: str
    theme: str


@dataclass
class ChurchTeaching:
    """Church teaching reference"""
    source: str  # e.g., "Katechizm Kościoła Katolickiego"
    number: Optional[str]  # Paragraph number
    topic: str
    summary: str


@dataclass
class ApprovedMiracle:
    """An approved miracle"""
    name: str
    year: str
    location: str
    description: str
    approved_by: str
    key_elements: List[str]


class ReligiousKnowledgeBase:
    """
    Religious knowledge base with ONLY verified, authentic sources.
    """

    # KEY SCRIPTURE PASSAGES BY THEME
    SCRIPTURE_BY_THEME = {
        "faith": [
            ScriptureReference("Hbr", 11, "1", "Wiara zaś jest poręką tych dóbr, których się spodziewamy, dowodem tych rzeczywistości, których nie widzimy.", "definicja wiary"),
            ScriptureReference("Rz", 10, "17", "Przeto wiara rodzi się z tego, co się słyszy, tym zaś, co się słyszy, jest słowo Chrystusa.", "źródło wiary"),
            ScriptureReference("Jk", 2, "26", "Jak ciało bez ducha jest martwe, tak też jest martwa wiara bez uczynków.", "wiara i uczynki"),
            ScriptureReference("Mt", 17, "20", "Zaprawdę, powiadam wam: Jeśli będziecie mieć wiarę jak ziarnko gorczycy...", "siła wiary"),
        ],
        "love": [
            ScriptureReference("1 Kor", 13, "4-7", "Miłość cierpliwa jest, łaskawa jest. Miłość nie zazdrości, nie szuka poklasku, nie unosi się pychą...", "hymn o miłości"),
            ScriptureReference("J", 15, "13", "Nikt nie ma większej miłości od tej, gdy ktoś życie swoje oddaje za przyjaciół swoich.", "najwyższa miłość"),
            ScriptureReference("1 J", 4, "8", "Kto nie miłuje, nie zna Boga, bo Bóg jest miłością.", "Bóg jest miłością"),
            ScriptureReference("Mt", 22, "37-39", "Będziesz miłował Pana Boga swego... Będziesz miłował swego bliźniego jak siebie samego.", "przykazanie miłości"),
        ],
        "hope": [
            ScriptureReference("Rz", 8, "28", "Wiemy też, że Bóg z tymi, którzy Go miłują, współdziała we wszystkim dla ich dobra.", "nadzieja"),
            ScriptureReference("Jr", 29, "11", "Albowiem Ja znam zamiary, jakie mam wobec was - mówi Pan - zamiary pełne pokoju, a nie zguby.", "plany Boga"),
            ScriptureReference("Ps", 23, "4", "Chociażbym chodził ciemną doliną, zła się nie ulęknę, bo Ty jesteś ze mną.", "Bóg jako pocieszenie"),
        ],
        "suffering": [
            ScriptureReference("Rz", 5, "3-4", "Chlubimy się także z ucisków, wiedząc, że ucisk wyrabia wytrwałość...", "sens cierpienia"),
            ScriptureReference("2 Kor", 12, "9", "Wystarczy ci mojej łaski. Moc bowiem w słabości się doskonali.", "łaska w słabości"),
            ScriptureReference("Iz", 53, "5", "On był przebity za nasze grzechy, zdruzgotany za nasze winy.", "cierpienie Chrystusa"),
        ],
        "forgiveness": [
            ScriptureReference("Mt", 6, "14-15", "Jeśli bowiem przebaczycie ludziom ich przewinienia, i wam przebaczy Ojciec wasz niebieski.", "przebaczenie"),
            ScriptureReference("Łk", 15, "20-24", "A gdy był jeszcze daleko, ujrzał go jego ojciec i wzruszył się głęboko...", "syn marnotrawny"),
            ScriptureReference("Ef", 4, "32", "Bądźcie dla siebie nawzajem dobrzy i miłosierni! Przebaczajcie sobie, tak jak i Bóg nam przebaczył w Chrystusie.", "wzajemne przebaczenie"),
        ],
        "conversion": [
            ScriptureReference("Dz", 9, "3-6", "Gdy zbliżał się już do Damaszku, olśniła go nagle światłość z nieba.", "nawrócenie Pawła"),
            ScriptureReference("Ez", 36, "26", "Dam wam serce nowe i ducha nowego tchnę do waszego wnętrza.", "nowe serce"),
            ScriptureReference("Łk", 15, "7", "Powiadam wam: Tak samo w niebie większa będzie radość z jednego grzesznika, który się nawraca.", "radość z nawrócenia"),
        ],
        "prayer": [
            ScriptureReference("Mt", 6, "9-13", "Ojcze nasz, który jesteś w niebie...", "Modlitwa Pańska"),
            ScriptureReference("Flp", 4, "6-7", "O nic się już zbytnio nie troskajcie, ale w każdej sprawie wasze prośby przedstawiajcie Bogu w modlitwie.", "modlitwa zaufania"),
            ScriptureReference("1 Tes", 5, "17", "Nieustannie się módlcie!", "ciągła modlitwa"),
        ],
        "grace": [
            ScriptureReference("Ef", 2, "8-9", "Łaską bowiem jesteście zbawieni przez wiarę. A to pochodzi nie od was, lecz jest darem Boga.", "łaska zbawienia"),
            ScriptureReference("Tt", 2, "11", "Ukazała się bowiem łaska Boga, która niesie zbawienie wszystkim ludziom.", "łaska dla wszystkich"),
        ],
        "resurrection": [
            ScriptureReference("1 Kor", 15, "55-57", "Gdzież jest, o śmierci, twoje zwycięstwo? Gdzież jest, o śmierci, twój oścień?", "zwycięstwo nad śmiercią"),
            ScriptureReference("J", 11, "25-26", "Ja jestem zmartwychwstaniem i życiem. Kto we Mnie wierzy, choćby i umarł, żyć będzie.", "Jezus zmartwychwstaniem"),
        ],
        "holy_spirit": [
            ScriptureReference("Ga", 5, "22-23", "Owocem zaś ducha jest: miłość, radość, pokój, cierpliwość, uprzejmość, dobroć, wierność, łagodność, opanowanie.", "owoce Ducha"),
            ScriptureReference("Dz", 2, "4", "I wszyscy zostali napełnieni Duchem Świętym...", "Zesłanie Ducha"),
        ],
    }

    # PAPAL ENCYCLICALS
    ENCYCLICALS = {
        "jan_pawel_ii": {
            "redemptor_hominis": {
                "year": 1979,
                "topic": "Odkupiciel człowieka",
                "key_points": [
                    "Chrystus objawia człowieka człowiekowi",
                    "Godność osoby ludzkiej",
                    "Wolność i odpowiedzialność"
                ]
            },
            "dives_in_misericordia": {
                "year": 1980,
                "topic": "Bóg bogaty w miłosierdzie",
                "key_points": [
                    "Miłosierdzie jako przymiot Boga",
                    "Przypowieść o synu marnotrawnym",
                    "Kościół jako głosiciel miłosierdzia"
                ]
            },
            "veritatis_splendor": {
                "year": 1993,
                "topic": "Blask prawdy - o moralności",
                "key_points": [
                    "Istnienie prawdy obiektywnej",
                    "Wolność a prawda",
                    "Sumienie i jego formacja"
                ]
            },
            "evangelium_vitae": {
                "year": 1995,
                "topic": "Ewangelia życia",
                "key_points": [
                    "Świętość życia ludzkiego",
                    "Obrona życia od poczęcia do naturalnej śmierci",
                    "Kultura życia vs kultura śmierci"
                ]
            },
            "fides_et_ratio": {
                "year": 1998,
                "topic": "Wiara i rozum",
                "key_points": [
                    "Harmonia wiary i rozumu",
                    "Filozofia w służbie teologii",
                    "Poszukiwanie prawdy"
                ]
            }
        },
        "benedykt_xvi": {
            "deus_caritas_est": {
                "year": 2005,
                "topic": "Bóg jest miłością",
                "key_points": [
                    "Eros i agape",
                    "Miłość Boga do człowieka",
                    "Działalność charytatywna Kościoła"
                ]
            },
            "spe_salvi": {
                "year": 2007,
                "topic": "W nadziei zbawieni",
                "key_points": [
                    "Nadzieja chrześcijańska",
                    "Życie wieczne jako prawdziwa nadzieja",
                    "Miejsca uczenia się nadziei"
                ]
            }
        },
        "franciszek": {
            "laudato_si": {
                "year": 2015,
                "topic": "Troska o wspólny dom",
                "key_points": [
                    "Ekologia integralna",
                    "Odpowiedzialność za stworzenie",
                    "Dialog dla przyszłości planety"
                ]
            },
            "fratelli_tutti": {
                "year": 2020,
                "topic": "O braterstwie i przyjaźni społecznej",
                "key_points": [
                    "Uniwersalne braterstwo",
                    "Dobry Samarytanin jako wzór",
                    "Dialog i przyjaźń społeczna"
                ]
            }
        }
    }

    # APPROVED MARIAN APPARITIONS
    APPROVED_APPARITIONS = [
        ApprovedMiracle(
            name="Objawienia w Guadalupe",
            year="1531",
            location="Meksyk",
            description="Matka Boża ukazała się Juanowi Diego, pozostawiając swój obraz na tilmie",
            approved_by="Kościół Katolicki",
            key_elements=["Tilma Juana Diego", "Obraz Matki Bożej", "Masowe nawrócenia Azteków"]
        ),
        ApprovedMiracle(
            name="Objawienia w Lourdes",
            year="1858",
            location="Francja",
            description="Niepokalana ukazała się Bernadecie Soubirous 18 razy",
            approved_by="Papież Pius IX",
            key_elements=["Bernadetta Soubirous", "Źródło uzdrowień", "70 uznanych cudów medycznych"]
        ),
        ApprovedMiracle(
            name="Objawienia w Fatimie",
            year="1917",
            location="Portugalia",
            description="Matka Boża ukazała się trójce pastuszków z orędziem pokoju i nawrócenia",
            approved_by="Kościół Katolicki",
            key_elements=["Trzej pastuszkowie", "Trzy tajemnice", "Cud słońca 13.10.1917"]
        ),
    ]

    # EUCHARISTIC MIRACLES
    EUCHARISTIC_MIRACLES = [
        ApprovedMiracle(
            name="Cud Eucharystyczny w Lanciano",
            year="VIII wiek",
            location="Włochy",
            description="Hostia przemieniła się w tkankę serca, a wino w krew",
            approved_by="Kościół Katolicki, potwierdzone naukowo",
            key_elements=["Tkanka mięśnia sercowego", "Krew grupy AB", "Zachowane przez wieki"]
        ),
        ApprovedMiracle(
            name="Cud w Buenos Aires",
            year="1996",
            location="Argentyna",
            description="Upuszczona Hostia przemieniła się w tkankę serca",
            approved_by="Badania naukowe potwierdziły",
            key_elements=["Tkanka serca w stanie agonii", "Badania Prof. Zugibe"]
        ),
    ]

    # CHURCH FATHERS QUOTES
    CHURCH_FATHERS = {
        "augustyn": {
            "name": "Święty Augustyn z Hippony",
            "era": "354-430",
            "quotes": [
                "Niespokojne jest nasze serce, dopóki nie spocznie w Tobie.",
                "Późno Cię umiłowałem, Piękności tak dawna a tak nowa.",
                "Módl się tak, jakby wszystko zależało od Boga. Działaj tak, jakby wszystko zależało od ciebie.",
            ]
        },
        "tomasz": {
            "name": "Święty Tomasz z Akwinu",
            "era": "1225-1274",
            "quotes": [
                "Wiara szuka zrozumienia.",
                "Lęk jest przyczyną wszelkiej niewoli, miłość jest matką wolności.",
                "Łaska nie niszczy natury, lecz ją doskonali.",
            ]
        },
        "franciszek_z_asyzu": {
            "name": "Święty Franciszek z Asyżu",
            "era": "1181-1226",
            "quotes": [
                "Panie, uczyń mnie narzędziem Twego pokoju.",
                "Zacznij od tego, co konieczne, potem rób to, co możliwe, a wkrótce będziesz robił rzeczy niemożliwe.",
                "Głoście Ewangelię, a gdy to konieczne - używajcie słów.",
            ]
        },
        "teresa_z_avili": {
            "name": "Święta Teresa z Avili",
            "era": "1515-1582",
            "quotes": [
                "Niech nic cię nie niepokoi, niech nic cię nie przeraża. Wszystko mija, Bóg się nie zmienia.",
                "Chrystus nie ma teraz na ziemi innego ciała niż twoje.",
            ]
        },
        "jan_od_krzyza": {
            "name": "Święty Jan od Krzyża",
            "era": "1542-1591",
            "quotes": [
                "Pod wieczór życia będziemy sądzeni z miłości.",
                "Aby dojść do tego, czego nie znasz, musisz iść drogą, której nie znasz.",
            ]
        }
    }

    # FRUITS OF THE HOLY SPIRIT
    FRUITS_OF_SPIRIT = [
        "miłość", "radość", "pokój", "cierpliwość", "uprzejmość",
        "dobroć", "wierność", "łagodność", "opanowanie"
    ]

    # SPIRITUAL JOURNEY STAGES (for narrative)
    SPIRITUAL_JOURNEY_STAGES = [
        {
            "name": "Życie przed wiarą / kryzys",
            "description": "Bohater żyje bez Boga lub w kryzysie duchowym",
            "narrative_elements": ["pustka", "poszukiwanie sensu", "rozczarowanie światem"]
        },
        {
            "name": "Pierwsze dotknięcie łaski",
            "description": "Pierwszy kontakt z wiarą, iskra nadziei",
            "narrative_elements": ["niespodziewane spotkanie", "pytania", "ciekawość"]
        },
        {
            "name": "Opór i wątpliwości",
            "description": "Bohater walczy z wiarą, ma pytania",
            "narrative_elements": ["intelektualne obiekcje", "strach przed zmianą", "wątpliwości"]
        },
        {
            "name": "Spotkanie z autentycznym świadectwem",
            "description": "Spotkanie z osobą żyjącą wiarą przekonuje",
            "narrative_elements": ["świadek wiary", "autentyczność", "przykład życia"]
        },
        {
            "name": "Ciemna noc duszy",
            "description": "Moment kryzysu, pozorne oddalenie Boga",
            "narrative_elements": ["samotność", "próba", "cierpienie oczyszczające"]
        },
        {
            "name": "Punkt nawrócenia",
            "description": "Decyzja za Bogiem, moment przełomu",
            "narrative_elements": ["decyzja", "łzy", "nowe życie"]
        },
        {
            "name": "Próba wiary",
            "description": "Testowanie nowej wiary przez życie",
            "narrative_elements": ["trudności", "wytrwałość", "wzrost"]
        },
        {
            "name": "Pogłębienie relacji z Bogiem",
            "description": "Rozwój życia modlitwy i sakramentalnego",
            "narrative_elements": ["modlitwa", "sakramenty", "wspólnota"]
        },
        {
            "name": "Misja / dzielenie się wiarą",
            "description": "Bohater zaczyna dzielić się wiarą",
            "narrative_elements": ["świadectwo", "apostolat", "służba"]
        },
        {
            "name": "Owoce Ducha Świętego",
            "description": "Widoczna przemiana życia",
            "narrative_elements": ["miłość", "radość", "pokój", "cierpliwość"]
        }
    ]

    def get_scripture_for_theme(self, theme: str) -> List[ScriptureReference]:
        """Get relevant Scripture references for a theme."""
        return self.SCRIPTURE_BY_THEME.get(theme.lower(), [])

    def get_encyclical_info(self, pope: str, encyclical: str) -> Optional[Dict]:
        """Get information about a papal encyclical."""
        pope_enc = self.ENCYCLICALS.get(pope.lower(), {})
        return pope_enc.get(encyclical.lower())

    def get_miracle_for_context(self, context: str) -> Optional[ApprovedMiracle]:
        """Get a relevant approved miracle for the context."""
        context_lower = context.lower()

        # Check for Marian context
        if any(word in context_lower for word in ["maryja", "matka boża", "niepokalana"]):
            return self.APPROVED_APPARITIONS[0]  # Return first Marian apparition

        # Check for Eucharistic context
        if any(word in context_lower for word in ["eucharystia", "komunia", "hostia", "msza"]):
            return self.EUCHARISTIC_MIRACLES[0]

        return None

    def get_church_father_quote(self, father: str = None) -> Dict:
        """Get a quote from Church Father."""
        if father and father.lower() in self.CHURCH_FATHERS:
            return self.CHURCH_FATHERS[father.lower()]

        # Random father
        import random
        return random.choice(list(self.CHURCH_FATHERS.values()))

    def get_spiritual_journey_stage(self, stage_number: int) -> Optional[Dict]:
        """Get a specific stage of spiritual journey."""
        if 0 <= stage_number < len(self.SPIRITUAL_JOURNEY_STAGES):
            return self.SPIRITUAL_JOURNEY_STAGES[stage_number]
        return None

    def get_all_themes(self) -> List[str]:
        """Get all available Scripture themes."""
        return list(self.SCRIPTURE_BY_THEME.keys())


# Singleton instance
_religious_kb: Optional[ReligiousKnowledgeBase] = None


def get_religious_knowledge_base() -> ReligiousKnowledgeBase:
    """Get or create religious knowledge base instance."""
    global _religious_kb
    if _religious_kb is None:
        _religious_kb = ReligiousKnowledgeBase()
    return _religious_kb
