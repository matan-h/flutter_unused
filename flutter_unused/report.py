import yaml
import os
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
            report['unused_files'] = [f for f in self.unused_files]
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
