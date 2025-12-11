#!/usr/bin/env python3
"""
GitHub Issues Dashboard Generator
Fetches issues from GitHub and generates an interactive HTML dashboard with dark mode
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
    monthly_data = defaultdict(lambda: {'total': 0})
    now = datetime.now(timezone.utc)

    for issue in issues:
        created_date = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00'))
        month_key = created_date.strftime('%Y-%m')

        # Only include last 12 months
        if (now - created_date).days <= 365:
            monthly_data[month_key]['total'] += 1

    # Sort by month and get last 12
    sorted_months = sorted(monthly_data.keys())[-12:]

    return {
        'total': total,
        'open': open_count,
        'closed': closed_count,
        'monthly_data': monthly_data,
        'sorted_months': sorted_months
    }

def generate_html(issues, stats):
    """Generate the HTML dashboard with dark mode"""

    # Get GitHub username
    try:
        result = subprocess.run('gh api user --jq .login', shell=True, capture_output=True, text=True)
        username = result.stdout.strip() if result.returncode == 0 else 'GitHub'
    except:
        username = 'GitHub'

    # Prepare chart data
    months_labels = json.dumps(stats['sorted_months'])
    monthly_counts = json.dumps([stats['monthly_data'][m]['total'] for m in stats['sorted_months']])

    # Generate issue rows for each tab
    def generate_rows(filter_state=None):
        rows = ""
        filtered_issues = issues if filter_state is None else [i for i in issues if i['state'] == filter_state]

        for issue in sorted(filtered_issues, key=lambda x: x['createdAt'], reverse=True):
            number = issue['number']
            title = issue['title']
            state = issue['state']
            repo = issue['repository']['nameWithOwner']
            url = issue['url']
            created = datetime.fromisoformat(issue['createdAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
            updated = datetime.fromisoformat(issue['updatedAt'].replace('Z', '+00:00')).strftime('%Y-%m-%d')

            state_badge_class = 'badge-open' if state == 'open' else 'badge-closed'
            state_text = 'OPEN' if state == 'open' else 'CLOSED'

            labels_html = ""
            for label in issue.get('labels', []):
                labels_html += f'<span class="label" style="background-color: #{label["color"]};">{label["name"]}</span> '

            rows += f'''
            <tr>
                <td><a href="{url}" target="_blank" class="issue-link">#{number}</a></td>
                <td class="issue-title"><a href="{url}" target="_blank" class="issue-link">{title}</a></td>
                <td><span class="repo-badge">{repo}</span></td>
                <td><span class="status-badge {state_badge_class}">{state_text}</span></td>
                <td>{labels_html}</td>
                <td>{created}</td>
                <td>{updated}</td>
            </tr>
            '''
        return rows

    all_issues_rows = generate_rows()
    open_issues_rows = generate_rows('open')
    closed_issues_rows = generate_rows('closed')

    # Get current timestamp
    last_updated = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S EST')

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{username}'s GitHub Issues Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #1a1a2e;
            color: #e0e0e0;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .header h1 {{
            color: #ffffff;
            font-size: 36px;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            color: #a0a0a0;
            font-size: 16px;
            margin-bottom: 5px;
        }}

        .header .last-updated {{
            color: #808080;
            font-size: 14px;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .stat-card {{
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: transform 0.2s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
        }}

        .stat-card.total {{
            background: linear-gradient(135deg, #ff6b9d 0%, #c44569 100%);
        }}

        .stat-card.open {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}

        .stat-card.closed {{
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }}

        .stat-card .number {{
            font-size: 48px;
            font-weight: bold;
            color: white;
            margin-bottom: 10px;
        }}

        .stat-card .label {{
            font-size: 18px;
            font-weight: 700;
            color: rgba(255,255,255,0.9);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        .nav-buttons {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}

        .nav-btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            color: white;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }}

        .nav-btn.charts {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}

        .nav-btn.open-tab {{
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }}

        .nav-btn.closed-tab {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        .nav-btn.all-tab {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }}

        .nav-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.4);
        }}

        .nav-btn.active {{
            box-shadow: 0 4px 12px rgba(255,255,255,0.3);
        }}

        .content-section {{
            display: none;
        }}

        .content-section.active {{
            display: block;
        }}

        .charts-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .chart-container {{
            background: #16213e;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }}

        .chart-container h2 {{
            color: #ffffff;
            margin-bottom: 10px;
            font-size: 20px;
        }}

        .chart-container .subtitle {{
            color: #a0a0a0;
            font-size: 14px;
            margin-bottom: 20px;
        }}

        .issues-container {{
            background: #16213e;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th {{
            background: #0f1626;
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #ffffff;
            border-bottom: 2px solid #4a5568;
            position: sticky;
            top: 0;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #2d3748;
            color: #e0e0e0;
        }}

        tr:hover {{
            background: rgba(255,255,255,0.05);
        }}

        .issue-title {{
            max-width: 400px;
        }}

        .issue-link {{
            color: #4facfe;
            text-decoration: none;
            font-weight: 500;
        }}

        .issue-link:hover {{
            text-decoration: underline;
            color: #00f2fe;
        }}

        .repo-badge {{
            display: inline-block;
            background: rgba(79, 172, 254, 0.2);
            color: #4facfe;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }}

        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}

        .badge-open {{
            background: rgba(67, 233, 123, 0.2);
            color: #43e97b;
        }}

        .badge-closed {{
            background: rgba(201, 60, 55, 0.2);
            color: #ff6b6b;
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
            color: #808080;
            margin-top: 30px;
            font-size: 14px;
        }}

        .empty-state {{
            text-align: center;
            padding: 60px 20px;
            color: #a0a0a0;
        }}

        .empty-state h3 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✏️ {username}'s Issues Dashboard</h1>
            <div class="subtitle">GitHub Issues - Automated Tracking</div>
            <div class="last-updated">Last updated: {last_updated}</div>
        </div>

        <div class="stats">
            <div class="stat-card total">
                <div class="number">{stats['total']}</div>
                <div class="label">Total Issues</div>
            </div>
            <div class="stat-card open">
                <div class="number">{stats['open']}</div>
                <div class="label">Open Issues</div>
            </div>
            <div class="stat-card closed">
                <div class="number">{stats['closed']}</div>
                <div class="label">Closed Issues</div>
            </div>
        </div>

        <div class="nav-buttons">
            <button class="nav-btn charts active" onclick="showTab('charts')">Charts</button>
            <button class="nav-btn open-tab" onclick="showTab('open')">Open Issues</button>
            <button class="nav-btn closed-tab" onclick="showTab('closed')">Closed Issues</button>
            <button class="nav-btn all-tab" onclick="showTab('all')">All Issues</button>
        </div>

        <div id="charts-section" class="content-section active">
            <div class="charts-grid">
                <div class="chart-container">
                    <h2>Issues by Status</h2>
                    <div class="subtitle">Distribution (Click to view)</div>
                    <canvas id="statusChart"></canvas>
                </div>
                <div class="chart-container">
                    <h2>Issues Over Time (Last 12 Months)</h2>
                    <div class="subtitle">Created Per Month (Click to view)</div>
                    <canvas id="trendChart"></canvas>
                </div>
            </div>
        </div>

        <div id="open-section" class="content-section">
            <div class="issues-container">
                <table>
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
                        {open_issues_rows if open_issues_rows else '<tr><td colspan="7" class="empty-state"><h3>No open issues</h3></td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="closed-section" class="content-section">
            <div class="issues-container">
                <table>
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
                        {closed_issues_rows if closed_issues_rows else '<tr><td colspan="7" class="empty-state"><h3>No closed issues</h3></td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div id="all-section" class="content-section">
            <div class="issues-container">
                <table>
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
                        {all_issues_rows if all_issues_rows else '<tr><td colspan="7" class="empty-state"><h3>No issues</h3></td></tr>'}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="footer">
            🤖 Generated with Claude Code | Auto-updates every 30 minutes
        </div>
    </div>

    <script>
        // Pie Chart for Status Distribution
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {{
            type: 'pie',
            data: {{
                labels: ['Open', 'Closed'],
                datasets: [{{
                    data: [{stats['open']}, {stats['closed']}],
                    backgroundColor: [
                        'rgba(79, 172, 254, 0.8)',
                        'rgba(118, 75, 162, 0.8)'
                    ],
                    borderColor: [
                        'rgba(79, 172, 254, 1)',
                        'rgba(118, 75, 162, 1)'
                    ],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            color: '#e0e0e0',
                            padding: 15,
                            font: {{
                                size: 12
                            }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = {stats['total']};
                                const percentage = ((value / total) * 100).toFixed(1);
                                return label + ': ' + value + ' (' + percentage + '%)';
                            }}
                        }}
                    }}
                }}
            }}
        }});

        // Bar Chart for Monthly Trends
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        new Chart(trendCtx, {{
            type: 'bar',
            data: {{
                labels: {months_labels},
                datasets: [{{
                    label: 'Issues Created',
                    data: {monthly_counts},
                    backgroundColor: 'rgba(79, 172, 254, 0.7)',
                    borderColor: 'rgba(79, 172, 254, 1)',
                    borderWidth: 2,
                    borderRadius: 5
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            stepSize: 1,
                            color: '#a0a0a0'
                        }},
                        grid: {{
                            color: 'rgba(255,255,255,0.1)'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            color: '#a0a0a0'
                        }},
                        grid: {{
                            color: 'rgba(255,255,255,0.1)'
                        }}
                    }}
                }}
            }}
        }});

        // Tab Navigation
        function showTab(tab) {{
            // Hide all sections
            document.querySelectorAll('.content-section').forEach(section => {{
                section.classList.remove('active');
            }});

            // Remove active class from all buttons
            document.querySelectorAll('.nav-btn').forEach(btn => {{
                btn.classList.remove('active');
            }});

            // Show selected section and activate button
            if (tab === 'charts') {{
                document.getElementById('charts-section').classList.add('active');
                document.querySelector('.nav-btn.charts').classList.add('active');
            }} else if (tab === 'open') {{
                document.getElementById('open-section').classList.add('active');
                document.querySelector('.nav-btn.open-tab').classList.add('active');
            }} else if (tab === 'closed') {{
                document.getElementById('closed-section').classList.add('active');
                document.querySelector('.nav-btn.closed-tab').classList.add('active');
            }} else if (tab === 'all') {{
                document.getElementById('all-section').classList.add('active');
                document.querySelector('.nav-btn.all-tab').classList.add('active');
            }}
        }}
    </script>
</body>
</html>'''

    return html

def main():
    """Main function"""
    print("=" * 60)
    print("GitHub Issues Dashboard Generator (Dark Mode)")
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
