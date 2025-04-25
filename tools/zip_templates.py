import os
import zipfile

def zip_template(template_dir):
    """Zips the given template directory, storing directories and deflating files."""
    zip_path = f"{template_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(template_dir):
            # Add directories to the zip file (stored, not compressed)
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                arcname = os.path.relpath(dir_path, start=os.path.dirname(template_dir))
                zipf.write(dir_path, arcname, compress_type=zipfile.ZIP_STORED)
            
            # Add files to the zip file (deflated, compressed)
            for file_name in files:
                file_path = os.path.join(root, file_name)
                arcname = os.path.relpath(file_path, start=os.path.dirname(template_dir))
                zipf.write(file_path, arcname, compress_type=zipfile.ZIP_DEFLATED)
    print(f"Zipped: {zip_path}")

def find_templates(base_dir="./djangorocket/templates"):
    """Find all directories containing a cookiecutter.json file."""
    templates = []
    for root, _, files in os.walk(base_dir):
        if "cookiecutter.json" in files:
            templates.append(root)
    return templates

def zip_all_templates(base_dir="./djangorocket/templates"):
    """Find and zip all templates in the base directory."""
    templates = find_templates(base_dir)
    if not templates:
        print("No templates found to zip.")
        return

    for template_dir in templates:
        zip_template(template_dir)

if __name__ == "__main__":
    base_dir = "./djangorocket/templates"
    zip_all_templates(base_dir)