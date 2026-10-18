"""Compile platform-specific annotations without changing alert behaviour."""
from copy import deepcopy
import re


def monitoring_platform_text(variants, platform=""):
    """Select a known platform, or defer selection to Prometheus alert labels."""
    if isinstance(variants, str):
        return variants
    if not isinstance(variants, dict) or not set(variants) <= {"linux", "windows", "unknown"}:
        raise ValueError("Annotation variants must contain linux, windows and/or unknown text")
    if any(not isinstance(value, str) for value in variants.values()):
        raise ValueError("Platform annotation values must be strings")
    fallback = variants.get("unknown", "Betriebssystem nicht eindeutig bekannt; Plattform und Messreihe vor der Diagnose prüfen.")
    if platform in ("linux", "windows"):
        return variants.get(platform, fallback)
    return ('{{ if eq $labels.platform "windows" }}' + variants.get("windows", fallback)
            + '{{ else if eq $labels.platform "linux" }}' + variants.get("linux", fallback)
            + '{{ else }}' + fallback + '{{ end }}')


def monitoring_platform_annotations(document, overrides):
    """Apply ordered annotation overrides matched by full alert-name regex.

    A platform hint refers to the monitored workload, never to the Prometheus
    server's Ansible facts. Expressions, labels and timing remain untouched.
    """
    result = deepcopy(document)
    for group in result.get("groups", []):
        for rule in group.get("rules", []):
            if "alert" not in rule:
                continue
            for override in overrides:
                if re.fullmatch(override["alertname"], rule["alert"]):
                    platform = override.get("platform", rule.get("labels", {}).get("platform", ""))
                    if platform not in ("", "linux", "windows"):
                        raise ValueError("Platform must be linux, windows or empty")
                    for key, value in override["annotations"].items():
                        rule.setdefault("annotations", {})[key] = monitoring_platform_text(value, platform)
    return result


class FilterModule:
    def filters(self):
        return {"monitoring_platform_text": monitoring_platform_text,
                "monitoring_platform_annotations": monitoring_platform_annotations}
