import argparse
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
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

    def get_pom_url(self):
        repo = self.params["repo_url"].rstrip('/')
        group_id, artifact_id = self.params["package_name"].split(":")
        version = self.params["version"]

        group_path = group_id.replace(".", "/")
        pom_url = f"{repo}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"
        return pom_url

    def download_pom(self, pom_url):
        try:
            with urllib.request.urlopen(pom_url) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            raise Exception(f"Не удалось загрузить POM-файл по адресу {pom_url}: {e}")

    def parse_dependencies(self, pom_content):
        try:
            root = ET.fromstring(pom_content)
        except Exception as e:
            raise Exception(f"Ошибка парсинга XML POM: {e}")

        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        deps = []
        for dep in root.findall(".//m:dependencies/m:dependency", ns):
            group_id = dep.findtext("m:groupId", default="", namespaces=ns)
            artifact_id = dep.findtext("m:artifactId", default="", namespaces=ns)
            version = dep.findtext("m:version", default="(не указана)", namespaces=ns)
            scope = dep.findtext("m:scope", default="compile", namespaces=ns)

            filt = self.params["filter_substring"]
            if filt and filt not in group_id and filt not in artifact_id:
                continue

            deps.append({
                "groupId": group_id,
                "artifactId": artifact_id,
                "version": version,
                "scope": scope
            })

        return deps

    def show_dependencies(self):
        pom_url = self.get_pom_url()
        print(f"Загружается POM-файл: {pom_url}")

        pom_content = self.download_pom(pom_url)
        dependencies = self.parse_dependencies(pom_content)

        if not dependencies:
            print("Нет зависимостей (или фильтр исключил все).")
            return

        print("\n=== Зависимости пакета ===")
        for dep in dependencies:
            print(f"{dep['groupId']}:{dep['artifactId']}:{dep['version']} (scope={dep['scope']})")
        print("=================================\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", "-c", default="config.json", help="Путь к JSON файлу конфигурации")
    args = parser.parse_args()

    try:
        cli = CLI_App(args.config)
        cli.show_dependencies()
    except Exception as e:
        print(f"[ОШИБКА] {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
