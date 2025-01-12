import yaml
import os
import re
import argparse
import glob

try:
    from rich.console import Console
    from rich.theme import Theme
    console = Console(theme=Theme(
        {
            "info": "green",
            "warning": "yellow",
            "error": "bold red",
        }
    ))
    rich_available = True
except ImportError:
    rich_available = False

def find_dart_files(directory):
    dart_files = []
    for root, _, files in os.walk(directory):
        if 'test' in root.split(os.sep) or 'integration_test' in root.split(os.sep) or '.dart_tool' in root.split(os.sep):
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

def analyze_unused(project_dir, args):
    pubspec_path = os.path.join(project_dir, 'pubspec.yaml')
    if not os.path.exists(pubspec_path):
        if rich_available:
            console.print(f"Error: pubspec.yaml not found in {project_dir}", style="error")
        else:
            print(f"Error: pubspec.yaml not found in {project_dir}")
        return

    all_dependencies = read_pubspec_dependencies(pubspec_path)
    used_dependencies = set()
    all_dart_files = find_dart_files(project_dir)

    ignored_files = []
    if args.ignore:
        for ignore_pattern in args.ignore:
            ignored_files.extend(glob.glob(os.path.join(project_dir, ignore_pattern), recursive=True))

    all_dart_files = [f for f in all_dart_files if f not in ignored_files]

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

def write_report(output_path, unused_dependencies, unused_files):
    with open(output_path, 'w', encoding='utf-8') as f:
        if unused_dependencies:
            f.write("Unused dependencies:\n")
            for dep in unused_dependencies:
                f.write(f"- {dep}\n")
        else:
            f.write("No unused dependencies found.\n")

        if unused_files:
            f.write("\nUnused files:\n")
            for file in unused_files:
                f.write(f"- {file}\n")
        else:
            f.write("\nNo unused files found.\n")

def main():
    parser = argparse.ArgumentParser(description="Analyze Flutter project for unused dependencies and files.")
    parser.add_argument("project_dir", help="Path to the Flutter project directory.")
    parser.add_argument("-o", "--output", help="Path to the output report file.")
    parser.add_argument("--ignore", help="Glob pattern to ignore files.", action='append', default=[])
    args = parser.parse_args()

    project_dir = args.project_dir
    unused_dependencies, unused_files = analyze_unused(project_dir, args)

    if args.output:
        write_report(args.output, unused_dependencies, unused_files)
    else:
        if unused_dependencies:
            if rich_available:
                console.print("Unused dependencies:", style="warning")
                for dep in unused_dependencies:
                    console.print(f"- {dep}", style="info")
            else:
                print("Unused dependencies:")
                for dep in unused_dependencies:
                    print(f"- {dep}")
        else:
            if rich_available:
                console.print("No unused dependencies found.", style="info")
            else:
                print("No unused dependencies found.")

        if unused_files:
            if rich_available:
                console.print("\nUnused files:", style="warning")
                for file in unused_files:
                    console.print(f"- {file}", style="info")
            else:
                print("\nUnused files:")
                for file in unused_files:
                    print(f"- {file}")
        else:
            if rich_available:
                console.print("\nNo unused files found.", style="info")
            else:
                print("\nNo unused files found.")

if __name__ == "__main__":
    main()
