import configparser
import os
import sys

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

def main():
    cfg = load_config()
    print("=== Конфигурация (Этап 1) ===")
    for key, value in cfg.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
