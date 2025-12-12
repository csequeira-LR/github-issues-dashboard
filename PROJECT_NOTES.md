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
✅ **Sortable table columns** - Click any column header to sort (ascending/descending/default)
✅ **Author column** - Shows who created each issue
✅ **Assignee column** - Shows who's assigned to each issue (or "Unassigned")

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

### Table Features & Usage

#### Column Structure
The dashboard displays issues with the following columns:
1. **Number** - Issue number with clickable link
2. **Title** - Issue title with clickable link
3. **Repository** - Repository name (owner/repo format)
4. **Status** - Open or Closed badge
5. **Author** - Username of who created the issue
6. **Assignee** - Username(s) of who's assigned (or "Unassigned")
7. **Labels** - Colored labels from the issue
8. **Created** - Date issue was created (YYYY-MM-DD)
9. **Updated** - Date issue was last updated (YYYY-MM-DD)

#### Sorting Functionality
All column headers are clickable and sortable:

**How to Sort:**
- **First click**: Sort ascending (A→Z, or oldest→newest for dates) - Shows ▲
- **Second click**: Sort descending (Z→A, or newest→oldest for dates) - Shows ▼
- **Third click**: Reset to default order (by created date, newest first) - Shows ▼

**Sorting Behavior:**
- **Number column**: Numeric sorting (properly handles #123 format)
- **Text columns** (Title, Repository, Author, Assignee, Labels): Alphabetical sorting
- **Date columns** (Created, Updated): Chronological sorting
- Each tab (Open, Closed, All) maintains independent sort states
- Visual indicators (▲/▼) show current sort direction

**Tip**: Hover over column headers to see the hover effect indicating they're clickable

#### Data Fetching
Issues are fetched using GitHub CLI with the following criteria:
- All issues where you are the **author** (`--author=@me`)
- All issues where you are **assigned** (`--assignee=@me`)
- Includes author information for both sets
- Deduplicates issues that match both criteria
- Limit: 1000 issues per query

### Customization Reference

#### Stat Card Label Styling
Location: `generate_dashboard.py` line ~230

```css
.stat-card .label {
    font-size: 18px;        /* Changed from 14px - controls text size */
    font-weight: 700;       /* Added - makes text bolder (400-800) */
    color: rgba(255,255,255,0.9);
    text-transform: uppercase;
    letter-spacing: 1px;
}
```

#### Table Sorting Styles
Location: `generate_dashboard.py` lines ~348-356

```css
th.sortable {
    cursor: pointer;
    user-select: none;
    transition: background 0.2s;
}

th.sortable:hover {
    background: #1a2332;
}
```

#### Other Customizable Elements
- **Background color**: Line ~148 - `background: #1a1a2e;`
- **Stat card colors**: Lines ~200-210 (gradients for pink, cyan, green)
- **Chart colors**: Lines ~560-562 (pie chart) and ~609 (bar chart)
- **Title**: Line ~438 - Change "✏️" emoji or text
- **Sortable columns**: Lines ~348-356 (hover effects and cursor styles)

#### Implementation Details

**Author/Assignee Extraction** (Lines 108-116):
- Extracts author from issue data or defaults to username
- Handles multiple assignees with comma-separated list
- Shows "Unassigned" when no assignees

**Sorting JavaScript** (Lines 683-759):
- `sortTable()` function handles all column sorting
- Maintains independent sort states per tab
- Smart sorting: numeric for numbers, date for dates, alphabetical for text
- Three-state cycle: none → ascending → descending → none

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

### Recent Updates

#### December 11, 2025 - Sortable Columns & Author/Assignee Features
- Added sortable functionality to all table columns
- Added Author column to show issue creator
- Added Assignee column to show who's assigned
- Updated data fetching to include author information
- Implemented three-state sorting (ascending/descending/default)
- Added visual indicators (▲/▼) for sort direction
- Added hover effects on column headers
- Independent sort states per tab (Open, Closed, All)

**Commit**: `a94d64f` - "Add sortable columns and Author/Assignee fields to dashboard"

#### December 11, 2025 - GitHub Actions Fixes
- Fixed authentication error by removing redundant `gh auth login` step
- Added `contents: write` permission for workflow to push changes
- Switched from `GITHUB_TOKEN` to `GH_PAT` (Personal Access Token) to fetch correct issues
- Dashboard now correctly shows only user's authored/assigned issues

**Commits**: `1c3b2dc`, `89d8a4e`, `07c0d2f`

### Claude Code Session Recovery
- Use `/rewind` or press `Esc` twice to access conversation checkpoints
- This conversation is automatically saved for 30 days
- Project notes saved in this file for reference

---
Last updated: December 11, 2025 (Sortable columns & Author/Assignee features)
