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

def generate_git_report(repo, repo_path):
    """
    Generate a comprehensive HTML report for the Git repository
    
    Args:
        repo: GitPython repository object
        repo_path: Path to the repository
        
    Returns:
        str: HTML content for the report
    """
    # Collect repository information
    repo_info = get_repo_info(repo, repo_path)
    branch_info = get_branch_info(repo)
    commit_history = get_commit_history(repo)
    commit_stats = analyze_commit_stats(commit_history)
    file_stats = get_file_stats(repo)
    
    # Generate charts
    commits_over_time_chart = generate_commits_over_time_chart(commit_history)
    author_distribution_chart = generate_author_distribution_chart(commit_history)
    file_types_chart = generate_file_types_chart(file_stats)
    
    # Create a context dictionary for the format string to avoid duplicate keyword arguments
    format_data = {
        'repo_name': os.path.basename(repo_path),
        'repo_path': repo_info['path'],
        'current_branch': repo_info['current_branch'],
        'repo_size': repo_info['size'],
        'commits_over_time_chart': commits_over_time_chart,
        'author_distribution_chart': author_distribution_chart,
        'file_types_chart': file_types_chart,
        'total_commits': commit_stats['total_commits'],
        'total_authors': commit_stats['total_authors'],
        'branch_count': branch_info['count'],
        'tags_count': repo_info['tags_count'],
        'first_commit_date': commit_stats['first_commit_date'],
        'last_commit_date': commit_stats['last_commit_date'],
        'repo_age': commit_stats['repo_age'],
        'most_active_author': commit_stats['most_active_author'],
        'most_active_author_commits': commit_stats['most_active_author_commits']
    }
    
    # Build remotes HTML
    remotes_html = ""
    for name, url in repo_info['remotes'].items():
        remotes_html += f"""
            <tr>
                <th>{name}</th>
                <td>{url}</td>
            </tr>
        """
    
    # Build branches HTML
    branches_html = ""
    for branch in branch_info['branches']:
        current_marker = "✅ " if branch['is_current'] else ""
        css_class = 'branch-current' if branch['is_current'] else ''
        branches_html += f"""
            <tr class="{css_class}">
                <td>{current_marker}{branch['name']}</td>
                <td class="commit-hash">{branch['last_commit_hash']}</td>
                <td>{branch['last_commit_date']}</td>
            </tr>
        """
    
    # Build recent commits HTML
    commits_html = ""
    for commit in commit_history['commits'][:10]:  # Show only 10 most recent commits
        commits_html += f"""
            <tr>
                <td class="commit-hash">{commit['hash'][:7]}</td>
                <td>{commit['author']}</td>
                <td>{commit['date']}</td>
                <td class="commit-message" title="{commit['message']}">{commit['message']}</td>
            </tr>
        """
    
    # Start building HTML content
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Git Repository Analysis: {format_data['repo_name']}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 0;
                background-color: #f8f9fa;
            }}
            
            /* Main layout */
            .container {{
                padding: 0;
                max-width: 100%;
            }}
            
            /* Header */
            .header {{
                background-color: #fff;
                padding: 20px;
                border-bottom: 2px solid #3498db;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                color: #2c3e50;
                font-size: 1.8rem;
                font-weight: 600;
            }}
            
            /* Main content */
            .main-content {{
                padding: 0 20px 20px 20px;
            }}
            
            /* Two column layout */
            .row {{
                display: flex;
                flex-wrap: wrap;
                margin: 0 -10px;
            }}
            .col {{
                flex: 1;
                padding: 0 10px;
                min-width: 300px;
                margin-bottom: 20px;
            }}
            .col-full {{
                flex-basis: 100%;
                padding: 0 10px;
                margin-bottom: 20px;
            }}
            
            /* Cards */
            .card {{
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                padding: 20px;
                height: 100%;
                box-sizing: border-box;
            }}
            
            /* Headings */
            h2 {{
                margin-top: 0;
                color: #2c3e50;
                border-bottom: 1px solid #eee;
                padding-bottom: 10px;
                font-size: 1.4rem;
            }}
            h3 {{
                color: #2c3e50;
                font-size: 1.1rem;
                margin-top: 20px;
                margin-bottom: 10px;
            }}
            
            /* Tables */
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
                font-size: 14px;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #eee;
            }}
            th {{
                background-color: #f8f9fa;
                font-weight: 600;
            }}
            tr:hover {{
                background-color: #f5f5f5;
            }}
            
            /* Stat boxes */
            .stat-grid {{
                display: flex;
                flex-wrap: wrap;
                margin: 0 -5px;
            }}
            .stat-box {{
                flex: 1 0 45%;
                background: #f8f9fa;
                border-radius: 6px;
                padding: 15px;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                transition: transform 0.2s;
                margin: 5px;
                min-width: 120px;
            }}
            .stat-box:hover {{
                transform: translateY(-2px);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
            
            /* Charts */
            .chart-container {{
                width: 100%;
                height: 350px;
                margin: 15px 0;
            }}
            
            /* Scrolling containers */
            .scrollable {{
                max-height: 350px;
                overflow-y: auto;
                border: 1px solid #eee;
                border-radius: 4px;
            }}
            
            /* Utility classes */
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
                max-width: 300px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                display: block;
            }}
            
            /* Responsive adjustments */
            @media (max-width: 768px) {{
                .col {{
                    flex-basis: 100%;
                }}
                .header {{
                    padding: 15px;
                }}
                .header h1 {{
                    font-size: 1.5rem;
                }}
                .chart-container {{
                    height: 300px;
                }}
            }}
        </style>
        <script>
            document.addEventListener('DOMContentLoaded', function() {{
                // Make sure charts render properly
                if (window.Plotly) {{
                    setTimeout(() => {{
                        const plots = document.querySelectorAll('.js-plotly-plot');
                        plots.forEach(plot => {{
                            window.Plotly.Plots.resize(plot);
                        }});
                    }}, 100);
                }}
            }});
            
            window.addEventListener('resize', function() {{
                if (window.Plotly) {{
                    const plots = document.querySelectorAll('.js-plotly-plot');
                    plots.forEach(plot => {{
                        window.Plotly.Plots.resize(plot);
                    }});
                }}
            }});
        </script>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Git Repository Analysis: {format_data['repo_name']}</h1>
            </div>
            
            <div class="main-content">
                <div class="row">
                    <!-- Repository Information -->
                    <div class="col">
                        <div class="card">
                            <h2>Repository Information</h2>
                            <table>
                                <tr>
                                    <th>Repository Path</th>
                                    <td>{format_data['repo_path']}</td>
                                </tr>
                                <tr>
                                    <th>Current Branch</th>
                                    <td>{format_data['current_branch']}</td>
                                </tr>
                                <tr>
                                    <th>Repository Size</th>
                                    <td>{format_data['repo_size']}</td>
                                </tr>
                            </table>
                            
                            <h3>Remote Information</h3>
                            <table>
                                {remotes_html}
                            </table>
                        </div>
                    </div>
                    
                    <!-- Repository Statistics -->
                    <div class="col">
                        <div class="card">
                            <h2>Repository Statistics</h2>
                            <div class="stat-grid">
                                <div class="stat-box">
                                    <div class="stat-value">{format_data['total_commits']}</div>
                                    <div class="stat-label">Total Commits</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-value">{format_data['total_authors']}</div>
                                    <div class="stat-label">Contributors</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-value">{format_data['branch_count']}</div>
                                    <div class="stat-label">Branches</div>
                                </div>
                                <div class="stat-box">
                                    <div class="stat-value">{format_data['tags_count']}</div>
                                    <div class="stat-label">Tags</div>
                                </div>
                            </div>
                            
                            <h3>Activity Summary</h3>
                            <table>
                                <tr>
                                    <th>First Commit</th>
                                    <td>{format_data['first_commit_date']}</td>
                                </tr>
                                <tr>
                                    <th>Last Commit</th>
                                    <td>{format_data['last_commit_date']}</td>
                                </tr>
                                <tr>
                                    <th>Repository Age</th>
                                    <td>{format_data['repo_age']}</td>
                                </tr>
                                <tr>
                                    <th>Most Active Author</th>
                                    <td>{format_data['most_active_author']} ({format_data['most_active_author_commits']} commits)</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Commits Over Time Chart -->
                    <div class="col-full">
                        <div class="card">
                            <h2>Commit Activity Over Time</h2>
                            <div class="chart-container" id="commits-over-time">
                                {format_data['commits_over_time_chart']}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Author Distribution Chart -->
                    <div class="col">
                        <div class="card">
                            <h2>Commits by Author</h2>
                            <div class="chart-container" id="author-distribution">
                                {format_data['author_distribution_chart']}
                            </div>
                        </div>
                    </div>
                    
                    <!-- File Types Chart -->
                    <div class="col">
                        <div class="card">
                            <h2>File Types Distribution</h2>
                            <div class="chart-container" id="file-types">
                                {format_data['file_types_chart']}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Branches -->
                    <div class="col">
                        <div class="card">
                            <h2>Branches ({format_data['branch_count']})</h2>
                            <div class="scrollable">
                                <table>
                                    <tr>
                                        <th>Branch Name</th>
                                        <th>Last Commit</th>
                                        <th>Last Active</th>
                                    </tr>
                                    {branches_html}
                                </table>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Recent Commits -->
                    <div class="col">
                        <div class="card">
                            <h2>Recent Commits</h2>
                            <div class="scrollable">
                                <table>
                                    <tr>
                                        <th>Commit</th>
                                        <th>Author</th>
                                        <th>Date</th>
                                        <th>Message</th>
                                    </tr>
                                    {commits_html}
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
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