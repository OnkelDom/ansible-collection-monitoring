# Plugins

`degit.monitoring.monitoring_platform_annotations` ergänzt betriebssystemspezifische
Prometheus-Annotationen. Die Prometheus-Rolle aktiviert den Filter mit
`prometheus_platform_annotation_overrides` (Standard: leere Liste).

```yaml
prometheus_platform_annotation_overrides:
  - alertname: DiskUsage.*
    annotations:
      action:
        linux: 'df -h "{{ $labels.path }}"'
        windows: 'Get-Volume'
        unknown: 'Betriebssystem und betroffenes Volume prüfen.'
```

`alertname` wird als vollständiger regulärer Ausdruck ausgewertet. Die Auswahl
erfolgt bei der Regelauswertung anhand des Labels `platform` des überwachten
Systems. Ein Override darf `platform: linux` oder `platform: windows` setzen,
wenn die Regel ausschließlich diese Plattform misst. Facts des Monitoringservers
sind dafür ungeeignet. Fehlende oder unbekannte Plattformen erhalten ausschließlich
den neutralen Text. Varianten dürfen selbst Prometheus-Templates enthalten.

Der Filter ändert ausschließlich Annotationen. Rollout: Regeln mit `promtool`
validieren, Plattformvarianten einschließlich fehlender Labels testen, gesicherte
Konfiguration ausrollen und Prometheus neu laden. Rückbau durch Wiederherstellen
der gesicherten Regeldatei und erneutes Laden. Schwellen, Labels und Routing bleiben
unverändert. `monitoring_platform_text` steht für einzelne Textvarianten bereit.
