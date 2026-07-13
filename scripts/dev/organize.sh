#!/bin/bash
# Organize root directory

mkdir -p docs/project scripts/dev

# Move long-named docs to docs/project/
mv 00_MN3_TAKEOVER_SUMMARY.md docs/project/overview.md 2>/dev/null || true
mv BEST_INTEGRATION_PLAN.md docs/project/integration.md 2>/dev/null || true
mv CODE_AUDIT_REPORT.md docs/project/audit.md 2>/dev/null || true
mv COMPLETION_REPORT.md docs/project/completion.md 2>/dev/null || true
mv DEVELOPMENT_SUMMARY.md docs/project/dev-summary.md 2>/dev/null || true
mv FINAL_SUMMARY.md docs/project/summary.md 2>/dev/null || true
mv HANDOVER_DOCUMENT.md docs/project/handover.md 2>/dev/null || true
mv INTEGRATION_FINAL_REPORT.md docs/project/integ-report.md 2>/dev/null || true
mv INTEGRATION_IMPLEMENTATION.md docs/project/integ-impl.md 2>/dev/null || true
mv INTEGRATION_PLAN.md docs/project/integ-plan.md 2>/dev/null || true
mv INTEGRATION_PROGRESS_REPORT.md docs/project/integ-progress.md 2>/dev/null || true
mv LAN_TEST_GUIDE.md docs/project/lan-guide.md 2>/dev/null || true
mv LAN_TEST_READY.md docs/project/lan-ready.md 2>/dev/null || true
mv MN2MC_COMPARISON_ANALYSIS.md docs/project/comparison.md 2>/dev/null || true
mv MN3_DEVELOPMENT_START.md docs/project/dev-start.md 2>/dev/null || true
mv MN3_HANDOVER_REPORT.md docs/project/handover-report.md 2>/dev/null || true
mv MN3_REFACTOR_COMPLETE.md docs/project/refactor.md 2>/dev/null || true
mv PHASE8_EXECUTION_PLAN.md docs/project/phase8-plan.md 2>/dev/null || true
mv PHASE8_EXECUTION_SUMMARY.md docs/project/phase8-summary.md 2>/dev/null || true
mv PROJECT_STRUCTURE.md docs/project/structure.md 2>/dev/null || true
mv PROGRESS_UPDATE.md docs/project/progress.md 2>/dev/null || true
mv QUICK_REFERENCE.md docs/project/quick-ref.md 2>/dev/null || true
mv TEST_PLAN.md docs/project/test-plan.md 2>/dev/null || true
mv TEST_REPORT.md docs/project/test-report.md 2>/dev/null || true
mv CLEANUP_REPORT.md docs/project/cleanup.md 2>/dev/null || true
mv FINAL_STATUS.md docs/project/status.md 2>/dev/null || true

# Move scripts to scripts/dev/
mv clean_all.sh scripts/dev/ 2>/dev/null || true
mv clean_git.sh scripts/dev/ 2>/dev/null || true
mv clean_repo.py scripts/dev/ 2>/dev/null || true
mv push.sh scripts/dev/ 2>/dev/null || true
mv push.bat scripts/dev/ 2>/dev/null || true

# Move local dev files to scripts/dev/
mv local_miniworld_server.py scripts/dev/ 2>/dev/null || true
mv miniworld_http_server.py scripts/dev/ 2>/dev/null || true
mv miniworld_rpc_server.py scripts/dev/ 2>/dev/null || true

echo "Organization complete"
