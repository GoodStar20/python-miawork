from .export import Export, ExportSR
from .upload import Upload, handle_uploaded_file, handle_uploaded_file_sr, uploadSR


import os

# If the temporary and export directories do not exist, they should be created
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

tmp_dir = os.path.join(BASE_DIR, "tmp")
export_dir = os.path.join(BASE_DIR, "export")

if not os.path.exists(tmp_dir):
    os.mkdir(tmp_dir)

if not os.path.exists(export_dir):
    os.mkdir(export_dir)