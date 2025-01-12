import yaml
import os
import re
import glob

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
