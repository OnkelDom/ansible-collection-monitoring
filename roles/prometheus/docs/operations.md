## Technical operating-system alarm content

LPM rules are currently supplied by the infrastructure repository through
`prometheus_alert_rules_files` and `prometheus_alert_rules_src_dir`. This collection
does not ship its own LPM rule set; the role validates and installs the supplied
files without rewriting their annotations.

For CPU, RAM, disk, network and service alarms, use technical annotations:

- `summary`: resource, host and the observed condition; avoid vague terms such as
  “Speicherdruck”, “IO-Problem” or “Verarbeitung beeinträchtigt”.
- `description`: measured value, unit, aggregation window, threshold and required
  duration. Describe every relevant condition in a combined expression.
- `action`: platform-specific diagnostic commands and the next operational step.
- `impact`: optional; omit generic consequences that add no information.
- `resolved_action`: optional explanation of what the ended alarm proves and
  which service check remains. Consumers must explicitly support this annotation.

Only report a cause established by a metric or a detected error. Missing exporter
metrics do not establish that the monitored application is unavailable. A stale
textfile does not establish a write-permission error.

Include available bytes and total capacity when the measurement provides them.
Keep current measurements separate from historical averages. Optional annotation
queries must handle absent results without template errors. For SQL, use
“SQL-Abfrage” for SELECT queries, “SQL-Datenänderung” for INSERT/UPDATE/DELETE and
“SQL-Ausführung” when the alert covers multiple statement types.

Before deployment, run `promtool check rules`, rule tests covering the rendered
annotations, and notification-template previews. Content-only changes must leave
expressions, thresholds, evaluation durations and routing labels unchanged.

Platform variants are compiled with `prometheus_platform_annotation_overrides`; see
[the filter contract](../../plugins/README.md). Select the monitored platform,
never the Prometheus host OS, and provide a neutral fallback for absent labels.
