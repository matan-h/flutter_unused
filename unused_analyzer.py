import yaml
import os
import re
import argparse

def find_dart_files(directory):
    dart_files = []
    for root, _, files in os.walk(directory):
        if 'test' in root.split(os.sep) or 'integration_test' in root.split(os.sep):
            continue
        for file in files:
            if file.endswith(".dart"):
                dart_files.append(os.path.join(root, file))
    return dart_files

def extract_imports(dart_file):
    imports = set()
    with open(dart_file, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r"import ['\"]package:([^'\"]+)['\"]", line)
            if match:
                imports.add(match.group(1).split('/')[0])
            else:
                match = re.match(r"import ['\"]([^'\"]+)['\"]", line)
                if match:
                    import_path = match.group(1)
                    if not import_path.startswith('dart:'):
                        parts = import_path.split('/')
                        if parts and not parts[0].startswith('.'):
                            imports.add(parts[0])
    return imports

def read_pubspec_dependencies(pubspec_path):
    with open(pubspec_path, 'r', encoding='utf-8') as f:
        pubspec = yaml.safe_load(f)
        dependencies = set(pubspec.get('dependencies', {}).keys())
        dev_dependencies = set(pubspec.get('dev_dependencies', {}).keys())
        return dependencies.union(dev_dependencies)

def analyze_unused(project_dir):
    pubspec_path = os.path.join(project_dir, 'pubspec.yaml')
    if not os.path.exists(pubspec_path):
        print(f"Error: pubspec.yaml not found in {project_dir}")
        return

    all_dependencies = read_pubspec_dependencies(pubspec_path)
    used_dependencies = set()
    all_dart_files = find_dart_files(project_dir)

    for dart_file in all_dart_files:
        used_dependencies.update(extract_imports(dart_file))

    unused_dependencies = all_dependencies - used_dependencies
    unused_files = []

    # Check for unused files (basic check: if a file is not imported, it's considered unused)
    for dart_file in all_dart_files:
        is_used = False
        for other_dart_file in all_dart_files:
            if dart_file != other_dart_file:
                with open(other_dart_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if re.search(re.escape(os.path.basename(dart_file)), line):
                            is_used = True
                            break
                    if is_used:
                        break
        if not is_used:
            unused_files.append(dart_file)

    return unused_dependencies, unused_files

def main():
    parser = argparse.ArgumentParser(description="Analyze Flutter project for unused dependencies and files.")
    parser.add_argument("project_dir", help="Path to the Flutter project directory.")
    args = parser.parse_args()

    project_dir = args.project_dir
    unused_dependencies, unused_files = analyze_unused(project_dir)

    if unused_dependencies:
        print("Unused dependencies:")
        for dep in unused_dependencies:
            print(f"- {dep}")
    else:
        print("No unused dependencies found.")

    if unused_files:
        print("\nUnused files:")
        for file in unused_files:
            print(f"- {file}")
    else:
        print("\nNo unused files found.")

if __name__ == "__main__":
    main()
