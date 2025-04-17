import os
import zipfile

def zip_template(template_dir):
    """Zips the given template directory."""
    zip_path = f"{template_dir}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(template_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=template_dir)
                zipf.write(file_path, arcname)
    print(f"Zipped: {zip_path}")

def find_templates(base_dir="./templates"):
    """Find all directories containing a cookiecutter.json file."""
    templates = []
    for root, _, files in os.walk(base_dir):
        if "cookiecutter.json" in files:
            templates.append(root)
    return templates

def zip_all_templates(base_dir="./templates"):
    """Find and zip all templates in the base directory."""
    templates = find_templates(base_dir)
    if not templates:
        print("No templates found to zip.")
        return

    for template_dir in templates:
        zip_template(template_dir)

if __name__ == "__main__":
    base_dir = "./templates"
    zip_all_templates(base_dir)