"""
System Iteracji i Rewizji dla NARRA_FORGE.
Umożliwia poprawianie i regenerację wygenerowanych narracji.
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
import os
from pathlib import Path

from .types import PipelineStage


class RevisionSystem:
    """
    System zarządzania rewizjami i wersjami projektów.

    Funkcje:
    - Zapisywanie snapshots kontekstu po każdym etapie
    - Wczytywanie poprzednich kontekstów
    - Wersjonowanie projektów
    - Porównywanie wersji
    """

    def __init__(self, storage_path: str = "data/revisions"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def save_context_snapshot(
        self,
        project_id: str,
        stage: PipelineStage,
        context: Dict[str, Any],
        version: int = 1
    ) -> str:
        """
        Zapisz snapshot kontekstu po danym etapie.

        Args:
            project_id: ID projektu
            stage: Etap pipeline'u
            context: Kontekst do zapisania
            version: Numer wersji

        Returns:
            Ścieżka do zapisanego pliku
        """
        project_dir = self.storage_path / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        snapshot_name = f"v{version}_stage{stage.value}_{stage.name}.json"
        snapshot_path = project_dir / snapshot_name

        # Przygotuj dane do zapisu (pomiń obiekty które nie są JSON-serializable)
        serializable_context = self._make_serializable(context)

        snapshot_data = {
            "project_id": project_id,
            "version": version,
            "stage": stage.name,
            "stage_number": stage.value,
            "timestamp": datetime.now().isoformat(),
            "context": serializable_context
        }

        with open(snapshot_path, 'w', encoding='utf-8') as f:
            json.dump(snapshot_data, f, ensure_ascii=False, indent=2)

        return str(snapshot_path)

    def load_context_snapshot(
        self,
        project_id: str,
        stage: PipelineStage,
        version: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Wczytaj snapshot kontekstu z danego etapu.

        Args:
            project_id: ID projektu
            stage: Etap pipeline'u
            version: Numer wersji

        Returns:
            Kontekst lub None jeśli nie znaleziono
        """
        project_dir = self.storage_path / project_id
        snapshot_name = f"v{version}_stage{stage.value}_{stage.name}.json"
        snapshot_path = project_dir / snapshot_name

        if not snapshot_path.exists():
            return None

        with open(snapshot_path, 'r', encoding='utf-8') as f:
            snapshot_data = json.load(f)

        return snapshot_data.get("context")

    def get_latest_version(self, project_id: str) -> int:
        """
        Pobierz numer najnowszej wersji projektu.

        Args:
            project_id: ID projektu

        Returns:
            Numer najnowszej wersji
        """
        project_dir = self.storage_path / project_id

        if not project_dir.exists():
            return 1

        versions = set()
        for file in project_dir.glob("v*_stage*.json"):
            # Wyciągnij numer wersji z nazwy pliku
            version_str = file.stem.split('_')[0][1:]  # v1 -> 1
            try:
                versions.add(int(version_str))
            except ValueError:
                continue

        return max(versions) if versions else 1

    def list_versions(self, project_id: str) -> List[Dict[str, Any]]:
        """
        Lista wszystkich wersji projektu.

        Args:
            project_id: ID projektu

        Returns:
            Lista informacji o wersjach
        """
        project_dir = self.storage_path / project_id

        if not project_dir.exists():
            return []

        versions_data = {}

        for file in project_dir.glob("v*_stage*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                version = data['version']
                if version not in versions_data:
                    versions_data[version] = {
                        "version": version,
                        "stages": [],
                        "created_at": data['timestamp']
                    }

                versions_data[version]["stages"].append({
                    "stage": data['stage'],
                    "stage_number": data['stage_number'],
                    "timestamp": data['timestamp']
                })

            except Exception:
                continue

        # Sortuj wersje
        versions_list = sorted(versions_data.values(), key=lambda x: x['version'], reverse=True)

        # Sortuj etapy w każdej wersji
        for version in versions_list:
            version["stages"].sort(key=lambda x: x['stage_number'])

        return versions_list

    def compare_versions(
        self,
        project_id: str,
        version1: int,
        version2: int,
        stage: PipelineStage
    ) -> Dict[str, Any]:
        """
        Porównaj dwie wersje projektu na danym etapie.

        Args:
            project_id: ID projektu
            version1: Pierwsza wersja
            version2: Druga wersja
            stage: Etap do porównania

        Returns:
            Raport porównania
        """
        context1 = self.load_context_snapshot(project_id, stage, version1)
        context2 = self.load_context_snapshot(project_id, stage, version2)

        if not context1 or not context2:
            return {
                "error": "Nie znaleziono jednej lub obu wersji"
            }

        # Podstawowe porównanie
        return {
            "project_id": project_id,
            "version1": version1,
            "version2": version2,
            "stage": stage.name,
            "differences": self._find_differences(context1, context2)
        }

    def _make_serializable(self, obj: Any) -> Any:
        """
        Konwertuj obiekt na JSON-serializable format.

        Args:
            obj: Obiekt do konwersji

        Returns:
            JSON-serializable wersja obiektu
        """
        if isinstance(obj, dict):
            return {k: self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            # Obiekty z __dict__ (np. WorldBible, Character)
            return self._make_serializable(obj.__dict__)
        else:
            # Dla innych typów zwróć string representation
            return str(obj)

    def _find_differences(self, obj1: Any, obj2: Any, path: str = "") -> List[Dict[str, Any]]:
        """
        Znajdź różnice między dwoma obiektami.

        Args:
            obj1: Pierwszy obiekt
            obj2: Drugi obiekt
            path: Ścieżka do aktualnego obiektu

        Returns:
            Lista różnic
        """
        differences = []

        if type(obj1) != type(obj2):
            differences.append({
                "path": path,
                "type": "type_change",
                "from": type(obj1).__name__,
                "to": type(obj2).__name__
            })
            return differences

        if isinstance(obj1, dict):
            all_keys = set(obj1.keys()) | set(obj2.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key

                if key not in obj1:
                    differences.append({
                        "path": new_path,
                        "type": "added",
                        "value": obj2[key]
                    })
                elif key not in obj2:
                    differences.append({
                        "path": new_path,
                        "type": "removed",
                        "value": obj1[key]
                    })
                else:
                    differences.extend(self._find_differences(obj1[key], obj2[key], new_path))

        elif isinstance(obj1, list):
            if len(obj1) != len(obj2):
                differences.append({
                    "path": path,
                    "type": "length_change",
                    "from": len(obj1),
                    "to": len(obj2)
                })

            for i in range(min(len(obj1), len(obj2))):
                new_path = f"{path}[{i}]"
                differences.extend(self._find_differences(obj1[i], obj2[i], new_path))

        elif obj1 != obj2:
            differences.append({
                "path": path,
                "type": "value_change",
                "from": obj1,
                "to": obj2
            })

        return differences


class RevisionRequest:
    """Żądanie rewizji projektu."""

    def __init__(
        self,
        project_id: str,
        from_stage: PipelineStage,
        instructions: Optional[str] = None,
        context_modifications: Optional[Dict[str, Any]] = None,
        create_new_version: bool = True
    ):
        self.project_id = project_id
        self.from_stage = from_stage
        self.instructions = instructions
        self.context_modifications = context_modifications or {}
        self.create_new_version = create_new_version
