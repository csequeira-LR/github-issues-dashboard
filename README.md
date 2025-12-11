# 📊 GitHub Issues Dashboard

An automated, interactive dashboard for tracking your GitHub issues with real-time updates, charts, and filtering capabilities.

## 🌐 Live Dashboard

Once deployed, your dashboard will be available at:
```
https://<your-username>.github.io/github-issues-dashboard
```

## 📊 Features

- ✅ **Real-time Issue Tracking**: Automatically fetches your GitHub issues
- 📈 **Interactive Charts**: Visual representation of issue trends over the last 12 months
- 🔍 **Search & Filter**: Search by title, repository, or labels; filter by status
- 🔗 **Clickable Links**: Direct links to each issue on GitHub
- 🤖 **Auto-Updated**: Dashboard refreshes automatically every 30 minutes
- ⚡ **Manual Trigger**: Can be triggered manually from the Actions tab anytime
- 📱 **Responsive Design**: Works on desktop, tablet, and mobile

## 🔄 Automatic Updates

This dashboard updates automatically using GitHub Actions:

- **Schedule**: Every 30 minutes
- **Manual Trigger**: Click "Run workflow" in the Actions tab
- **Auto-commit**: Changes are automatically committed to the repository

## 📈 What's Tracked

- Total issues (authored by you or assigned to you)
- Open vs Closed issues
- Historical trends (last 12 months)
- Issue details with direct GitHub links
- Labels and repository information

## 🛠️ How It Works

1. **GitHub Actions** runs `generate_dashboard.py` every 30 minutes (or on manual trigger)
2. Script fetches all your issues using GitHub CLI
3. Generates an interactive HTML dashboard with Chart.js
4. Commits the updated `index.html` to the repository
5. **GitHub Pages** serves the latest version at the live URL

## 🚀 Setup Instructions

### 1. Create a New GitHub Repository

```bash
# Navigate to the project directory
cd ~/github-issues-dashboard

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: GitHub Issues Dashboard"
```

### 2. Create Repository on GitHub

1. Go to https://github.com/new
2. Create a new repository named `github-issues-dashboard`
3. **Do NOT** initialize with README (we already have one)
4. Click "Create repository"

### 3. Push to GitHub

```bash
# Add remote origin (replace <your-username> with your GitHub username)
git remote add origin https://github.com/<your-username>/github-issues-dashboard.git

# Push to main branch
git branch -M main
git push -u origin main
```

### 4. Enable GitHub Pages

1. Go to your repository settings: `https://github.com/<your-username>/github-issues-dashboard/settings/pages`
2. Under "Source", select `main` branch
3. Select `/ (root)` folder
4. Click "Save"
5. Your dashboard will be live at: `https://<your-username>.github.io/github-issues-dashboard`

### 5. Configure Permissions

1. Go to `Settings` → `Actions` → `General`
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Click "Save"

## 🎯 Usage

### Automatic Updates

The dashboard automatically updates every 30 minutes. No action required!

### Manual Updates

To trigger an update manually:

1. Go to the "Actions" tab in your repository
2. Click "Update Dashboard" workflow
3. Click "Run workflow" dropdown
4. Click the green "Run workflow" button

### Local Testing

To test the dashboard generation locally:

```bash
# Make sure you're authenticated with GitHub CLI
gh auth login

# Run the script
python3 generate_dashboard.py

# Open index.html in your browser
open index.html  # macOS
# or
xdg-open index.html  # Linux
# or just open it in your browser manually
```

## 📁 Project Structure

```
github-issues-dashboard/
├── .github/
│   └── workflows/
│       └── update-dashboard.yml    # GitHub Actions workflow
├── generate_dashboard.py           # Main script to generate dashboard
├── index.html                      # Generated dashboard (auto-updated)
└── README.md                       # This file
```

## 🔧 Customization

### Change Update Frequency

Edit `.github/workflows/update-dashboard.yml`:

```yaml
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 * * * *'   # Every hour
  # - cron: '0 */6 * * *' # Every 6 hours
  # - cron: '0 0 * * *'   # Once a day at midnight
```

### Modify Dashboard Appearance

Edit `generate_dashboard.py` and customize the HTML template:
- Change colors in the `<style>` section
- Modify layout and structure
- Add additional statistics or charts

### Filter Specific Repositories

Modify the `fetch_issues()` function in `generate_dashboard.py` to filter by repository:

```python
# Example: Only fetch issues from specific org
authored = run_gh_command(
    'gh search issues --author=@me --owner=lightriversoftware --limit 1000 --json ...'
)
```

## 🐛 Troubleshooting

### Dashboard not updating

1. Check the Actions tab for failed workflow runs
2. Verify GitHub Actions has write permissions (see Setup step 5)
3. Check that GitHub Pages is enabled

### No issues showing

1. Verify you have issues authored by or assigned to you
2. Check GitHub CLI authentication in the Actions logs
3. Try running `generate_dashboard.py` locally to debug

### Chart not displaying

- Make sure Chart.js is loading (check browser console)
- Verify the monthly data has entries

## 📝 Notes

- The dashboard tracks all issues where you are the author OR assignee
- Issue data is fetched using GitHub CLI (`gh`)
- The GITHUB_TOKEN used by Actions has access to public repositories by default
- For private repositories, you may need to create a Personal Access Token

## 🤝 Contributing

Feel free to fork this repository and customize it for your needs!

## 📄 License

MIT License - feel free to use and modify as needed.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
