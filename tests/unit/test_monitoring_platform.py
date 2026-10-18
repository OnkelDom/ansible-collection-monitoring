import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "monitoring_platform", Path(__file__).resolve().parents[2] / "plugins/filter/monitoring_platform.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_annotations_only_and_no_mutation():
    source = {"groups": [{"rules": [{"alert": "Disk", "expr": "disk > 80", "for": "15m",
                                    "labels": {"severity": "warning"},
                                    "annotations": {"summary": "Disk"}},
                                   {"record": "disk", "expr": "raw"}]}]}
    result = module.monitoring_platform_annotations(source, [{"alertname": "Disk", "annotations": {
        "action": {"linux": "df -h", "windows": "Get-Volume", "unknown": "Plattform prüfen"}}}])
    rule = result["groups"][0]["rules"][0]
    assert rule.pop("annotations")["action"] == (
        '{{ if eq $labels.platform "windows" }}Get-Volume{{ else if eq $labels.platform "linux" }}df -h'
        '{{ else }}Plattform prüfen{{ end }}')
    original = source["groups"][0]["rules"][0].copy()
    original.pop("annotations")
    assert rule == original
    assert source["groups"][0]["rules"][0]["annotations"] == {"summary": "Disk"}
    assert result["groups"][0]["rules"][1] == source["groups"][0]["rules"][1]


def test_fixed_platform_and_neutral_fallback():
    variants = {"linux": "df -h", "windows": "Get-Volume"}
    assert module.monitoring_platform_text(variants, "windows") == "Get-Volume"
    assert module.monitoring_platform_text(variants, "linux") == "df -h"
    assert "Betriebssystem nicht eindeutig bekannt" in module.monitoring_platform_text(variants)


def test_invalid_platform_does_not_guess():
    with pytest.raises(ValueError):
        module.monitoring_platform_text({"win32": "wrong"})
