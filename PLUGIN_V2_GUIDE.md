# Plugin System V2 - Page Mode Implementation Guide

## Overview

The Plugin System V2 introduces **page mode** support, allowing plugins to render as full pages instead of just modals. This provides a much better user experience for complex plugin outputs that need more screen real estate.

## Key Features

### ✅ Implemented Features

1. **Clean V2 Manifest Schema**: Simple flag-based approach for page mode support
2. **Master Template System**: Guaranteed consistent navigation back to file explorer
3. **Folder-Constrained Operation**: Plugins operate within current folder context
4. **Dual Mode Support**: Plugins can support both modal and page modes
5. **Backward Compatibility**: V1 plugins continue to work unchanged
6. **Enhanced UI**: Dropdown selection for page-capable plugins

## V2 Manifest Schema

### Required V2 Fields

```json
{
    "schema_version": "2.0",
    "supports_page_mode": true,
    "page_title": "Custom Page Title (optional)"
}
```

### Complete V2 Manifest Example

```json
{
    "id": "folder_dashboard",
    "name": "Folder Dashboard", 
    "version": "1.0.0",
    "entry_point": "dashboard_plugin",
    "type": "ui",
    "icon": "📊",
    "description": "Comprehensive folder analysis with charts and statistics",
    "schema_version": "2.0",
    "supports_page_mode": true,
    "page_title": "Folder Analytics Dashboard",
    "dependencies": [],
    "settings": {}
}
```

## Architecture Components

### 1. Enhanced Plugin Manager

**New Methods:**
- `get_page_mode_plugins()`: Returns V2 plugins supporting page mode
- `get_plugin_manifest(plugin_id)`: Get manifest for specific plugin
- Enhanced `get_toolbar_items()`: Includes V2 metadata

### 2. Page Mode Route Handler

**Route:** `/plugin/<plugin_id>?path=<current_path>`

**Key Features:**
- Folder constraint enforcement
- Security path validation  
- Master template rendering
- Error handling with consistent UI

### 3. Master Template System

**Template:** `plugin_page_master.html`

**Guaranteed Elements:**
- "Back to Explorer" navigation
- Current folder context display
- Plugin toolbar with refresh/modal switch
- Consistent error handling
- Responsive layout

### 4. Enhanced Frontend

**Features:**
- Dropdown mode selection for V2 plugins
- Visual indicators for page-capable plugins
- Keyboard navigation support
- Automatic dropdown hiding

## Usage Guide

### For Plugin Developers

#### 1. Convert Existing Plugin to V2

1. **Update manifest.json:**
```json
{
    "schema_version": "2.0",
    "supports_page_mode": true,
    "page_title": "My Plugin Dashboard"
}
```

2. **Enhance plugin output for page mode:**
```python
def execute(path, **kwargs):
    # Your existing plugin logic
    result = analyze_data(path)
    
    # Generate rich HTML for page mode
    html_output = generate_comprehensive_dashboard(result)
    
    return {
        "success": True,
        "output": html_output,
        "title": "Comprehensive Analysis",
        "is_html": True,
        "content_type": "html"
    }
```

#### 2. Page Mode Best Practices

1. **Rich HTML Output**: Design for full-page display
2. **Responsive Design**: Support mobile and desktop
3. **Interactive Elements**: Add buttons, charts, tabs
4. **Export Features**: Allow data download/sharing
5. **Real-time Updates**: Consider auto-refresh for live data

### For Users

#### 1. Identifying V2 Plugins

- Look for the 📄 indicator next to plugin names
- V2 plugins show dropdown on click

#### 2. Using Page Mode

1. **Via Dropdown:**
   - Click V2 plugin button
   - Select "Full Page View" from dropdown

2. **Direct Navigation:**
   - URL pattern: `/plugin/<plugin_id>?path=<folder_path>`

3. **Switching Modes:**
   - Use "Quick View" button in page mode for modal
   - Use "Full Page View" from modal dropdown

## Sample Plugin: Folder Dashboard

### Features Demonstrated

1. **Comprehensive Analysis**: File statistics, size distribution, recent files
2. **Rich Visualization**: Charts, grids, interactive elements  
3. **Export Functionality**: JSON data export
4. **Responsive Design**: Works on all screen sizes
5. **Modern UI**: Gradients, cards, proper spacing

### Key Implementation Points

1. **HTML Generation**: Complex dashboard with CSS styling
2. **Data Processing**: File system analysis with statistics
3. **Interactive Features**: JavaScript functions for export/refresh
4. **Error Handling**: Graceful fallbacks for permission issues

## Technical Implementation

### 1. Plugin Loading Process

```python
# V2 Detection in PluginManager
def _load_ui_plugin(self, plugin_name, plugin_path, manifest):
    # ... existing logic ...
    
    # Add V2 support to toolbar items
    self.toolbar_items.append({
        "id": manifest["id"],
        "name": manifest["name"], 
        "icon": manifest["icon"],
        "description": manifest.get("description", ""),
        "supports_page_mode": manifest.get("supports_page_mode", False),
        "schema_version": manifest.get("schema_version", "1.0"),
        "page_title": manifest.get("page_title")
    })
```

### 2. Route Handler Implementation

```python
@app.route('/plugin/<plugin_id>')
def plugin_page(plugin_id):
    # Get current path (folder constraint)
    current_path = request.args.get('path', '')
    
    # Verify plugin supports page mode
    page_plugins = app.plugin_manager.get_page_mode_plugins()
    if plugin_id not in page_plugins:
        abort(404)
    
    # Security: path validation
    # Plugin execution with folder constraint
    # Master template rendering
```

### 3. Frontend Enhancement

```javascript
// V2 Plugin Detection
if (supportsPage && schemaVersion === '2.0') {
    // Show dropdown for mode selection
    dropdown.classList.toggle('hidden');
} else {
    // Direct modal execution for V1 plugins
    executePlugin(pluginId, currentPath);
}
```

## Migration Path

### Phase 1: V2 Infrastructure ✅
- [x] V2 manifest schema
- [x] Enhanced plugin manager  
- [x] Page mode route handler
- [x] Master template system

### Phase 2: Sample Implementation ✅
- [x] Folder Dashboard V2 plugin
- [x] Frontend UI enhancements
- [x] Testing and validation

### Phase 3: Plugin Migration (Future)
- [ ] Convert existing plugins to V2
- [ ] Add page mode to complex plugins
- [ ] Enhanced templates and layouts

## Testing

### Validation Checklist

- [x] V2 plugins load correctly
- [x] Page mode navigation works
- [x] Folder constraint enforcement
- [x] Modal/page mode switching
- [x] Error handling with master template
- [x] Responsive design
- [x] Keyboard navigation

### Test Results

```
✅ Folder Dashboard V2 plugin loaded successfully!
   Schema Version: 2.0
   Supports Page Mode: True
   Page Title: Folder Analytics Dashboard

🧪 Plugin execution successful!
   Title: Folder Dashboard - web-file-explorer
   HTML Output: 21083 characters
   Content Type: html
```

## Conclusion

The Plugin System V2 successfully implements page mode functionality with:

1. **Clean Architecture**: Simple V2 schema without over-engineering
2. **Folder Constraint**: Plugins operate within current directory context
3. **Master Template**: Guaranteed consistent navigation back to explorer
4. **Backward Compatibility**: V1 plugins continue working unchanged  
5. **Enhanced UX**: Rich full-page plugin experiences

The system is ready for production use and provides a solid foundation for migrating existing plugins to take advantage of page mode capabilities.
