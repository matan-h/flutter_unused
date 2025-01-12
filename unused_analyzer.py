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

def print_output(message, style=None):
    if rich_available:
        console.print(message, style=style)
    else:
        print(message)

def find_dart_files(directory):
    dart_files = []
    test_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".dart"):
                full_path = os.path.join(root, file)
                if 'test' in root.split(os.sep) or 'integration_test' in root.split(os.sep):
                    test_files.append(full_path)
                elif '.dart_tool' not in root.split(os.sep):
                    dart_files.append(full_path)
    return dart_files, test_files

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
    all_dart_files, test_files = find_dart_files(project_dir)

    ignored_files = []
    if args.ignore:
        for ignore_pattern in args.ignore:
            ignored_files.extend(glob.glob(os.path.join(project_dir, ignore_pattern), recursive=True))

    all_dart_files = [f for f in all_dart_files if f not in ignored_files]
    
    for dart_file in all_dart_files:
        used_dependencies.update(extract_imports(dart_file))
    for test_file in test_files:
        used_dependencies.update(extract_imports(test_file))

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
    
    return Report(unused_dependencies, unused_files)

class Report:
    def __init__(self, unused_dependencies, unused_files):
        self.unused_dependencies = unused_dependencies
        self.unused_files = unused_files

    def write_report(self, output_path):
        report = {}
        if self.unused_dependencies:
            report['unused_dependencies'] = list(self.unused_dependencies)
        else:
            report['unused_dependencies'] = []

        if self.unused_files:
            report['unused_files'] = [os.path.relpath(f, start=os.getcwd()) for f in self.unused_files]
        else:
            report['unused_files'] = []

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(report, f, indent=2)

    def print_report(self):
        if self.unused_dependencies:
            print_output("Unused dependencies:", style="warning")
            for dep in self.unused_dependencies:
                print_output(f"- {dep}", style="info")
        else:
            print_output("No unused dependencies found.", style="info")

        if self.unused_files:
            print_output("\nUnused files:", style="warning")
            for file in self.unused_files:
                print_output(f"- {os.path.relpath(file, start=os.getcwd())}", style="info")
        else:
            print_output("\nNo unused files found.", style="info")


def main():
    parser = argparse.ArgumentParser(description="Analyze Flutter project for unused dependencies and files.")
    parser.add_argument("project_dir", help="Path to the Flutter project directory.")
    parser.add_argument("-o", "--output", help="Path to the output report file.")
    parser.add_argument("--ignore", help="Glob pattern to ignore files.", action='append', default=[])
    args = parser.parse_args()

    project_dir = os.path.realpath(args.project_dir)
    report = analyze_unused(project_dir, args)

    if report:
        if args.output:
            report.write_report(args.output)
        else:
            report.print_report()

if __name__ == "__main__":
    main()
