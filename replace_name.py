import os

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        # Skip binary files or non-utf-8 files
        return
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    # Replace occurrences
    new_content = content.replace("Drona", "Bhishma's")
    new_content = new_content.replace("drona", "bhishma's")
    new_content = new_content.replace("DRONA", "BHISHMA'S")

    if new_content != content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filepath}")
        except Exception as e:
            print(f"Error writing {filepath}: {e}")

def main():
    exclude_dirs = {'venv', 'node_modules', '.git', '__pycache__', 'airflow'}
    exclude_exts = {'.png', '.jpg', '.jpeg', '.gif', '.zip', '.pdf', '.pyc', '.exe', '.dll', '.so'}

    for root, dirs, files in os.walk('.'):
        # Mutate dirs in-place to skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_exts:
                continue

            filepath = os.path.join(root, file)
            # Skip this script itself
            if os.path.basename(filepath) == 'replace_name.py':
                continue

            replace_in_file(filepath)

if __name__ == '__main__':
    main()
