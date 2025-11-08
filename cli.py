import argparse
import json
import sys
from pathlib import Path

class CLI_App:
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.params = {}
        self.load_json_config()
        self.validate_params()

    def load_json_config(self):
        if not self.config_path.exists():
            raise Exception(f"Файл конфигурации '{self.config_path}' не найден.")

        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                self.params = json.load(f)
        except Exception as e:
            raise Exception(f"Ошибка чтения JSON: {e}")

        if not isinstance(self.params, dict):
            raise Exception("Некорректный формат config.json (ожидается объект JSON).")

    def validate_params(self):
        required_fields = [
            "package_name",
            "repo_url",
            "test_mode",
            "version",
            "output_image",
            "max_depth",
            "filter_substring"
        ]

        for field in required_fields:
            if field not in self.params:
                raise Exception(f"Отсутствует обязательный параметр: '{field}'")

        if not isinstance(self.params["package_name"], str) or not self.params["package_name"].strip():
            raise Exception("Параметр 'package_name' должен быть непустой строкой.")

        if not isinstance(self.params["repo_url"], str) or not self.params["repo_url"].strip():
            raise Exception("Параметр 'repo_url' должен быть непустой строкой.")
        
        if not isinstance(self.params["test_mode"], bool):
            raise Exception("Параметр 'test_mode' должен быть типа bool.")

        if not isinstance(self.params["version"], str) or not self.params["version"].strip():
            raise Exception("Параметр 'version' должен быть непустой строкой.")

        if not isinstance(self.params["output_image"], str) or not self.params["output_image"].strip():
            raise Exception("Параметр 'output_image' должен быть непустой строкой (имя файла изображения).")

        try:
            self.params["max_depth"] = int(self.params["max_depth"])
            if self.params["max_depth"] < 1:
                raise ValueError()
        except Exception:
            raise Exception("Параметр 'max_depth' должен быть целым числом >= 1.")

        if not isinstance(self.params["filter_substring"], str):
            raise Exception("Параметр 'filter_substring' должен быть строкой.")

    def print_params(self):
        print("=== Настройки приложения ===")
        for key, value in self.params.items():
            print(f"{key}: {value}")
        print("============================")


def main():
    parser = argparse.ArgumentParser(description="CLI-приложение для чтения конфигурации из JSON (этап 1).")
    parser.add_argument("--config", "-c", default="config.json", help="Путь к JSON файлу конфигурации")
    args = parser.parse_args()

    try:
        cli = CLI_App(args.config)
        cli.print_params()
    except Exception as e:
        print(f"[ОШИБКА КОНФИГУРАЦИИ] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
