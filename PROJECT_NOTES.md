# GitHub Issues Dashboard - Project Notes

## Session Dates: December 10-11, 2025

### What We Built
A professional GitHub Issues Dashboard with dark mode theme, auto-updates, and interactive charts.

### Key Files
- `generate_dashboard.py` - Main generator script (fetches issues, generates HTML)
- `.github/workflows/update-dashboard.yml` - GitHub Actions for auto-updates every 30 minutes
- `index.html` - Generated dashboard (auto-created, don't edit directly)
- `README.md` - Full documentation

### Live Dashboard
**URL**: https://csequeira-LR.github.io/github-issues-dashboard

### Repository
**GitHub**: https://github.com/csequeira-LR/github-issues-dashboard

### Features Implemented
✅ Dark mode theme (#1a1a2e background)
✅ Vibrant colored stat cards (pink, cyan, green gradients)
✅ Pie chart for status distribution
✅ Bar chart for monthly issue trends
✅ Tab navigation (Charts, Open Issues, Closed Issues, All Issues)
✅ Auto-updates every 30 minutes via GitHub Actions
✅ Manual trigger capability from Actions tab
✅ Responsive design for all devices

### How to Update Dashboard

#### Manual Local Update
```bash
cd ~/github-issues-dashboard
python3 generate_dashboard.py
```

#### Push Changes to GitHub
```bash
cd ~/github-issues-dashboard
git add .
git commit -m "Your commit message"
git push
```

#### Trigger Manual Refresh (GitHub)
1. Go to repository Actions tab
2. Click "Update Dashboard" workflow
3. Click "Run workflow"
4. Wait 1-2 minutes for GitHub Pages to rebuild

### Customization Reference

#### Stat Card Label Styling (Lines 219-225)
Location: `generate_dashboard.py` line ~220

```css
.stat-card .label {
    font-size: 18px;        /* Changed from 14px - controls text size */
    font-weight: 700;       /* Added - makes text bolder (400-800) */
    color: rgba(255,255,255,0.9);
    text-transform: uppercase;
    letter-spacing: 1px;
}
```

#### Other Customizable Elements
- **Background color**: Line 148 - `background: #1a1a2e;`
- **Stat card colors**: Lines 200-210 (gradients for pink, cyan, green)
- **Chart colors**: Lines 540-542 (pie chart) and 589 (bar chart)
- **Title**: Line 421 - Change "✏️" emoji or text

### Important Notes
- Dashboard fetches ALL issues you authored OR are assigned to
- Uses GitHub CLI (`gh`) to fetch data
- Auto-updates run via GitHub Actions (no local server needed)
- GitHub Pages deployment takes 1-2 minutes to update after push
- **Requires Personal Access Token (PAT)** stored as `GH_PAT` secret in repository

### GitHub Actions Setup & Configuration

#### Required Repository Secret
The workflow requires a Personal Access Token (PAT) to authenticate as your user account:

**Secret Name**: `GH_PAT`
**Location**: Repository Settings → Secrets and variables → Actions

**How to Create PAT**:
1. Go to GitHub Settings: https://github.com/settings/tokens
2. Generate new token (classic)
3. Required scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `read:user` (Read user profile data)
4. Copy token and add as repository secret named `GH_PAT`

**Why PAT is Required**:
- The default `GITHUB_TOKEN` authenticates as `github-actions[bot]`
- Using `@me` with the bot account fetches wrong issues
- Personal token ensures it fetches YOUR authored/assigned issues

#### Workflow Permissions
The workflow has `contents: write` permission to commit and push updated dashboard files.

### Troubleshooting Guide

#### Issue: "gh auth login" Error
**Error Message**: `The value of the GITHUB_TOKEN environment variable is being used for authentication`

**Solution**: Remove the explicit authentication step. GitHub CLI automatically uses `GITHUB_TOKEN` when set as environment variable.

**Fixed in commit**: `1c3b2dc`

#### Issue: Permission Denied (403) on Push
**Error Message**: `remote: Permission to repository denied to github-actions[bot]`

**Solution**: Add `permissions: contents: write` to the workflow job.

**Fixed in commit**: `89d8a4e`

#### Issue: Dashboard Shows Wrong Issues
**Symptom**: Dashboard displays issues you didn't author or aren't assigned to

**Cause**: Using default `GITHUB_TOKEN` authenticates as bot instead of your user

**Solution**: Create Personal Access Token (PAT) and use `GH_PAT` secret instead of `GITHUB_TOKEN`

**Fixed in commit**: `07c0d2f`

### Previous Setup (No Longer Used)
We initially created a local dashboard with Flask server:
- Location: `~/github-issues-dashboard.html` (local file, not in git)
- Server: `~/dashboard-server.py`
- Startup: `~/start-dashboard.sh`

**These are superseded by the GitHub-hosted version and are no longer needed.**

### To Resume This Project Later
1. Navigate to project: `cd ~/github-issues-dashboard`
2. Check status: `git status`
3. View live dashboard: https://csequeira-LR.github.io/github-issues-dashboard
4. Make changes to `generate_dashboard.py`
5. Test locally: `python3 generate_dashboard.py`
6. Push to GitHub when ready

### Claude Code Session Recovery
- Use `/rewind` or press `Esc` twice to access conversation checkpoints
- This conversation is automatically saved for 30 days
- Project notes saved in this file for reference

---
Last updated: December 11, 2025
