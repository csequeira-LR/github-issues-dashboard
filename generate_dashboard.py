#!/usr/bin/env python3
"""
GitHub Issues Dashboard Generator
Fetches issues from GitHub and generates an interactive HTML dashboard
"""

import os
import json
import subprocess
from datetime import datetime, timedelta, timezone
from collections import defaultdict

def run_gh_command(command):
    """Run a gh CLI command and return the output"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout) if result.stdout else []
        else:
            print(f"Error running command: {result.stderr}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

def fetch_issues():
    """Fetch all issues authored by or assigned to the user"""
    print("Fetching issues authored by user...")
    authored = run_gh_command(
        'gh search issues --author=@me --limit 1000 --json number,title,state,repository,createdAt,updatedAt,closedAt,url,assignees,labels'
    )

    print("Fetching issues assigned to user...")
    assigned = run_gh_command(
        'gh search issues --assignee=@me --limit 1000 --json number,title,state,repository,createdAt,updatedAt,closedAt,url,assignees,labels,author'
    )

    # Combine and deduplicate
    all_issues = {issue['url']: issue for issue in authored + assigned}
    return list(all_issues.values())

def calculate_statistics(issues):
    """Calculate statistics from issues"""
    total = len(issues)
    open_count = sum(1 for i in issues if i['state'] == 'open')
    closed_count = total - open_count

    # Calculate monthly trends (last 12 months)
    monthly_data = defaultdict(lambda: {'open': 0, 'closed': 0})
    now = datetime.now(timezone.utc)

    for issue in issues:
        created_date = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))
        month_key = created_date.strftime('%Y-%m')

        # Only include last 12 months
        if (now - created_date).days <= 365:
            if issue['state'] == 'open':
                monthly_data[month_key]['open'] += 1
            else:
                monthly_data[month_key]['closed'] += 1

    # Sort by month
    sorted_months = sorted(monthly_data.keys())[-12:]

    return {
        'total': total,
        'open': open_count,
        'closed': closed_count,
        'monthly_data': monthly_data,
        'sorted_months': sorted_months
    }

def generate_html(issues, stats):
    """Generate the HTML dashboard"""

    # Prepare chart data
    months_labels = json.dumps(stats['sorted_months'])
    open_data = json.dumps([stats['monthly_data'][m]['open'] for m in stats['sorted_months']])
    closed_data = json.dumps([stats['monthly_data'][m]['closed'] for m in stats['sorted_months']])

    # Generate issue rows
    issue_rows = ""
    for issue in sorted(issues, key=lambda x: x['createdAt'], reverse=True):
        number = issue['number']
        title = issue['title']
        state = issue['state']
        repo = issue['repository']['nameWithOwner']
        url = issue['url']
        created = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
        updated = datetime.fromisoformat(issue['updatedAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d')

        state_class = 'status-open' if state == 'open' else 'status-closed'
        state_text = 'OPEN' if state == 'open' else 'CLOSED'

        labels_html = ""
        for label in issue.get('labels', []):
            labels_html += f'<span class="label" style="background-color: #{label["color"]};">{label["name"]}</span> '

        issue_rows += f'''
        <tr class="{state_class}" data-state="{state}" data-repo="{repo}" data-title="{title.lower()}">
            <td><a href="{url}" target="_blank">#{number}</a></td>
            <td class="issue-title"><a href="{url}" target="_blank">{title}</a></td>
            <td><span class="repo-badge">{repo}</span></td>
            <td><span class="status-badge status-{state}">{state_text}</span></td>
            <td>{labels_html}</td>
            <td>{created}</td>
            <td>{updated}</td>
        </tr>
        '''

    # Get current timestamp
    last_updated = datetime.now().strftime('%B %d, %Y at %I:%M %p UTC')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Issues Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .header h1 {{
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }}

        .last-updated {{
            color: #666;
            font-size: 14px;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}

        .stat-card h3 {{
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .stat-card .number {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
        }}

        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .chart-container h2 {{
            color: #333;
            margin-bottom: 20px;
            font-size: 24px;
        }}

        .controls {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .search-bar {{
            width: 100%;
            padding: 12px 20px;
            border: 2px solid #e1e4e8;
            border-radius: 8px;
            font-size: 16px;
            margin-bottom: 15px;
        }}

        .search-bar:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .filter-btn:hover {{
            background: #667eea;
            color: white;
        }}

        .filter-btn.active {{
            background: #667eea;
            color: white;
        }}

        .issues-container {{
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #f6f8fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #e1e4e8;
            position: sticky;
            top: 0;
        }}

        td {{
            padding: 12px;
            border-bottom: 1px solid #e1e4e8;
        }}

        tr:hover {{
            background: #f6f8fa;
        }}

        .issue-title {{
            max-width: 400px;
        }}

        .issue-title a {{
            color: #0366d6;
            text-decoration: none;
            font-weight: 500;
        }}

        .issue-title a:hover {{
            text-decoration: underline;
        }}

        .repo-badge {{
            display: inline-block;
            background: #f1f8ff;
            color: #0366d6;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}

        .status-badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .status-open {{
            background: #d1f0d1;
            color: #1a7f37;
        }}

        .status-closed {{
            background: #f0d1d1;
            color: #c93c37;
        }}

        .label {{
            display: inline-block;
            padding: 3px 8px;
            border-radius: 10px;
            font-size: 11px;
            font-weight: 500;
            color: white;
            margin-right: 4px;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 GitHub Issues Dashboard</h1>
            <div class="last-updated">Last updated: {last_updated}</div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>Total Issues</h3>
                <div class="number">{stats['total']}</div>
            </div>
            <div class="stat-card">
                <h3>Open Issues</h3>
                <div class="number">{stats['open']}</div>
            </div>
            <div class="stat-card">
                <h3>Closed Issues</h3>
                <div class="number">{stats['closed']}</div>
            </div>
        </div>

        <div class="chart-container">
            <h2>📈 Issue Trends (Last 12 Months)</h2>
            <canvas id="trendChart"></canvas>
        </div>

        <div class="controls">
            <input type="text"
                   class="search-bar"
                   id="searchInput"
                   placeholder="Search by title, repository, or labels..."
                   onkeyup="filterTable()">

            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterByState('all')">All Issues</button>
                <button class="filter-btn" onclick="filterByState('open')">Open Only</button>
                <button class="filter-btn" onclick="filterByState('closed')">Closed Only</button>
            </div>
        </div>

        <div class="issues-container">
            <table id="issuesTable">
                <thead>
                    <tr>
                        <th>Number</th>
                        <th>Title</th>
                        <th>Repository</th>
                        <th>Status</th>
                        <th>Labels</th>
                        <th>Created</th>
                        <th>Updated</th>
                    </tr>
                </thead>
                <tbody>
                    {issue_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            🤖 Generated with Claude Code | Auto-updates every 30 minutes
        </div>
    </div>

    <script>
        // Initialize trend chart
        const ctx = document.getElementById('trendChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {months_labels},
                datasets: [{{
                    label: 'Open Issues',
                    data: {open_data},
                    borderColor: '#1a7f37',
                    backgroundColor: 'rgba(26, 127, 55, 0.1)',
                    tension: 0.4
                }}, {{
                    label: 'Closed Issues',
                    data: {closed_data},
                    borderColor: '#c93c37',
                    backgroundColor: 'rgba(201, 60, 55, 0.1)',
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'top',
                    }},
                    title: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1
                        }}
                    }}
                }}
            }}
        }});

        // Filter functionality
        let currentFilter = 'all';

        function filterByState(state) {{
            currentFilter = state;

            // Update button states
            document.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});
            event.target.classList.add('active');

            filterTable();
        }}

        function filterTable() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const table = document.getElementById('issuesTable');
            const rows = table.getElementsByTagName('tr');

            for (let i = 1; i < rows.length; i++) {{
                const row = rows[i];
                const state = row.getAttribute('data-state');
                const title = row.getAttribute('data-title');
                const repo = row.getAttribute('data-repo').toLowerCase();
                const text = row.textContent.toLowerCase();

                const matchesFilter = currentFilter === 'all' || state === currentFilter;
                const matchesSearch = !searchTerm || title.includes(searchTerm) || repo.includes(searchTerm) || text.includes(searchTerm);

                row.style.display = matchesFilter && matchesSearch ? '' : 'none';
            }}
        }}
    </script>
</body>
</html>'''

    return html

def main():
    """Main function"""
    print("=" * 60)
    print("GitHub Issues Dashboard Generator")
    print("=" * 60)

    # Fetch issues
    issues = fetch_issues()
    print(f"Fetched {len(issues)} total issues")

    # Calculate statistics
    stats = calculate_statistics(issues)
    print(f"Open: {stats['open']}, Closed: {stats['closed']}")

    # Generate HTML
    html = generate_html(issues, stats)

    # Write to file
    output_file = 'index.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Dashboard generated successfully: {output_file}")
    print("=" * 60)

if __name__ == '__main__':
    main()
