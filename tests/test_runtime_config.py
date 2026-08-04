import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def test_env_example_mentions_redis_and_postgres():
    env_example = ROOT / ".env.example"
    contents = env_example.read_text(encoding="utf-8")
    assert "REDIS_URL" in contents
    assert "POSTGRES_DB" in contents


def test_settings_module_imports_without_errors(monkeypatch):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "metaguard_project.settings")
    import metaguard_project.settings as settings_module

    importlib.reload(settings_module)
    assert settings_module.BASE_DIR.exists()
