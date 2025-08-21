-- SQLite
SELECT id, title, status, service_name, created_at, resolved_at, acknowledged_at, is_escalated, updated_at, resolved_by_ccoe, caused_by_infra
FROM incidents
where service_id = 'PJFLEB2'
AND created_at >= datetime('now', '-2 days')
ORDER BY created_at DESC;
