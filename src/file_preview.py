"""
File Preview functionality for the Web File Explorer.
Provides preview capabilities for various file types.
"""
from flask import Blueprint, render_template, request, abort, current_app, jsonify
import os
import mimetypes
import logging
import magic
import base64
import pygments
from pygments.lexers import get_lexer_for_filename, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

# Setup logging
logger = logging.getLogger("file_preview")

# Create Blueprint for file preview
file_preview_bp = Blueprint('file_preview', __name__)

# Define supported file types
SUPPORTED_TEXT_TYPES = [
    'text/plain', 'text/html', 'text/css', 'text/javascript', 
    'application/json', 'application/xml', 'application/x-sh', 
    'application/x-httpd-php', 'application/x-python-code'
]

SUPPORTED_IMAGE_TYPES = [
    'image/jpeg', 'image/png', 'image/gif', 'image/svg+xml'
]

SUPPORTED_PDF_TYPES = [
    'application/pdf'
]

@file_preview_bp.route('/<path:path>')
def preview_file(path):
    """Preview a file without downloading it"""
    # Use configured BASE_DIR
    base_dir = current_app.config.get('BASE_DIR')
    if not base_dir:
        abort(500, description="Application base directory not configured.")
        
    # Convert the path to absolute path relative to configured BASE_DIR
    abs_path = os.path.abspath(os.path.join(base_dir, path))
    
    # Security check to prevent directory traversal attacks
    if not abs_path.startswith(os.path.abspath(base_dir)):
        abort(403)  # Forbidden
    
    # Check if path is a file
    if not os.path.isfile(abs_path):
        abort(404)  # Not Found
    
    try:
        # Determine file type
        file_mime = magic.Magic(mime=True).from_file(abs_path)
        
        # Handle file preview based on type
        if any(file_mime.startswith(t) for t in SUPPORTED_TEXT_TYPES) or file_mime.startswith('text/'):
            return render_text_preview(abs_path, file_mime, path)
        elif any(file_mime.startswith(t) for t in SUPPORTED_IMAGE_TYPES):
            return render_image_preview(abs_path, file_mime, path)
        elif any(file_mime.startswith(t) for t in SUPPORTED_PDF_TYPES):
            return render_pdf_preview(abs_path, file_mime, path)
        else:
            return render_unsupported_preview(abs_path, file_mime, path)
    except Exception as e:
        logger.error(f"Error previewing file {abs_path}: {e}")
        abort(500, description=f"Error previewing file: {str(e)}")

def render_text_preview(file_path, file_mime, relative_path):
    """Render preview for text files with syntax highlighting"""
    try:
        with open(file_path, 'r', errors='replace') as f:
            content = f.read()
        
        # Apply syntax highlighting if possible
        try:
            lexer = get_lexer_for_filename(file_path)
        except ClassNotFound:
            try:
                lexer = guess_lexer(content)
            except ClassNotFound:
                # Fallback to plain text
                lexer = get_lexer_for_filename("file.txt")
                
        formatter = HtmlFormatter(linenos=True, cssclass="source-code")
        highlighted_content = pygments.highlight(content, lexer, formatter)
        
        # Get CSS for syntax highlighting
        highlight_css = HtmlFormatter().get_style_defs('.source-code')
        
        return render_template('file_preview.html', 
                             file_path=relative_path,
                             file_name=os.path.basename(file_path),
                             file_type=file_mime,
                             content=highlighted_content,
                             highlight_css=highlight_css,
                             preview_type='text',
                             file_size=os.path.getsize(file_path))
    except UnicodeDecodeError:
        # If can't decode as text, treat as binary
        return render_unsupported_preview(file_path, file_mime, relative_path)

def render_image_preview(file_path, file_mime, relative_path):
    """Render preview for image files"""
    # For SVG, we can embed directly
    if file_mime == 'image/svg+xml':
        try:
            with open(file_path, 'r') as f:
                svg_content = f.read()
                
            return render_template('file_preview.html', 
                                 file_path=relative_path,
                                 file_name=os.path.basename(file_path),
                                 file_type=file_mime,
                                 svg_content=svg_content,
                                 preview_type='svg',
                                 file_size=os.path.getsize(file_path))
        except:
            # Fall back to image rendering if SVG can't be parsed
            pass
    
    # For other images, we'll use base64 encoding
    try:
        with open(file_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')
            
        return render_template('file_preview.html', 
                             file_path=relative_path,
                             file_name=os.path.basename(file_path),
                             file_type=file_mime,
                             image_data=image_data,
                             preview_type='image',
                             file_size=os.path.getsize(file_path))
    except Exception as e:
        logger.error(f"Error encoding image {file_path}: {e}")
        return render_unsupported_preview(file_path, file_mime, relative_path)

def render_pdf_preview(file_path, file_mime, relative_path):
    """Render preview for PDF files"""
    # Create a relative URL for the PDF
    pdf_url = f"/explore/{relative_path}"
    
    return render_template('file_preview.html', 
                         file_path=relative_path,
                         file_name=os.path.basename(file_path),
                         file_type=file_mime,
                         pdf_url=pdf_url,
                         preview_type='pdf',
                         file_size=os.path.getsize(file_path))

def render_unsupported_preview(file_path, file_mime, relative_path):
    """Render preview for unsupported file types"""
    file_size = os.path.getsize(file_path)
    
    return render_template('file_preview.html', 
                         file_path=relative_path,
                         file_name=os.path.basename(file_path),
                         file_type=file_mime,
                         preview_type='unsupported',
                         file_size=file_size)

def register_blueprint(app):
    """Register the file preview blueprint with the Flask app"""
    app.register_blueprint(file_preview_bp, url_prefix='/preview')
    
    # Modify the existing explore route to add a preview option
    @app.context_processor
    def inject_preview_url():
        def get_preview_url(path):
            return f"/preview/{path}"
        return {'get_preview_url': get_preview_url}