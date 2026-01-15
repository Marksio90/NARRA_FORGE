"""
NARRA_FORGE Streamlit Dashboard
Interfejs użytkownika do generacji narracji.
"""
import streamlit as st
import requests
import time
import json
from datetime import datetime
from typing import Optional, Dict, Any

# ============================================================================
# CONFIGURATION
# ============================================================================

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="NARRA_FORGE",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .big-title {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stage-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
        background-color: #f8f9fa;
    }
    .stage-completed {
        border-left-color: #28a745;
        background-color: #d4edda;
    }
    .stage-failed {
        border-left-color: #dc3545;
        background-color: #f8d7da;
    }
    .stage-active {
        border-left-color: #ffc107;
        background-color: #fff3cd;
    }
    .metric-card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# STATE MANAGEMENT
# ============================================================================

if 'current_project_id' not in st.session_state:
    st.session_state.current_project_id = None

if 'project_status' not in st.session_state:
    st.session_state.project_status = None

# ============================================================================
# API FUNCTIONS
# ============================================================================

def generate_narrative(brief: str, form: str, genre: str, **kwargs) -> Optional[Dict]:
    """Wyślij żądanie generacji do API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/generate",
            json={
                "brief": brief,
                "form": form,
                "genre": genre,
                **kwargs
            },
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Błąd komunikacji z API: {e}")
        return None


def get_project_status(project_id: str) -> Optional[Dict]:
    """Pobierz status projektu."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/status/{project_id}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Błąd pobierania statusu: {e}")
        return None


def list_projects(status: Optional[str] = None, limit: int = 50) -> Optional[Dict]:
    """Lista projektów."""
    try:
        params = {"limit": limit}
        if status:
            params["status"] = status

        response = requests.get(
            f"{API_BASE_URL}/api/projects",
            params=params,
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Błąd pobierania projektów: {e}")
        return None


def delete_project(project_id: str) -> bool:
    """Usuń projekt."""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/projects/{project_id}",
            timeout=5
        )
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"Błąd usuwania projektu: {e}")
        return False


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_header():
    """Renderuj nagłówek."""
    st.markdown('<p class="big-title">📚 NARRA_FORGE</p>', unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align: center; font-size: 1.2rem; color: #666;'>"
        "Autonomiczny Wieloświatowy System Generowania Narracji"
        "</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")


def render_stage_progress(stages_completed: list, stages_failed: list, current_stage: Optional[str]):
    """Renderuj postęp etapów."""
    all_stages = [
        ("BRIEF_INTERPRETATION", "1. Interpretacja zlecenia"),
        ("WORLD_ARCHITECTURE", "2. Architektura świata"),
        ("CHARACTER_ARCHITECTURE", "3. Architektura postaci"),
        ("NARRATIVE_STRUCTURE", "4. Struktura narracyjna"),
        ("SEGMENT_PLANNING", "5. Planowanie segmentów"),
        ("SEQUENTIAL_GENERATION", "6. Generacja sekwencyjna"),
        ("COHERENCE_CONTROL", "7. Kontrola koherencji"),
        ("LANGUAGE_STYLIZATION", "8. Stylizacja językowa"),
        ("EDITORIAL_REVIEW", "9. Redakcja wydawnicza"),
        ("FINAL_OUTPUT", "10. Finalne wyjście")
    ]

    st.subheader("📊 Postęp produkcji")

    for stage_key, stage_name in all_stages:
        if stage_key in stages_completed:
            st.markdown(
                f'<div class="stage-box stage-completed">✅ {stage_name}</div>',
                unsafe_allow_html=True
            )
        elif stage_key in stages_failed:
            st.markdown(
                f'<div class="stage-box stage-failed">❌ {stage_name}</div>',
                unsafe_allow_html=True
            )
        elif stage_key == current_stage:
            st.markdown(
                f'<div class="stage-box stage-active">⏳ {stage_name} (w trakcie...)</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="stage-box">⚪ {stage_name}</div>',
                unsafe_allow_html=True
            )


def render_metrics(status_data: Dict):
    """Renderuj metryki projektu."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Status",
            value=status_data["status"].upper(),
            delta=None
        )

    with col2:
        progress_pct = int(status_data["progress"] * 100)
        st.metric(
            label="Postęp",
            value=f"{progress_pct}%",
            delta=None
        )

    with col3:
        st.metric(
            label="Etapy ukończone",
            value=f"{len(status_data['stages_completed'])}/10",
            delta=None
        )

    with col4:
        if status_data.get("completed_at"):
            created = datetime.fromisoformat(status_data["created_at"])
            completed = datetime.fromisoformat(status_data["completed_at"])
            duration = (completed - created).total_seconds()
            st.metric(
                label="Czas trwania",
                value=f"{int(duration)}s",
                delta=None
            )
        else:
            st.metric(
                label="Czas trwania",
                value="W trakcie...",
                delta=None
            )


# ============================================================================
# PAGES
# ============================================================================

def page_new_generation():
    """Strona nowej generacji."""
    st.header("🎬 Nowa Generacja Narracji")

    with st.form("generation_form"):
        # Brief
        brief = st.text_area(
            "📝 Zlecenie narracyjne",
            height=200,
            placeholder="""Opisz co chcesz stworzyć...

Przykład:
Stwórz mroczne opowiadanie science fiction osadzone w umierającym systemie gwiezdnym.
Główny bohater to ostatni pilot transportowy, który odkrywa tajemniczy ładunek
mogący ocalić lub zniszczyć pozostałych przy życiu ludzi..."""
        )

        col1, col2 = st.columns(2)

        with col1:
            form = st.selectbox(
                "📖 Forma",
                options=["short_story", "novella", "novel", "epic"],
                format_func=lambda x: {
                    "short_story": "Opowiadanie (5-15k słów)",
                    "novella": "Nowela (15-50k słów)",
                    "novel": "Powieść (50-120k słów)",
                    "epic": "Epopeja (120k+ słów)"
                }[x]
            )

            genre = st.selectbox(
                "🎭 Gatunek",
                options=["sci_fi", "fantasy", "horror", "thriller", "drama", "mystery"],
                format_func=lambda x: {
                    "sci_fi": "Science Fiction",
                    "fantasy": "Fantasy",
                    "horror": "Horror",
                    "thriller": "Thriller",
                    "drama": "Dramat",
                    "mystery": "Kryminał"
                }[x]
            )

        with col2:
            world_scale = st.selectbox(
                "🌍 Skala świata",
                options=["intimate", "regional", "global", "cosmic"],
                format_func=lambda x: {
                    "intimate": "Intymna (mały, osobisty świat)",
                    "regional": "Regionalna (miasta, królestwa)",
                    "global": "Globalna (planety, cywilizacje)",
                    "cosmic": "Kosmiczna (galaktyki, multiwersum)"
                }[x]
            )

            expansion = st.selectbox(
                "📚 Potencjał ekspansji",
                options=["standalone", "series", "universe"],
                format_func=lambda x: {
                    "standalone": "Samodzielne (pojedyncza historia)",
                    "series": "Seria (planowane kontynuacje)",
                    "universe": "Uniwersum (wieloświatowe)"
                }[x]
            )

        # Fokus tematyczny
        thematic_focus = st.multiselect(
            "🎯 Fokus tematyczny",
            options=["survival", "morality", "identity", "power", "love", "death", "time", "technology"],
            default=["survival", "morality"],
            format_func=lambda x: {
                "survival": "Przetrwanie",
                "morality": "Moralność",
                "identity": "Tożsamość",
                "power": "Władza",
                "love": "Miłość",
                "death": "Śmierć",
                "time": "Czas",
                "technology": "Technologia"
            }[x]
        )

        # Zaawansowane opcje
        with st.expander("⚙️ Zaawansowane opcje"):
            preferred_model = st.selectbox(
                "Model AI",
                options=["gpt-4-turbo", "gpt-3.5-turbo", "gpt-4", "claude-sonnet", "claude-opus"],
                index=0
            )

            temperature = st.slider(
                "Temperature (kreatywność)",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1
            )

        # Submit
        submitted = st.form_submit_button("🚀 Rozpocznij generację", use_container_width=True)

        if submitted:
            if not brief:
                st.error("Proszę podać opis zlecenia narracyjnego!")
                return

            with st.spinner("Wysyłanie zlecenia do systemu..."):
                result = generate_narrative(
                    brief=brief,
                    form=form,
                    genre=genre,
                    world_scale=world_scale,
                    thematic_focus=thematic_focus,
                    expansion_potential=expansion,
                    preferred_model=preferred_model,
                    temperature=temperature
                )

                if result:
                    st.session_state.current_project_id = result["project_id"]
                    st.success(f"✅ Projekt utworzony! ID: {result['project_id']}")
                    st.info(f"Status: {result['message']}")
                    time.sleep(1)
                    st.rerun()


def page_monitor():
    """Strona monitorowania."""
    st.header("📊 Monitor Projektów")

    if not st.session_state.current_project_id:
        st.warning("Brak aktywnego projektu. Rozpocznij nową generację w zakładce 'Nowa Generacja'.")
        return

    project_id = st.session_state.current_project_id

    # Przyciski
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("🔄 Odśwież"):
            st.rerun()
    with col2:
        if st.button("❌ Zakończ monitoring"):
            st.session_state.current_project_id = None
            st.rerun()

    st.markdown("---")

    # Pobierz status
    with st.spinner("Pobieranie statusu..."):
        status = get_project_status(project_id)

    if not status:
        st.error("Nie udało się pobrać statusu projektu")
        return

    # Metryki
    render_metrics(status)

    st.markdown("---")

    # Postęp etapów
    col1, col2 = st.columns([2, 1])

    with col1:
        render_stage_progress(
            status["stages_completed"],
            status["stages_failed"],
            status.get("current_stage")
        )

    with col2:
        st.subheader("ℹ️ Informacje")
        st.write(f"**ID projektu:** `{project_id}`")
        st.write(f"**Utworzono:** {status['created_at']}")

        if status.get("started_at"):
            st.write(f"**Rozpoczęto:** {status['started_at']}")

        if status.get("completed_at"):
            st.write(f"**Ukończono:** {status['completed_at']}")

        if status.get("error"):
            st.error(f"**Błąd:** {status['error']}")

    # Auto-refresh jeśli w trakcie
    if status["status"] == "processing":
        time.sleep(2)
        st.rerun()

    # Pliki wyjściowe
    if status["status"] == "completed" and status.get("output_files"):
        st.markdown("---")
        st.subheader("📁 Pliki wyjściowe")

        for file_type, file_path in status["output_files"].items():
            st.write(f"**{file_type}:** `{file_path}`")


def page_projects():
    """Strona listy projektów."""
    st.header("📚 Wszystkie Projekty")

    # Filtry
    col1, col2 = st.columns([1, 3])

    with col1:
        status_filter = st.selectbox(
            "Filtruj po statusie",
            options=[None, "queued", "processing", "completed", "failed"],
            format_func=lambda x: {
                None: "Wszystkie",
                "queued": "W kolejce",
                "processing": "W trakcie",
                "completed": "Ukończone",
                "failed": "Nieudane"
            }[x]
        )

    # Pobierz projekty
    with st.spinner("Ładowanie projektów..."):
        result = list_projects(status=status_filter)

    if not result:
        st.error("Nie udało się pobrać listy projektów")
        return

    projects = result.get("projects", [])

    st.write(f"Znaleziono **{result['total']}** projektów")

    # Lista projektów
    for project in projects:
        with st.expander(f"🎬 {project['id']} - {project['status'].upper()}"):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.write(f"**Status:** {project['status']}")
                st.write(f"**Utworzono:** {project['created_at']}")
                st.write(f"**Etapy ukończone:** {len(project['stages_completed'])}/10")

                if project.get("error"):
                    st.error(f"**Błąd:** {project['error']}")

            with col2:
                if st.button("👁️ Monitoruj", key=f"monitor_{project['id']}"):
                    st.session_state.current_project_id = project['id']
                    st.rerun()

                if project["status"] in ["completed", "failed"]:
                    if st.button("🗑️ Usuń", key=f"delete_{project['id']}"):
                        if delete_project(project['id']):
                            st.success("Projekt usunięty!")
                            time.sleep(1)
                            st.rerun()


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Główna aplikacja."""
    render_header()

    # Sidebar
    with st.sidebar:
        st.title("📋 Menu")

        page = st.radio(
            "Wybierz stronę:",
            options=["new", "monitor", "projects"],
            format_func=lambda x: {
                "new": "🎬 Nowa Generacja",
                "monitor": "📊 Monitor",
                "projects": "📚 Wszystkie Projekty"
            }[x]
        )

        st.markdown("---")

        # Status API
        try:
            health = requests.get(f"{API_BASE_URL}/health", timeout=2).json()
            st.success("✅ API połączone")
            st.write(f"Aktywne projekty: {health['active_projects']}")
        except:
            st.error("❌ Brak połączenia z API")

        st.markdown("---")
        st.caption("NARRA_FORGE v1.0.0")

    # Routing
    if page == "new":
        page_new_generation()
    elif page == "monitor":
        page_monitor()
    elif page == "projects":
        page_projects()


if __name__ == "__main__":
    main()
