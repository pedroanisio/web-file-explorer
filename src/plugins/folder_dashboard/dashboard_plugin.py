"""
Folder Dashboard Plugin - V2 Sample Plugin
Demonstrates page mode with comprehensive folder analysis and interactive charts.
"""
import os
import datetime
import json
from collections import defaultdict, Counter
from pathlib import Path

def execute(path, **kwargs):
    """
    Execute the folder dashboard analysis.
    
    Args:
        path (str): The folder path to analyze
        
    Returns:
        dict: Dashboard data with HTML output
    """
    try:
        # Analyze the folder
        analysis = analyze_folder(path)
        
        # Generate the dashboard HTML
        dashboard_html = generate_dashboard_html(analysis, path)
        
        return {
            "success": True,
            "output": dashboard_html,
            "title": f"Folder Dashboard - {os.path.basename(path) or 'Root'}",
            "is_html": True,
            "content_type": "html"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Dashboard analysis failed: {str(e)}"
        }

def analyze_folder(path):
    """Analyze folder contents and generate statistics"""
    analysis = {
        "path": path,
        "folder_name": os.path.basename(path) or "Root",
        "total_files": 0,
        "total_dirs": 0,
        "total_size": 0,
        "file_types": Counter(),
        "size_distribution": [],
        "largest_files": [],
        "recent_files": [],
        "oldest_files": [],
        "hidden_files": 0,
        "empty_files": 0,
        "analysis_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    if not os.path.exists(path) or not os.path.isdir(path):
        return analysis
    
    files_info = []
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            
            try:
                stat_info = os.stat(item_path)
                
                if os.path.isfile(item_path):
                    analysis["total_files"] += 1
                    file_size = stat_info.st_size
                    analysis["total_size"] += file_size
                    
                    # File extension analysis
                    ext = Path(item).suffix.lower() or 'no_extension'
                    analysis["file_types"][ext] += 1
                    
                    # Track file info for further analysis
                    file_info = {
                        "name": item,
                        "size": file_size,
                        "modified": stat_info.st_mtime,
                        "created": stat_info.st_ctime,
                        "is_hidden": item.startswith('.'),
                        "extension": ext
                    }
                    files_info.append(file_info)
                    
                    # Count special file types
                    if item.startswith('.'):
                        analysis["hidden_files"] += 1
                    if file_size == 0:
                        analysis["empty_files"] += 1
                        
                elif os.path.isdir(item_path):
                    analysis["total_dirs"] += 1
                    
            except (OSError, PermissionError):
                # Skip files we can't access
                continue
    
    except PermissionError:
        return analysis
    
    # Process file statistics
    if files_info:
        # Sort by size for largest files
        files_by_size = sorted(files_info, key=lambda x: x["size"], reverse=True)
        analysis["largest_files"] = files_by_size[:10]
        
        # Sort by modification time for recent files
        files_by_modified = sorted(files_info, key=lambda x: x["modified"], reverse=True)
        analysis["recent_files"] = files_by_modified[:10]
        
        # Sort by creation time for oldest files
        files_by_created = sorted(files_info, key=lambda x: x["created"])
        analysis["oldest_files"] = files_by_created[:10]
        
        # Size distribution
        size_ranges = [
            (0, 1024, "< 1 KB"),
            (1024, 1024*100, "1 KB - 100 KB"),
            (1024*100, 1024*1024, "100 KB - 1 MB"),
            (1024*1024, 1024*1024*10, "1 MB - 10 MB"),
            (1024*1024*10, float('inf'), "> 10 MB")
        ]
        
        size_dist = {label: 0 for _, _, label in size_ranges}
        for file_info in files_info:
            size = file_info["size"]
            for min_size, max_size, label in size_ranges:
                if min_size <= size < max_size:
                    size_dist[label] += 1
                    break
        
        analysis["size_distribution"] = [{"range": k, "count": v} for k, v in size_dist.items()]
    
    return analysis

def generate_dashboard_html(analysis, path):
    """Generate the HTML dashboard"""
    
    # Format file size
    def format_size(size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    # Format timestamp
    def format_time(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")
    
    # Generate file type chart data
    file_types_data = []
    for ext, count in analysis["file_types"].most_common(10):
        file_types_data.append({"label": ext or "No extension", "value": count})
    
    # Generate size distribution chart data
    size_dist_data = analysis["size_distribution"]
    
    html = f"""
    <div class="folder-dashboard">
        <style>
            .dashboard-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }}
            .dashboard-card {{
                background: white;
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }}
            .dark .dashboard-card {{
                background: #1f2937;
                border-color: #374151;
            }}
            .stat-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 1rem;
                margin-bottom: 2rem;
            }}
            .stat-card {{
                background: linear-gradient(135deg, #3B82F6, #1D4ED8);
                color: white;
                padding: 1.5rem;
                border-radius: 0.5rem;
                text-align: center;
            }}
            .stat-card.green {{
                background: linear-gradient(135deg, #10B981, #047857);
            }}
            .stat-card.yellow {{
                background: linear-gradient(135deg, #F59E0B, #D97706);
            }}
            .stat-card.purple {{
                background: linear-gradient(135deg, #8B5CF6, #7C3AED);
            }}
            .stat-card.red {{
                background: linear-gradient(135deg, #EF4444, #DC2626);
            }}
            .stat-number {{
                font-size: 2rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }}
            .stat-label {{
                font-size: 0.875rem;
                opacity: 0.9;
            }}
            .chart-container {{
                height: 300px;
                margin: 1rem 0;
            }}
            .file-list {{
                max-height: 300px;
                overflow-y: auto;
            }}
            .file-item {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0.5rem 0;
                border-bottom: 1px solid #f3f4f6;
            }}
            .dark .file-item {{
                border-bottom-color: #374151;
            }}
            .file-name {{
                font-family: monospace;
                font-size: 0.875rem;
            }}
            .file-size {{
                color: #6b7280;
                font-size: 0.75rem;
            }}
            .dark .file-size {{
                color: #9ca3af;
            }}
            .dashboard-header {{
                text-align: center;
                margin-bottom: 2rem;
                padding: 2rem;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 0.5rem;
            }}
            .path-display {{
                font-family: monospace;
                background: rgba(255, 255, 255, 0.2);
                padding: 0.5rem 1rem;
                border-radius: 0.25rem;
                margin-top: 1rem;
            }}
        </style>
        
        <div class="dashboard-header">
            <h1>📊 Folder Analytics Dashboard</h1>
            <p>Comprehensive analysis of: <strong>{analysis['folder_name']}</strong></p>
            <div class="path-display">{path}</div>
            <p style="margin-top: 1rem; opacity: 0.9;">Analysis completed at {analysis['analysis_time']}</p>
        </div>
        
        <!-- Overview Statistics -->
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-number">{analysis['total_files']}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card green">
                <div class="stat-number">{analysis['total_dirs']}</div>
                <div class="stat-label">Directories</div>
            </div>
            <div class="stat-card yellow">
                <div class="stat-number">{format_size(analysis['total_size'])}</div>
                <div class="stat-label">Total Size</div>
            </div>
            <div class="stat-card purple">
                <div class="stat-number">{len(analysis['file_types'])}</div>
                <div class="stat-label">File Types</div>
            </div>
        </div>
        
        <!-- Detailed Analysis Grid -->
        <div class="dashboard-grid">
            <!-- File Types Distribution -->
            <div class="dashboard-card">
                <h3>📂 File Types Distribution</h3>
                <div class="chart-container">
    """
    
    # Add file types list
    if file_types_data:
        html += "<div class='file-list'>"
        for item in file_types_data:
            percentage = (item["value"] / analysis["total_files"] * 100) if analysis["total_files"] > 0 else 0
            html += f"""
                <div class="file-item">
                    <span class="file-name">{item['label']}</span>
                    <span class="file-size">{item['value']} files ({percentage:.1f}%)</span>
                </div>
            """
        html += "</div>"
    else:
        html += "<p>No files found</p>"
    
    html += """
                </div>
            </div>
            
            <!-- Size Distribution -->
            <div class="dashboard-card">
                <h3>📏 Size Distribution</h3>
                <div class="chart-container">
    """
    
    if size_dist_data:
        html += "<div class='file-list'>"
        for item in size_dist_data:
            percentage = (item["count"] / analysis["total_files"] * 100) if analysis["total_files"] > 0 else 0
            html += f"""
                <div class="file-item">
                    <span class="file-name">{item['range']}</span>
                    <span class="file-size">{item['count']} files ({percentage:.1f}%)</span>
                </div>
            """
        html += "</div>"
    
    html += """
                </div>
            </div>
            
            <!-- Largest Files -->
            <div class="dashboard-card">
                <h3>🔍 Largest Files</h3>
                <div class="file-list">
    """
    
    for file_info in analysis["largest_files"][:10]:
        html += f"""
            <div class="file-item">
                <span class="file-name">{file_info['name']}</span>
                <span class="file-size">{format_size(file_info['size'])}</span>
            </div>
        """
    
    html += """
                </div>
            </div>
            
            <!-- Recent Files -->
            <div class="dashboard-card">
                <h3>⏰ Recently Modified</h3>
                <div class="file-list">
    """
    
    for file_info in analysis["recent_files"][:10]:
        html += f"""
            <div class="file-item">
                <span class="file-name">{file_info['name']}</span>
                <span class="file-size">{format_time(file_info['modified'])}</span>
            </div>
        """
    
    # Add additional statistics
    html += f"""
                </div>
            </div>
            
            <!-- Additional Statistics -->
            <div class="dashboard-card">
                <h3>📈 Additional Statistics</h3>
                <div class="file-list">
                    <div class="file-item">
                        <span class="file-name">Hidden Files</span>
                        <span class="file-size">{analysis['hidden_files']}</span>
                    </div>
                    <div class="file-item">
                        <span class="file-name">Empty Files</span>
                        <span class="file-size">{analysis['empty_files']}</span>
                    </div>
                    <div class="file-item">
                        <span class="file-name">Average File Size</span>
                        <span class="file-size">{format_size(analysis['total_size'] / max(analysis['total_files'], 1))}</span>
                    </div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="dashboard-card">
                <h3>🚀 Quick Actions</h3>
                <div style="display: flex; flex-direction: column; gap: 0.5rem;">
                    <button onclick="refreshDashboard()" class="btn btn-blue">
                        🔄 Refresh Analysis
                    </button>
                    <button onclick="exportData()" class="btn btn-gray">
                        📊 Export Data
                    </button>
                    <button onclick="showDetails()" class="btn btn-gray">
                        🔍 View Details
                    </button>
                </div>
            </div>
        </div>
        
        <script>
            function refreshDashboard() {{
                window.location.reload();
            }}
            
            function exportData() {{
                const data = {json.dumps(analysis, indent=2)};
                const blob = new Blob([JSON.stringify(data, null, 2)], {{type: 'application/json'}});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'folder-analysis-{analysis["folder_name"]}.json';
                a.click();
                URL.revokeObjectURL(url);
            }}
            
            function showDetails() {{
                alert('Detailed view feature coming soon!');
            }}
        </script>
    </div>
    """
    
    return html
