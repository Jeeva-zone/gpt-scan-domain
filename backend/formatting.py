from __future__ import annotations

import csv
import io


def dedupe_and_limit(results: list[dict[str, str | bool]], max_results: int) -> list[dict[str, str | bool]]:
    seen: set[tuple[str, str]] = set()
    output: list[dict[str, str | bool]] = []
    for item in sorted(results, key=lambda x: (str(x['hostname']), str(x['ip']))):
        key = (str(item['hostname']), str(item['ip']))
        if key in seen:
            continue
        seen.add(key)
        output.append({'hostname': key[0], 'ip': key[1], 'cloudflare': True})
        if len(output) >= max_results:
            break
    return output


def results_to_csv(results: list[dict[str, str | bool]]) -> str:
    stream = io.StringIO(newline='')
    writer = csv.writer(stream, lineterminator='\n')
    writer.writerow(['hostname', 'ip', 'cloudflare'])
    for result in results:
        writer.writerow([result['hostname'], result['ip'], 'true'])
    return stream.getvalue()
