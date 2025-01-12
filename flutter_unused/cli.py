import argparse
import os
from flutter_unused.finder import find_dart_files, extract_imports, read_pubspec_dependencies
from flutter_unused.report import Report, print_output
import glob
import re

def analyze_unused(project_dir, args):
    pubspec_path = os.path.join(project_dir, 'pubspec.yaml')
    if not os.path.exists(pubspec_path):
        print_output(f"Error: pubspec.yaml not found in {project_dir}", style="error")
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
            unused_files.append(os.path.relpath(dart_file,start=project_dir))
    
    return Report(unused_dependencies, unused_files)


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
