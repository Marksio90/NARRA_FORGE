"""
Genre Excellence Prompts for NarraForge 2.0

Genre-specific writing standards for bestseller-level quality.
Each genre has unique requirements for excellence.
"""

from typing import Dict
from app.models.project import GenreType


GENRE_EXCELLENCE_PROMPTS: Dict[GenreType, str] = {
    GenreType.FANTASY: """
FANTASY EXCELLENCE STANDARDS:

WORLD-BUILDING:
- Magia musi mieć KOSZTY i OGRANICZENIA (hard magic system)
- Każda kultura ma unikalną historię, język, zwyczaje
- Geografia wpływa na politykę i konflikty
- Ekosystem jest spójny i logiczny
- Magia ma jasne zasady, które są KONSEKWENTNE

POSTACIE:
- Bohater ma wady, które naprawdę mu szkodzą
- Mentor NIE rozwiązuje problemów za bohatera
- Złoczyńca wierzy w słuszność swoich działań
- Poboczne postacie mają własne cele i życie
- Postacie są produktami swoich kultur

FABUŁA:
- Stawki rosną ORGANICZNIE, nie sztucznie
- Każda bitwa ma konsekwencje (ranni, zmarli, trauma)
- Magia NIE jest deus ex machina
- Zwycięstwo wymaga POŚWIĘCENIA
- Profekie są ambiwalentne, nie dosłowne

STYL:
- Opisy świata przez oczy postaci, NIE wykłady
- Akcja jest klarowna przestrzennie
- Dialog ujawnia charakter i konflikt
- Poetyckie momenty w WŁAŚCIWYCH miejscach (nie wszędzie)
- Unikaj "Tolkien-speak" - niech dialog będzie naturalny

UNIKAJ:
- Info-dumpów ("Jak wiesz, Janie...")
- Wybrańców bez żadnej ceny
- Magii bez ograniczeń
- Ras jako monolit (wszyscy elfowie są...)
- Zbyt wielu wymyślonych nazw na raz
""",

    GenreType.THRILLER: """
THRILLER EXCELLENCE STANDARDS:

NAPIĘCIE:
- Rozpocznij IN MEDIA RES lub z silnym hakiem
- KAŻDA scena podnosi stawki
- Tykający zegar - deadline jest REALNY
- Red herrings są fair play (możliwe do odgadnięcia)
- Sekrety ujawniane stopniowo, nie naraz

PROTAGONISTA:
- Ma specyficzne umiejętności, ale i wyraźne SŁABOŚCI
- Osobiste stawki + zewnętrzne stawki
- Musi dokonywać MORALNIE TRUDNYCH wyborów
- Trauma z przeszłości wpływa na decyzje TERAZ
- Błędy mają konsekwencje

ANTAGONISTA:
- Jest o krok przed bohaterem (aż do kulminacji)
- Ma LOGICZNE motywacje (nie "bo jest zły")
- Stanowi OSOBISTE zagrożenie dla bohatera
- Zdolny do zaskakujących, ale logicznych posunięć
- Może mieć rację w niektórych kwestiach

STRUKTURA:
- Cliffhangery na końcu rozdziałów (OBOWIĄZKOWE)
- Przeplatanie wątków dla maksymalnego napięcia
- Fałszywe kulminacje przed prawdziwą
- Rozwiązanie jest satysfakcjonujące ale NIE przewidywalne
- Tempo: nigdy nie pozwól czytelnikowi odetchnąć

UNIKAJ:
- Głupich błędów bohaterów tylko dla fabuły
- "Wiem wszystko" antagonistów
- Przypadkowych rozwiązań
- Porzuconych wątków
- Opowiadania zamiast pokazywania napięcia
""",

    GenreType.ROMANCE: """
ROMANCE EXCELLENCE STANDARDS:

CHEMIA:
- Napięcie romantyczne od PIERWSZEGO spotkania
- Przeszkody są WEWNĘTRZNE, nie tylko zewnętrzne
- Momenty intymności (niekoniecznie fizycznej)
- Dialogi z subtekstem - co NIE mówią
- Drobne gesty znaczą więcej niż wielkie deklaracje

PROTAGONIŚCI:
- Oboje mają pełne życie POZA związkiem
- Każde ma "lie" (fałszywe przekonanie) do pokonania
- Wzajemnie się ZMIENIAJĄ na lepsze
- Mają chemię słowną (banter, przekomarzanie)
- Są równorzędnymi partnerami

STRUKTURA:
- Meet cute lub intrygujące poznanie
- Rosnąca bliskość MIMO przeszkód
- "Dark moment" gdy wszystko wydaje się stracone
- Grand gesture + HEA/HFN
- Przeszkody logiczne, nie sztuczne

EMOCJE:
- Czytelnik KIBICUJE parze
- Momenty słodkie, gorące i bolesne
- Vulnerability (bezbronność) obu stron
- Cathartic payoff (satysfakcjonujące spełnienie)

UNIKAJ:
- Toksycznych zachowań romantyzowanych
- "Nie lubię, ale kocham" bez rozwoju
- Jednego partnera "naprawiającego" drugiego
- Zewnętrznych przeszkód zamiast wewnętrznych
- Big misunderstanding jako głównej przeszkody
""",

    GenreType.HORROR: """
HORROR EXCELLENCE STANDARDS:

ATMOSFERA:
- Dread (niepokój) > Jump scares
- Sugestia > Eksplicytność
- Normalne staje się DZIWNE
- Cisza jest przerażająca
- Buduj powoli, potem atakuj

PROTAGONISTA:
- Ma coś do stracenia (rodzina, zdrowie psychiczne, życie)
- Decyzje są ZROZUMIAŁE (nie "idiotka idzie do piwnicy")
- Strach jest RELATABLE (uniwersalny)
- Walczy, nie jest tylko ofiarą
- Zmienia się przez doświadczenie

ZAGROŻENIE:
- Zasady są SPÓJNE (nawet jeśli nieznane bohaterowi)
- Pokazuj mało, sugeruj dużo
- Realny koszt dla bohaterów (nie plot armor)
- Niekoniecznie pokonane na końcu
- Zostaw miejsce na wyobraźnię czytelnika

PSYCHOLOGIA:
- Lęki uniwersalne (śmierć, samotność, utrata kontroli)
- Paranoja czytelnika (czy to już się zaczyna?)
- Granica realność/koszmar zamazana
- Końcówka pozostawia NIEPOKÓJ
- Prawdziwy horror jest w głowie, nie w potworze

UNIKAJ:
- Gore dla samego gore
- "Wyjaśniania" zbyt dużo
- Głupich postaci (tylko żeby mogły zginąć)
- Happy endings bez kosztów
- Przewidywalnych jump scares
""",

    GenreType.MYSTERY: """
MYSTERY/CRIME EXCELLENCE STANDARDS:

ZAGADKA:
- Fair play - wszystkie wskazówki dostępne czytelnikowi
- Rozwiązanie zaskakujące ale LOGICZNE
- Fałszywe tropy prowadzą gdzieś (nie ślepe uliczki)
- Prawda jest gorsza/bardziej skomplikowana niż przypuszczenia
- Clue planting subtelny ale uczciwy

DETEKTYW/PROTAGONISTA:
- Unikalny sposób myślenia/metodologia
- Wady osobiste NIE przeszkadzają w śledztwie
- Motywacja osobista do rozwiązania
- Błędne założenia, które koryguje
- Rozwój przez śledztwo

STRUKTURA:
- Hook z zagadką/zbrodnią na początku
- Komplikacje gdy rozwiązanie wydaje się bliskie
- Red herrings fair (ale mylące)
- Revelation zorganizowane dla max impactu
- Rozwiązanie odpowiada na WSZYSTKIE pytania

ATMOSPHERE:
- Każdy może być winny (lub ofiarą)
- Napięcie rośnie wraz ze śledztwem
- Przeszłość wpływa na teraźniejszość
- Prawda jest niebezpieczna

UNIKAJ:
- Ukrywania kluczowych informacji przed czytelnikiem
- Deus ex machina rozwiązań
- "Wiem od początku" detektywów
- Zbyt wielu postaci do śledzenia
- Niezwiązanych z fabułą opisów
""",

    GenreType.SCI_FI: """
SCIENCE FICTION EXCELLENCE STANDARDS:

TECHNOLOGIA/NAUKA:
- Spójny system technologiczny z REGUŁAMI
- Technologia ma implikacje społeczne
- Sense of wonder (zachować poczucie cudu)
- Hard SF: zasady fizyki respektowane
- Soft SF: konsekwencja wewnętrzna

ŚWIAT:
- Społeczeństwo logicznie wynika z technologii
- Nie tylko gadżety - kultura, polityka, ekonomia
- Dystopia/utopia uzasadniona
- Obcy są OBCY (nie ludzie z gumowymi uszami)
- Skala kosmiczna z ludzkim sercem

POSTACIE:
- Reagują na technologię jak PRAWDZIWI ludzie
- Konflikty uniwersalne w nowym kontekście
- Człowieczeństwo testowane przez posthumanizm
- Bohaterowie aktywni, nie tylko świadkowie świata
- Diversity naturalna (przyszłość jest różnorodna)

STYL:
- Opisy technologii przez użycie, nie wykłady
- Żargon minimalny, znaczący
- Spekulacja oparta na trendach
- Pytania filozoficzne wplecione w akcję
- "What if" doprowadzone do logicznych konsekwencji

UNIKAJ:
- Techno-babblu bez znaczenia
- "Magicznej" technologii
- Monokulturowych planet
- Kolonialnych narracji bez krytyki
- Scenografii bez wpływu na fabułę
""",

    GenreType.DRAMA: """
DRAMA EXCELLENCE STANDARDS:

KONFLIKT:
- Wewnętrzny > zewnętrzny
- Moralne dylematy bez łatwych odpowiedzi
- Prawdziwe konsekwencje wyborów
- Relacje jako pole bitwy
- Każda postać ma rację (z jej perspektywy)

POSTACIE:
- Pełne, wielowymiarowe osoby
- Motywacje zrozumiałe nawet gdy nieakceptowalne
- Transformacja przez cierpienie
- Dialog ujawnia charakter
- Subtelność > melodramat

STRUKTURA:
- Wolniejsze tempo, głębsza penetracja
- Momenty ciszy znaczą wiele
- Kulminacja emocjonalna, nie akcyjna
- Rozwiązanie może być ambiwalentne
- Epilog pokazuje długoterminowe skutki

TON:
- Autentyzm emocjonalny
- Unikaj sentymentalizmu
- Nadzieja może być cicha
- Uniwersalne prawdy przez szczegółowe życia
- Szacunek dla złożoności ludzkiej

UNIKAJ:
- Melodramatu (przesadnych emocji)
- Postaci-symboli zamiast ludzi
- "Message fiction" (przesłanie przed historią)
- Katharsis zbyt łatwej
- Wszystkowiedzącego narratora osądzającego
""",

    GenreType.COMEDY: """
COMEDY EXCELLENCE STANDARDS:

HUMOR:
- Timing jest WSZYSTKIM
- Setup → Punchline z nieoczekiwanym twistem
- Running gags z escalation
- Character-based humor (wynika z postaci)
- Subtelność i slapstick w balansie

POSTACIE:
- Lovable losers (przegrani, których kochamy)
- Wady są ŚMIESZNE, nie irytujące
- Straight man + funny one (ale role mogą się zmieniać)
- Postacie mają cel (nie tylko są śmieszne)
- Rozwój nie niszczy komizmu

STRUKTURA:
- Escalation (każdy akt szaleńszy)
- Misunderstandings prowadzą do chaosu
- Kulminacja to maksymalny chaos
- Happy ending (ale może być bittersweet)
- Callbacks do wcześniejszych żartów

TON:
- Ciepło pod humorem
- Śmiejemy się Z postaciami, nie z nich
- Satyryczny komentarz może być
- Czarny humor ostrożnie dawkowany
- Serce nad sprytnym żartem

UNIKAJ:
- Humoru kosztem godności postaci
- Żartów dla żartów (bez fabuły)
- Cringe humor (jeśli nie zamierzony)
- Punchline'ów telegrafowanych
- Postaci świadomych że są w komedii
""",

    GenreType.RELIGIOUS: """
RELIGIOUS LITERATURE EXCELLENCE STANDARDS:

AUTENTYCZNOŚĆ DUCHOWA:
- Wiara jako RELACJA z żywym Bogiem, nie zbiór zasad
- Wątpliwości są naturalne i pokazane uczciwie
- Łaska jest DAREM, nie nagrodą za zasługi
- Nawrócenie to PROCES, nie moment
- Ciemna noc duszy jest częścią drogi

POSTACIE:
- Święci mieli SŁABOŚCI - pokazuj je uczciwie
- Grzesznicy mają GODNOŚĆ - szanuj ją
- Bóg działa PRZEZ ludzi, nie ZAMIAST nich
- Wewnętrzna walka duchowa > zewnętrzne konflikty
- Przemiana jest stopniowa i kosztowna

TEOLOGIA:
- Zgodność z nauczaniem Kościoła (Magisterium)
- Cytaty biblijne W KONTEKŚCIE
- Nauczanie PRZEZ historię, nie kazania
- Tajemnica POZOSTAJE tajemnicą
- Łaska i wolna wola w napięciu

TON:
- Nadzieja nawet w najgłębszej ciemności
- Szacunek bez sztywności
- Radość wiary, nie tylko obowiązki
- Miłosierdzie > Osąd
- Dostępność dla poszukujących

ŹRÓDŁA:
- TYLKO zatwierdzone cuda i objawienia
- Cytaty biblijne dokładne (lub wyraźnie parafrazowane)
- Nauczanie Kościoła bez zniekształceń
- Żywoty świętych z wiarygodnych źródeł

UNIKAJ:
- Taniego moralizatorstwa
- Sentymentalizmu religijnego
- Deus ex machina cudów
- Uproszczonych odpowiedzi na trudne pytania
- Przedstawiania wiary jako łatwej drogi
- Oceniania i potępiania postaci
"""
}


def get_genre_excellence_prompt(genre: GenreType) -> str:
    """Get excellence prompt for a specific genre."""
    return GENRE_EXCELLENCE_PROMPTS.get(genre, GENRE_EXCELLENCE_PROMPTS[GenreType.DRAMA])


def get_combined_writing_prompt(genre: GenreType, scene_context: str = "") -> str:
    """Get combined writing prompt with genre excellence standards."""
    excellence = get_genre_excellence_prompt(genre)

    return f"""
{excellence}

OGÓLNE ZASADY PISARSTWA:

SHOW DON'T TELL:
- Emocje przez działania, nie etykiety ("był smutny" → pokazać smutek)
- Charaktery przez zachowanie, nie opisy
- Świat przez detale, nie wykłady

DEEP POV (głęboka perspektywa):
- W głowie JEDNEJ postaci na scenę
- Brak "widział że", "czuł że" - jesteśmy TĄ postacią
- Myśli postaci w jej języku

SENSORY DETAILS (zmysły):
- Używaj WSZYSTKICH 5 zmysłów
- Specyficzne, nie ogólne detale
- Detale znaczące dla fabuły/postaci

DIALOG:
- Każda postać ma UNIKALNY głos
- Subtext > explicite mówienie
- Akcja/gest przerywa długie wymiany
- "Powiedział/a" jest niewidzialne - używaj śmiało

{scene_context}
"""
