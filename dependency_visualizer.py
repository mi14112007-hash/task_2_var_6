import configparser
import os
import sys
import requests

def load_config():
    config_path = "config.ini"

    if not os.path.exists(config_path):
        print("❌ Ошибка: config.ini не найден")
        sys.exit(1)

    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    try:
        settings = cfg["settings"]
        data = {
            "package_name": settings["package_name"],
            "repository_url": settings["repository_url"],
            "test_mode": settings.getboolean("test_mode"),
            "test_repo_path": settings["test_repo_path"],
            "version": settings["version"],
            "max_depth": int(settings["max_depth"]),
            "filter_substring": settings["filter_substring"],
            "output_file": settings["output_file"]
        }
    except Exception as e:
        print(f"❌ Ошибка в конфигурации: {e}")
        sys.exit(1)

    return data


def fetch_dependencies(package, version, repo_url):
    url = f"{repo_url}/{package}/{version}/dependencies"
    print(f"🔗 Запрос: {url}")

    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        deps = []
        for dep in data.get("dependencies", []):
            if dep.get("kind") == "normal":  # runtime-deps only
                deps.append(dep["crate_id"])

        return deps

    except Exception as e:
        print(f"❌ Ошибка при получении зависимостей: {e}")
        return []


def main():
    cfg = load_config()

    print("=== Этап 2: Получение зависимостей ===")
    deps = fetch_dependencies(cfg["package_name"], cfg["version"], cfg["repository_url"])

    if deps:
        print(f"Зависимости пакета {cfg['package_name']} ({cfg['version']}):")
        for d in deps:
            print(f" - {d}")
    else:
        print("Нет зависимостей или ошибка в запросе")


if __name__ == "__main__":
    main()
