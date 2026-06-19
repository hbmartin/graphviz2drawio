---
name: sonarqube-analysis
description: Inspect SonarQube Cloud/SonarCloud findings for this repository using local .env credentials. Use when the user asks to inspect, summarize, triage, prioritize, or fix SonarQube/SonarCloud issues, quality gate results, security hotspots, vulnerabilities, bugs, code smells, or new-code findings.
---

# SonarQube Analysis

## Workflow

1. Load Sonar settings from the repo `.env` without printing secrets.
   This checkout is expected to use SonarCloud project
   `hbmartin_create-ts-lib` on branch `main`.
2. Prefer the bundled script:

   ```bash
   python3 .agents/skills/sonarqube-analysis/scripts/sonar_report.py --format markdown
   ```

3. If the user asks for a focused slice, pass one or more flags:

   ```bash
   python3 .agents/skills/sonarqube-analysis/scripts/sonar_report.py --bugs --security
   python3 .agents/skills/sonarqube-analysis/scripts/sonar_report.py --new-code
   python3 .agents/skills/sonarqube-analysis/scripts/sonar_report.py --branch main --top 20
   python3 .agents/skills/sonarqube-analysis/scripts/sonar_report.py --project hbmartin_create-ts-lib
   ```

4. Summarize findings in this order:
   - quality gate and latest analysis date
   - vulnerabilities, bugs, blockers, and security hotspots
   - new-code findings
   - largest maintainability clusters by rule/file
   - likely false positives/report hygiene

5. For fix work, inspect the local source before editing. Separate likely real defects from generated-code noise and false positives.

## Safety

- Never print `SONAR_TOKEN` or raw `.env` contents.
- Ask before making live Sonar changes such as marking false positives, accepting issues, or changing project settings.
- Treat `sonar.exclusions` as a multi-value setting when using the Sonar API.
- Use local file references in final answers when a finding maps to this checkout.

## Expected `.env`

The script expects these keys:

```bash
SONAR_HOST_URL=https://sonarcloud.io
SONAR_ORG=hbmartin
SONAR_PROJECT_KEY=hbmartin_create-ts-lib
SONAR_BRANCH=main
SONAR_TOKEN=...
```
