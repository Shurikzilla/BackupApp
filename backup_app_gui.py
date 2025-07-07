import sys, os, subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout,
    QLabel, QPushButton, QListWidget, QCheckBox, QProgressBar,
    QTextEdit, QMessageBox, QFileDialog, QInputDialog, QHBoxLayout,
    QDialog, QListWidgetItem, QDialogButtonBox
)
from PyQt6.QtCore import QThread, pyqtSignal

from app_definitions import load_plugins, load_custom_rules
from detect_installed_apps import get_installed_display_names
from backup_engine import *
from scan_user_configs import scan_user_configs

class BackupWorker(QThread):
    progress = pyqtSignal(int)
    log_text = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, selected_apps, plugins, zip_enabled):
        super().__init__()
        self.apps = selected_apps
        self.plugins = plugins
        self.zip = zip_enabled

    def run(self):
        total = len(self.apps)
        for i, app in enumerate(self.apps):
            paths = self.plugins.get(app, {})
            out = os.path.join("Backup", app)
            os.makedirs(out, exist_ok=True)

            any_data = False
            for f in paths.get("files", []):
                if path_exists(f):
                    backup_file(f, out)
                    self.log_text.emit(f"[BACKUP] Файл: {f}")
                    any_data = True
            for d in paths.get("folders", []):
                if path_exists(d):
                    backup_folder(d, out)
                    self.log_text.emit(f"[BACKUP] Папка: {d}")
                    any_data = True
            for r in paths.get("registry", []):
                if registry_key_exists(r):
                    reg_path = os.path.join(out, f"{app}_reg.reg")
                    backup_registry_key(r, reg_path)
                    self.log_text.emit(f"[BACKUP] Реестр: {r}")
                    any_data = True

            if not any_data:
                self.log_text.emit(f"[INFO] Нет данных для: {app}")
            if self.zip and any_data:
                compress_folder(out, os.path.join("Backup", f"{app}_backup"))
                self.log_text.emit(f"[ZIP] Архив создан: {app}")

            self.progress.emit(int((i + 1) / total * 100))
        self.finished.emit()

class PluginEditDialog(QWidget):
    def __init__(self, name, data):
        super().__init__()
        self.setWindowTitle(f"Плагин: {name}")
        self.name = name
        self.data = data
        self.path = os.path.join("Plugins", f"example_{name.lower().replace(' ', '_')}.json")
        self.layout = QVBoxLayout()

        self.files = QListWidget()
        self.folders = QListWidget()
        self.registry = QListWidget()
        for f in data.get("files", []): self.files.addItem(f)
        for f in data.get("folders", []): self.folders.addItem(f)
        for f in data.get("registry", []): self.registry.addItem(f)

        self._section("Файлы", self.files)
        self._section("Папки", self.folders)
        self._section("Реестр", self.registry)

        save = QPushButton("💾 Сохранить")
        save.clicked.connect(self.save)
        self.layout.addWidget(save)
        self.setLayout(self.layout)

    def _section(self, label, lw):
        self.layout.addWidget(QLabel(label))
        hbox = QHBoxLayout()
        hbox.addWidget(lw)
        btns = QVBoxLayout()
        add = QPushButton("+")
        rm = QPushButton("–")
        add.clicked.connect(lambda: self._add(lw))
        rm.clicked.connect(lambda: self._rm(lw))
        btns.addWidget(add)
        btns.addWidget(rm)
        hbox.addLayout(btns)
        self.layout.addLayout(hbox)

    def _add(self, lw):
        text, ok = QInputDialog.getText(self, "Добавить", "Введите путь:")
        if ok and text:
            lw.addItem(text.strip())

    def _rm(self, lw):
        for item in lw.selectedItems():
            lw.takeItem(lw.row(item))

    def save(self):
        from json import dump
        out = {
            "files": [self.files.item(i).text() for i in range(self.files.count())],
            "folders": [self.folders.item(i).text() for i in range(self.folders.count())],
            "registry": [self.registry.item(i).text() for i in range(self.registry.count())]
        }
        with open(self.path, "w", encoding="utf-8") as f:
            dump({self.name: out}, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, "OK", "Сохранено")

class BackupApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BackupApp")
        self.plugins = {}
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.load_definitions()
        self.init_main_tab()
        self.init_logs_tab()
        self.init_plugin_tab()
        self.refresh_app_list()

    def load_definitions(self):
        self.plugins = load_plugins()
        self.plugins.update(load_custom_rules())

    def init_main_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.app_list = QListWidget()
        self.zip_cb = QCheckBox("Сжать в ZIP")
        self.restore_cb = QCheckBox("Режим восстановления")
        self.restore_original = QCheckBox("Восстановить в оригинальные места")
        self.restore_original.setChecked(True)
        self.choose_dir_btn = QPushButton("📁 Выбрать каталог восстановления")
        self.choose_dir_btn.setEnabled(False)
        self.choose_dir_btn.clicked.connect(self.pick_restore_dir)
        self.restore_original.toggled.connect(lambda v: self.choose_dir_btn.setEnabled(not v))

        self.restore_target_dir = None
        self.run_btn = QPushButton("▶ Выполнить")
        self.run_btn.clicked.connect(self.run_task)
        self.progress = QProgressBar()

        layout.addWidget(QLabel("Приложения:"))
        layout.addWidget(self.app_list)
        layout.addWidget(self.zip_cb)
        layout.addWidget(self.restore_cb)
        layout.addWidget(self.restore_original)
        layout.addWidget(self.choose_dir_btn)
        layout.addWidget(self.run_btn)
        layout.addWidget(self.progress)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Главная")
    def init_logs_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.logs = QTextEdit()
        self.logs.setReadOnly(True)
        layout.addWidget(self.logs)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "Логи")

    def init_plugin_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()

        self.found_configs = QListWidget()
        self.found_configs.addItems(scan_user_configs())
        self.found_configs.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        self.app_name = QTextEdit()
        self.app_name.setPlaceholderText("Имя нового плагина")

        btn_add = QPushButton("Добавить как плагин")
        btn_add.clicked.connect(self.save_plugin)

        self.plugin_list = QListWidget()
        self.plugin_list.addItems(sorted(self.plugins.keys()))

        btn_edit = QPushButton("Редактировать выбранный")
        btn_edit.clicked.connect(self.edit_plugin)

        btn_check = QPushButton("🧪 Проверить выбранный")
        btn_check.clicked.connect(self.check_plugin)

        btn_check_all = QPushButton("🧪 Проверить все плагины")
        btn_check_all.clicked.connect(self.check_all_plugins)

        layout.addWidget(QLabel("Найденные конфиги:"))
        layout.addWidget(self.found_configs)
        layout.addWidget(self.app_name)
        layout.addWidget(btn_add)
        layout.addWidget(QLabel("Существующие плагины:"))
        layout.addWidget(self.plugin_list)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_check)
        layout.addWidget(btn_check_all)

        tab.setLayout(layout)
        self.tabs.addTab(tab, "Плагины")
    def save_plugin(self):
        from json import dump
        selected = self.found_configs.selectedItems()
        name = self.app_name.toPlainText().strip()
        if not name or not selected:
            QMessageBox.warning(self, "Ошибка", "Укажите имя и выберите конфиги.")
            return
        plugin = {
            "files": [i.text() for i in selected],
            "folders": [],
            "registry": []
        }
        path = os.path.join("Plugins", f"example_{name.lower().replace(' ', '_')}.json")
        with open(path, "w", encoding="utf-8") as f:
            dump({name: plugin}, f, indent=2, ensure_ascii=False)
        QMessageBox.information(self, "Готово", f"Сохранено как: {path}")
        self.load_definitions()
        self.refresh_app_list()
        self.check_plugin_immediate(name)

    def check_plugin_immediate(self, name):
        from winreg import OpenKey, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE

        def key_exists(path):
            try:
                hive_str, sub = path.split("\\", 1)
                hive = {"HKEY_CURRENT_USER": HKEY_CURRENT_USER, "HKEY_LOCAL_MACHINE": HKEY_LOCAL_MACHINE}.get(hive_str)
                with OpenKey(hive, sub): return True
            except: return False

        plugin = self.plugins.get(name)
        if not plugin:
            QMessageBox.warning(self, "Ошибка", "Плагин не найден")
            return

        result = QListWidget()
        result.addItem(f"🧪 Проверка плагина: {name}")
        errors_found = False

        for f in plugin.get("files", []):
            if os.path.isfile(expand(f)):
                result.addItem(f"✅ Файл: {f}")
            else:
                result.addItem(f"⚠️ Нет файла: {f}")
                errors_found = True
        for d in plugin.get("folders", []):
            if os.path.isdir(expand(d)):
                result.addItem(f"✅ Папка: {d}")
            else:
                result.addItem(f"⚠️ Нет папки: {d}")
                errors_found = True
        for r in plugin.get("registry", []):
            if key_exists(r):
                result.addItem(f"✅ Реестр: {r}")
            else:
                result.addItem(f"⚠️ Ключ реестра не найден: {r}")
                errors_found = True

        dlg = QDialog(self)
        dlg.setWindowTitle(f"🧪 Проверка плагина: {name}")
        dlg.resize(600, 400)
        layout = QVBoxLayout()
        layout.addWidget(result)

        buttons = QDialogButtonBox()
        buttons.addButton("Закрыть", QDialogButtonBox.StandardButton.RejectRole)
        if errors_found:
            edit_btn = QPushButton("✏️ Открыть в редакторе")
            edit_btn.clicked.connect(lambda: PluginEditDialog(name, plugin).show())
            buttons.addButton(edit_btn, QDialogButtonBox.ButtonRole.ActionRole)

        layout.addWidget(buttons)
        dlg.setLayout(layout)
        dlg.exec()
    def edit_plugin(self):
        item = self.plugin_list.currentItem()
        if not item:
            return
        name = item.text()
        dlg = PluginEditDialog(name, self.plugins[name])
        dlg.show()

    def check_plugin(self):
        self.check_plugin_immediate(self.plugin_list.currentItem().text())

    def check_all_plugins(self):
        from winreg import OpenKey, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE

        def key_exists(path):
            try:
                hive_str, sub = path.split("\\", 1)
                hive = {"HKEY_CURRENT_USER": HKEY_CURRENT_USER, "HKEY_LOCAL_MACHINE": HKEY_LOCAL_MACHINE}.get(hive_str)
                with OpenKey(hive, sub): return True
            except: return False

        result = QListWidget()
        total = len(self.plugins)
        ok_count, warn_count, err_count = 0, 0, 0

        for name, data in sorted(self.plugins.items()):
            result.addItem(f"🔹 {name}")
            empty = not any(data.get(k) for k in ("files", "folders", "registry"))
            if empty:
                result.addItem("  🟥 Плагин пуст: ни одного пути не задано")
                err_count += 1
                continue

            def check_each(item_type, label, test):
                nonlocal ok_count, warn_count
                for path in data.get(label, []):
                    if test(expand(path)):
                        result.addItem(f"  ✅ {label}: {path}")
                        ok_count += 1
                    else:
                        result.addItem(f"  ⚠️ {label} не найден: {path}")
                        warn_count += 1

            check_each(data, "files", os.path.isfile)
            check_each(data, "folders", os.path.isdir)

            for reg in data.get("registry", []):
                if key_exists(reg):
                    result.addItem(f"  ✅ Реестр: {reg}")
                    ok_count += 1
                else:
                    result.addItem(f"  ⚠️ Реестр не найден: {reg}")
                    warn_count += 1

        dlg = QDialog(self)
        dlg.setWindowTitle(f"🧪 Проверено {total} плагинов — ✅ {ok_count}, ⚠ {warn_count}, 🟥 {err_count}")
        dlg.resize(800, 500)
        layout = QVBoxLayout()
        layout.addWidget(result)
        dlg.setLayout(layout)
        dlg.exec()
    def refresh_app_list(self):
        self.app_list.clear()
        installed = get_installed_display_names()
        visible = [name for name in self.plugins if name in installed or name.startswith("My")]
        self.app_list.addItems(visible)
        self.progress.setValue(0)
        self.append_log(f"[GUI] Обновлён список приложений ({len(visible)})")

    def append_log(self, msg):
        self.logs.append(msg)

    def run_task(self):
        selected = [i.text() for i in self.app_list.selectedItems()]
        if not selected:
            QMessageBox.warning(self, "Нет выбора", "Выберите хотя бы одно приложение")
            return

        if self.restore_cb.isChecked():
            self.run_restore(selected)
        else:
            self.run_backup(selected)

    def run_backup(self, selected):
        self.run_btn.setEnabled(False)
        self.logs.clear()
        self.progress.setValue(0)

        self.worker = BackupWorker(selected, self.plugins, self.zip_cb.isChecked())
        self.worker.progress.connect(self.progress.setValue)
        self.worker.log_text.connect(self.append_log)
        self.worker.finished.connect(self.on_worker_done)
        self.worker.start()

    def run_restore(self, selected):
        for app in selected:
            paths = self.plugins.get(app, {})
            out = os.path.join("Backup", app)

            for f in paths.get("files", []):
                src = os.path.join(out, os.path.basename(f))
                if os.path.exists(src):
                    dst = expand(f) if self.restore_original.isChecked() else os.path.join(self.restore_target_dir, os.path.basename(f))
                    restore_file(src, dst)

            for d in paths.get("folders", []):
                src = os.path.join(out, os.path.basename(d))
                if os.path.exists(src):
                    dst = expand(d) if self.restore_original.isChecked() else os.path.join(self.restore_target_dir, os.path.basename(d))
                    restore_folder(src, dst)

            for r in paths.get("registry", []):
                if self.restore_original.isChecked():
                    reg_file = os.path.join(out, f"{app}_reg.reg")
                    if os.path.exists(reg_file):
                        restore_registry_key(reg_file)

        self.append_log("✅ Восстановление завершено.")
        self.refresh_app_list()

    def pick_restore_dir(self):
        dir = QFileDialog.getExistingDirectory(self, "Выбор папки")
        if dir:
            self.restore_target_dir = dir
            self.append_log(f"Каталог восстановления: {dir}")

    def on_worker_done(self):
        self.run_btn.setEnabled(True)
        self.append_log("✅ Резервное копирование завершено.")
        self.refresh_app_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    app.exec()

