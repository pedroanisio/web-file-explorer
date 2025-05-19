"""
Git Repository Analyzer Plugin
Provides comprehensive Git repository analysis with beautiful visualizations
"""
import os
import subprocess
import tempfile
import json
import datetime
import logging
import sys
from pathlib import Path
import traceback

# Setup logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("git_repo_analyzer")

# Import dependencies with fallback for when dependencies aren't installed yet
try:
    logger.debug("Attempting to import plugin dependencies")
    import git
    logger.debug("Successfully imported gitpython")
    import pandas as pd
    logger.debug("Successfully imported pandas")
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    logger.debug("Successfully imported plotly")
    from tabulate import tabulate
    logger.debug("Successfully imported tabulate")
    DEPS_INSTALLED = True
    logger.info("All dependencies successfully imported")
except ImportError as e:
    logger.error(f"Failed to import dependency: {e}")
    missing_package = str(e).split("'")[1] if "'" in str(e) else str(e)
    logger.error(f"Missing package: {missing_package}")
    logger.debug(f"Python path: {sys.path}")
    DEPS_INSTALLED = False

def execute(path, **kwargs):
    """
    Execute the Git repository analysis
    
    Args:
        path (str): Absolute path to the current directory in file explorer
        
    Returns:
        dict: Analysis results with HTML content
    """
    logger.debug(f"Execute called with path: {path}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    logger.debug(f"Python executable: {sys.executable}")
    logger.debug(f"Python version: {sys.version}")
    
    # Check if dependencies are installed
    if not DEPS_INSTALLED:
        logger.error("Dependencies not installed, cannot proceed")
        missing_deps = []
        for dep in ["git", "pandas", "plotly", "tabulate"]:
            try:
                __import__(dep)
                logger.debug(f"Dependency {dep} is available")
            except ImportError:
                logger.error(f"Dependency {dep} is missing")
                missing_deps.append(dep)
        
        return {
            "success": False,
            "error": f"Required dependencies not installed: {', '.join(missing_deps)}. Please restart the application to auto-install dependencies."
        }
    
    try:
        # Check if the path is a git repository
        git_dir = os.path.join(path, '.git')
        logger.debug(f"Checking if {git_dir} exists")
        if not os.path.exists(git_dir):
            logger.warning(f"Path {path} is not a Git repository (no .git directory)")
            return {
                "success": False,
                "error": f"The directory {path} is not a Git repository."
            }
        
        # Initialize repository object
        logger.debug(f"Initializing Git repository at {path}")
        repo = git.Repo(path)
        logger.debug(f"Git repository initialized: {repo}")
        
        # Generate the report
        logger.info(f"Generating Git report for repository at {path}")
        html_content = generate_git_report(repo, path)
        logger.debug(f"Generated HTML report ({len(html_content)} characters)")
        
        return {
            "success": True,
            "output": html_content,
            "title": "Git Repository Analysis",
            "content_type": "html"  # Indicate that output contains HTML
        }
        
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"Error analyzing Git repository: {e}")
        logger.debug(f"Error details: {error_details}")
        return {
            "success": False,
            "error": f"Error analyzing Git repository: {str(e)}\n\n{error_details}"
        }

def generate_git_report(repo, path):
    """
    Generate a comprehensive HTML report for the Git repository
    
    Args:
        repo: GitPython repository object
        path: Path to the repository
        
    Returns:
        str: HTML content for the report
    """
    # Collect repository information
    repo_info = get_repo_info(repo, path)
    branch_info = get_branch_info(repo)
    commit_history = get_commit_history(repo)
    commit_stats = analyze_commit_stats(commit_history)
    file_stats = get_file_stats(repo)
    
    # Generate charts
    commits_over_time_chart = generate_commits_over_time_chart(commit_history)
    author_distribution_chart = generate_author_distribution_chart(commit_history)
    file_types_chart = generate_file_types_chart(file_stats)
    
    # Start building HTML content
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Git Repository Analysis</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            .dashboard {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }}
            @media (max-width: 768px) {{
                .dashboard {{
                    grid-template-columns: 1fr;
                }}
            }}
            .card {{
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                padding: 20px;
                margin-bottom: 20px;
            }}
            .full-width {{
                grid-column: 1 / -1;
            }}
            h1, h2, h3 {{
                color: #2c3e50;
            }}
            h1 {{
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                margin-top: 0;
                border-bottom: 1px solid #ddd;
                padding-bottom: 8px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: 600;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            .stat-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 15px 0;
            }}
            .stat-box {{
                background: #f8f9fa;
                border-radius: 6px;
                padding: 15px;
                text-align: center;
            }}
            .stat-value {{
                font-size: 24px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }}
            .stat-label {{
                font-size: 14px;
                color: #7f8c8d;
            }}
            .chart-container {{
                width: 100%;
                height: 350px;
                margin: 15px 0;
            }}
            .branch-list, .commit-list {{
                max-height: 400px;
                overflow-y: auto;
            }}
            .branch-current {{
                font-weight: bold;
                color: #27ae60;
            }}
            .commit-hash {{
                font-family: monospace;
                color: #e74c3c;
            }}
            .commit-message {{
                font-style: italic;
            }}
        </style>
    </head>
    <body>
        <h1>Git Repository Analysis: {os.path.basename(path)}</h1>
        
        <div class="dashboard">
            <!-- Repository Information -->
            <div class="card">
                <h2>Repository Information</h2>
                <table>
                    <tr>
                        <th>Repository Path</th>
                        <td>{repo_info['path']}</td>
                    </tr>
                    <tr>
                        <th>Current Branch</th>
                        <td>{repo_info['current_branch']}</td>
                    </tr>
                    <tr>
                        <th>Repository Size</th>
                        <td>{repo_info['size']}</td>
                    </tr>
                </table>
                
                <h3>Remote Information</h3>
                <table>
    """
    
    # Add remote information
    for name, url in repo_info['remotes'].items():
        html += f"""
                    <tr>
                        <th>{name}</th>
                        <td>{url}</td>
                    </tr>
        """
    
    html += """
                </table>
            </div>
            
            <!-- Repository Statistics -->
            <div class="card">
                <h2>Repository Statistics</h2>
                <div class="stat-grid">
                    <div class="stat-box">
                        <div class="stat-value">{commit_stats['total_commits']}</div>
                        <div class="stat-label">Total Commits</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{commit_stats['total_authors']}</div>
                        <div class="stat-label">Contributors</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{branch_info['count']}</div>
                        <div class="stat-label">Branches</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-value">{repo_info['tags_count']}</div>
                        <div class="stat-label">Tags</div>
                    </div>
                </div>
                
                <h3>Activity Summary</h3>
                <table>
                    <tr>
                        <th>First Commit</th>
                        <td>{commit_stats['first_commit_date']}</td>
                    </tr>
                    <tr>
                        <th>Last Commit</th>
                        <td>{commit_stats['last_commit_date']}</td>
                    </tr>
                    <tr>
                        <th>Repository Age</th>
                        <td>{commit_stats['repo_age']}</td>
                    </tr>
                    <tr>
                        <th>Most Active Author</th>
                        <td>{commit_stats['most_active_author']} ({commit_stats['most_active_author_commits']} commits)</td>
                    </tr>
                </table>
            </div>
            
            <!-- Branches -->
            <div class="card">
                <h2>Branches ({branch_info['count']})</h2>
                <div class="branch-list">
                    <table>
                        <tr>
                            <th>Branch Name</th>
                            <th>Last Commit</th>
                            <th>Last Active</th>
                        </tr>
    """.format(**locals(), **commit_stats, **repo_info)
    
    # Add branch information
    for branch in branch_info['branches']:
        current_marker = "✅ " if branch['is_current'] else ""
        css_class = 'branch-current' if branch['is_current'] else ''
        html += f"""
                        <tr class="{css_class}">
                            <td>{current_marker}{branch['name']}</td>
                            <td class="commit-hash">{branch['last_commit_hash']}</td>
                            <td>{branch['last_commit_date']}</td>
                        </tr>
        """
    
    html += """
                    </table>
                </div>
            </div>
            
            <!-- Recent Commits -->
            <div class="card">
                <h2>Recent Commits</h2>
                <div class="commit-list">
                    <table>
                        <tr>
                            <th>Commit</th>
                            <th>Author</th>
                            <th>Date</th>
                            <th>Message</th>
                        </tr>
    """
    
    # Add recent commits
    for commit in commit_history['commits'][:10]:  # Show only 10 most recent commits
        html += f"""
                        <tr>
                            <td class="commit-hash">{commit['hash'][:7]}</td>
                            <td>{commit['author']}</td>
                            <td>{commit['date']}</td>
                            <td class="commit-message">{commit['message']}</td>
                        </tr>
        """
    
    html += """
                    </table>
                </div>
            </div>
            
            <!-- Commits Over Time Chart -->
            <div class="card full-width">
                <h2>Commit Activity Over Time</h2>
                <div class="chart-container" id="commits-over-time">
                    {commits_over_time_chart}
                </div>
            </div>
            
            <!-- Author Distribution Chart -->
            <div class="card">
                <h2>Commits by Author</h2>
                <div class="chart-container" id="author-distribution">
                    {author_distribution_chart}
                </div>
            </div>
            
            <!-- File Types Chart -->
            <div class="card">
                <h2>File Types Distribution</h2>
                <div class="chart-container" id="file-types">
                    {file_types_chart}
                </div>
            </div>
        </div>
    </body>
    </html>
    """.format(commits_over_time_chart=commits_over_time_chart,
               author_distribution_chart=author_distribution_chart,
               file_types_chart=file_types_chart)
    
    return html

def get_repo_info(repo, path):
    """Get basic repository information"""
    # Get current branch
    try:
        current_branch = repo.active_branch.name
    except:
        current_branch = "(detached HEAD)"
    
    # Get remotes
    remotes = {remote.name: remote.url for remote in repo.remotes}
    
    # Get repository size
    size_bytes = get_repo_size(path)
    if size_bytes < 1024:
        size = f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        size = f"{size_bytes/1024:.1f} KB"
    else:
        size = f"{size_bytes/(1024*1024):.1f} MB"
    
    # Get tags count
    tags_count = len(list(repo.tags))
    
    return {
        "path": path,
        "current_branch": current_branch,
        "remotes": remotes,
        "size": size,
        "tags_count": tags_count
    }

def get_branch_info(repo):
    """Get information about all branches"""
    branches = []
    current_branch_name = ""
    try:
        current_branch_name = repo.active_branch.name
    except:
        current_branch_name = "(detached HEAD)"
    
    for branch in repo.branches:
        # Get last commit on branch
        last_commit = list(repo.iter_commits(branch.name, max_count=1))[0]
        commit_date = datetime.datetime.fromtimestamp(last_commit.committed_date)
        
        branches.append({
            "name": branch.name,
            "is_current": branch.name == current_branch_name,
            "last_commit_hash": last_commit.hexsha[:7],
            "last_commit_date": commit_date.strftime("%Y-%m-%d %H:%M")
        })
    
    # Sort branches: current branch first, then alphabetically
    branches.sort(key=lambda x: (not x['is_current'], x['name']))
    
    return {
        "count": len(branches),
        "branches": branches
    }

def get_commit_history(repo):
    """Get commit history from the repository"""
    commits = []
    for commit in repo.iter_commits():
        commit_date = datetime.datetime.fromtimestamp(commit.committed_date)
        commits.append({
            "hash": commit.hexsha,
            "author": commit.author.name,
            "author_email": commit.author.email,
            "date": commit_date.strftime("%Y-%m-%d %H:%M"),
            "timestamp": commit.committed_date,
            "message": commit.message.strip().split('\n')[0],  # Only first line of commit message
            "stats": commit.stats.total
        })
    
    return {
        "commits": commits
    }

def analyze_commit_stats(commit_history):
    """Analyze commit statistics"""
    commits = commit_history['commits']
    
    if not commits:
        return {
            "total_commits": 0,
            "total_authors": 0,
            "first_commit_date": "N/A",
            "last_commit_date": "N/A",
            "repo_age": "N/A",
            "most_active_author": "N/A",
            "most_active_author_commits": 0
        }
    
    # Count commits by author
    authors = {}
    for commit in commits:
        author = commit['author']
        authors[author] = authors.get(author, 0) + 1
    
    # Find most active author
    most_active_author = max(authors.items(), key=lambda x: x[1]) if authors else ("None", 0)
    
    # Get first and last commit dates
    first_commit = commits[-1]
    last_commit = commits[0]
    
    first_date = datetime.datetime.fromtimestamp(first_commit['timestamp'])
    last_date = datetime.datetime.fromtimestamp(last_commit['timestamp'])
    
    # Calculate repository age
    repo_age_days = (last_date - first_date).days
    if repo_age_days < 1:
        repo_age = "Less than a day"
    elif repo_age_days < 30:
        repo_age = f"{repo_age_days} days"
    elif repo_age_days < 365:
        repo_age = f"{repo_age_days // 30} months, {repo_age_days % 30} days"
    else:
        years = repo_age_days // 365
        remaining_days = repo_age_days % 365
        months = remaining_days // 30
        repo_age = f"{years} years, {months} months"
    
    return {
        "total_commits": len(commits),
        "total_authors": len(authors),
        "first_commit_date": first_commit['date'],
        "last_commit_date": last_commit['date'],
        "repo_age": repo_age,
        "most_active_author": most_active_author[0],
        "most_active_author_commits": most_active_author[1]
    }

def get_file_stats(repo):
    """Get statistics about files in the repository"""
    try:
        # Get all files in the repository
        items = subprocess.check_output(['git', 'ls-files'], cwd=repo.working_dir)
        files = items.decode('utf-8').strip().split('\n')
        
        # Count files by extension
        extensions = {}
        for file in files:
            if file:  # Skip empty lines
                ext = os.path.splitext(file)[1]
                if not ext:
                    ext = '(no extension)'
                else:
                    # Remove leading dot from extension
                    ext = ext[1:]
                extensions[ext] = extensions.get(ext, 0) + 1
        
        # Convert to list of dictionaries for easier processing
        ext_data = [{"extension": ext, "count": count} for ext, count in extensions.items()]
        
        # Sort by count (descending)
        ext_data.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            "total_files": len(files),
            "extensions": ext_data
        }
    except Exception as e:
        return {
            "total_files": 0,
            "extensions": [],
            "error": str(e)
        }

def get_repo_size(path):
    """Calculate the size of the Git repository (excluding .git directory)"""
    try:
        # Use git to list all files and their sizes
        output = subprocess.check_output(
            ['git', 'ls-files', '-z'], 
            cwd=path
        )
        files = output.decode('utf-8').split('\0')
        
        total_size = 0
        for file in files:
            if file:  # Skip empty entries
                file_path = os.path.join(path, file)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
        
        return total_size
    except Exception as e:
        return 0

def generate_commits_over_time_chart(commit_history):
    """Generate a chart showing commits over time"""
    commits = commit_history['commits']
    
    if not commits:
        return "<p>No commit data available</p>"
    
    # Prepare data
    dates = [datetime.datetime.fromtimestamp(commit['timestamp']) for commit in commits]
    dates.reverse()  # Oldest first
    
    # Count commits by day
    date_counts = {}
    for date in dates:
        day_str = date.strftime("%Y-%m-%d")
        date_counts[day_str] = date_counts.get(day_str, 0) + 1
    
    # Convert to pandas DataFrame
    df = pd.DataFrame({
        'date': list(date_counts.keys()),
        'commits': list(date_counts.values())
    })
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Create figure
    fig = px.line(df, x='date', y='commits', 
                  title='Commit Activity Over Time',
                  labels={'date': 'Date', 'commits': 'Number of Commits'},
                  template='plotly_white')
    
    # Add area below line
    fig.add_traces(
        px.area(df, x='date', y='commits', color_discrete_sequence=['rgba(0, 123, 255, 0.2)']).data[0]
    )
    
    # Customize layout
    fig.update_layout(
        showlegend=False,
        hovermode='x unified',
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis=dict(
            tickformat='%b %Y',
            tickangle=-45,
            tickmode='auto',
            nticks=10
        )
    )
    
    # Convert to HTML
    return fig.to_html(include_plotlyjs='cdn', full_html=False, config={'responsive': True})

def generate_author_distribution_chart(commit_history):
    """Generate a chart showing commit distribution by author"""
    commits = commit_history['commits']
    
    if not commits:
        return "<p>No commit data available</p>"
    
    # Count commits by author
    authors = {}
    for commit in commits:
        author = commit['author']
        authors[author] = authors.get(author, 0) + 1
    
    # Convert to pandas DataFrame
    df = pd.DataFrame({
        'author': list(authors.keys()),
        'commits': list(authors.values())
    })
    df = df.sort_values('commits', ascending=False)
    
    # Limit to top 10 authors
    if len(df) > 10:
        others_commits = df.iloc[10:]['commits'].sum()
        df = df.iloc[:10]
        df = pd.concat([df, pd.DataFrame({'author': ['Others'], 'commits': [others_commits]})])
    
    # Create pie chart
    fig = px.pie(df, values='commits', names='author',
                 title='Commits by Author',
                 template='plotly_white')
    
    # Customize layout
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10)
    )
    
    # Convert to HTML
    return fig.to_html(include_plotlyjs='cdn', full_html=False, config={'responsive': True})

def generate_file_types_chart(file_stats):
    """Generate a chart showing distribution of file types"""
    extensions = file_stats.get('extensions', [])
    
    if not extensions:
        return "<p>No file data available</p>"
    
    # Prepare data
    df = pd.DataFrame(extensions)
    
    # Limit to top 10 extensions
    if len(df) > 10:
        others_count = df.iloc[10:]['count'].sum()
        df = df.iloc[:10]
        df = pd.concat([df, pd.DataFrame({'extension': ['Others'], 'count': [others_count]})])
    
    # Create horizontal bar chart
    fig = px.bar(df, x='count', y='extension', orientation='h',
                title='File Types Distribution',
                labels={'count': 'Number of Files', 'extension': 'File Extension'},
                template='plotly_white',
                color='count',
                color_continuous_scale='viridis')
    
    # Customize layout
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        yaxis=dict(categoryorder='total ascending')
    )
    
    # Convert to HTML
    return fig.to_html(include_plotlyjs='cdn', full_html=False, config={'responsive': True}) 