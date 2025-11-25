import configparser
import os
import sys

# ===========================
# Этап 1: Загрузка конфигурации
# ===========================
def load_config():
    config_path = "config.ini"

    if not os.path.exists(config_path):
        print("❌ Ошибка: config.ini не найден")
        sys.exit(1)

    cfg = configparser.ConfigParser()
    cfg.read(config_path)

    try:
        settings = {
            "package_name": cfg.get("SETTINGS", "package_name"),
            "repo_url": cfg.get("SETTINGS", "repo_url"),
            "test_mode": cfg.getboolean("SETTINGS", "test_mode"),
            "package_version": cfg.get("SETTINGS", "package_version"),
            "max_depth": cfg.getint("SETTINGS", "max_depth"),
            "filter_substring": cfg.get("SETTINGS", "filter_substring")
        }
    except (configparser.NoOptionError, configparser.NoSectionError, ValueError) as e:
        print(f"❌ Ошибка конфигурации: {e}")
        sys.exit(1)

    return settings

# ===========================
# Этап 2: Получение зависимостей
# ===========================
def get_direct_dependencies(package_name, repo_url, version, test_mode):
    dependencies = {}
    
    if test_mode:
        if not os.path.exists(repo_url):
            print(f"❌ Ошибка: файл тестового репозитория {repo_url} не найден")
            sys.exit(1)

        with open(repo_url, "r") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" not in line:
                    print(f"❌ Ошибка формата в строке {line_num}: '{line}'")
                    sys.exit(1)
                pkg, deps = line.split(":", 1)
                pkg = pkg.strip()
                deps_list = [d.strip() for d in deps.split(",") if d.strip()]
                dependencies[pkg] = deps_list
    else:
        # Заглушка для реального репозитория Cargo
        dependencies[package_name] = []

    if package_name not in dependencies:
        print(f"❌ Ошибка: пакет {package_name} не найден в репозитории")
        sys.exit(1)

    return dependencies

# ===========================
# Этап 3: Построение графа зависимостей
# ===========================
def build_dependency_graph(package_name, dependencies, max_depth, filter_substring):
    graph = {}
    visited = set()

    def bfs(node, depth):
        if depth > max_depth:
            return
        if node in visited:
            return
        if filter_substring and filter_substring in node:
            return
        visited.add(node)
        graph[node] = dependencies.get(node, [])
        for dep in graph[node]:
            bfs(dep, depth + 1)

    bfs(package_name, 0)

    # Выводим только граф зависимостей
    for k in sorted(graph.keys()):
        print(f"{k}: {sorted(graph[k])}")

    return graph

# ===========================
# Этап 4: Порядок загрузки зависимостей с проверкой эталона
# ===========================
def get_load_order(graph, package_name, expected_order=None):
    visited = set()
    order = []

    def dfs(node):
        if node in visited:
            return
        visited.add(node)
        for dep in graph.get(node, []):
            dfs(dep)
        order.append(node)

    dfs(package_name)

    # Вывод порядка загрузки
    print(f"Порядок загрузки зависимостей для {package_name}: {order}")

    # Сравнение с эталонным порядком (для тестирования)
    if expected_order:
        if order == expected_order:
            print("✅ Порядок совпадает с ожидаемым эталоном.")
        else:
            print(f"Расхождение с ожидаемым порядком: {expected_order}")
            print("   Возможное объяснение: упрощённый алгоритм DFS не учитывает все нюансы реального менеджера пакетов (версии, optional dependencies и features).")

    return order

# ===========================
# Главная функция
# ===========================
def main():
    settings = load_config()
    deps = get_direct_dependencies(
        settings["package_name"],
        settings["repo_url"],
        settings["package_version"],
        settings["test_mode"]
    )
    graph = build_dependency_graph(
        settings["package_name"],
        deps,
        settings["max_depth"],
        settings["filter_substring"]
    )

    # Пример эталонного порядка для тестирования
    # Для реального репозитория можно оставить None
    expected_order = ['D', 'B', 'E', 'C', 'A']
    get_load_order(graph, settings["package_name"], expected_order)

if __name__ == "__main__":
    main()
