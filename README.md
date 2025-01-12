# Flutter Unused

A tool to analyze unused dependencies and files in Flutter projects.

## Installation

```bash
pip install git+https://github.com/matan-h/flutter_unused.git
```

## Usage

To analyze a Flutter project, run the following command:

```bash
flutter_unused <path_to_your_flutter_project>
```

This will output a report of unused dependencies and files.

### Options

*   `-h`, `--help`: Show help message and exit.
*   `-o`, `--output <output_path>`: Specify the path to save the report to a file.
*   `--ignore <glob_pattern>`: Glob pattern to ignore files. This option can be used multiple times.

## Example

```bash
flutter_unused ./my_flutter_project --output report.txt
```

This will analyze the Flutter project located at `./my_flutter_project` and save the report to `report.txt`.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License.
