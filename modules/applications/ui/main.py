import json
import os
import subprocess
from pathlib import Path
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTreeView, QComboBox, QLabel, QHeaderView
from PySide6.QtGui import QStandardItemModel, QStandardItem, QIcon
from PySide6.QtCore import Qt


class ApplicationsMain(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        # Data
        self.applications_data = []
        self.installeds = []
        self.current_group = "*"
        self.advanced_filter = False
        self.pending_changes = {"install": set(), "remove": set()}
        self.current_desktop = os.environ.get("XDG_SESSION_DESKTOP", "?").lower()

        # Top bar with title
        self.title_bar = QLabel(f"Applications (Desktop: {self.current_desktop})")
        self.main_layout.addWidget(self.title_bar)

        # Button bar
        self.button_bar = QHBoxLayout()
        self.main_layout.addLayout(self.button_bar)

        self.advanced_button = QPushButton("Advanced")
        self.advanced_button.setCheckable(True)
        self.advanced_button.toggled.connect(self.on_advanced_toggled)
        self.button_bar.addWidget(self.advanced_button)

        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.on_group_filter_changed)
        self.button_bar.addWidget(self.group_combo)

        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.on_reset_clicked)
        self.button_bar.addWidget(self.reset_button)

        self.update_system_button = QPushButton("Update System")
        self.update_system_button.setEnabled(False)
        self.update_system_button.clicked.connect(self.on_update_system_clicked)
        self.button_bar.addStretch()
        self.button_bar.addWidget(self.update_system_button)

        # Tree view for applications
        self.tree_view = QTreeView()
        self.tree_view.setEditTriggers(QTreeView.NoEditTriggers)
        self.main_layout.addWidget(self.tree_view)

        self.load_data()
        self.populate_view()

        self.setWindowTitle("Manjaro Application Utility")
        self.resize(800, 600)

    def load_data(self):
        data_path = Path(__file__).parent.parent / "data" / "default.json"
        with open(data_path, "r") as f:
            self.applications_data = json.load(f)

        self.group_combo.clear()
        self.group_combo.addItem("*")
        for group in self.applications_data:
            self.group_combo.addItem(group["name"])

        pkgs = []
        for group in (a["apps"] for a in self.applications_data):
            pkgs.extend(x for x in (p["pkg"] for p in group))

        output = subprocess.run(f"pacman -Qq {' '.join(pkgs)}", capture_output=True, shell=True, text=True, timeout=3).stdout
        if not output:
            return ""
        self.installeds = output.splitlines()
        # print(self.installeds)
        for group in self.applications_data:
            for app in group["apps"]:
                app["installed"] = app["pkg"] in self.installeds

    def populate_view(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Application", "Description", "Action"])
        model.itemChanged.connect(self.on_item_changed)
        self.tree_view.setModel(model)

        for group in self.applications_data:
            if self.current_group == "*" or self.current_group == group["name"]:
                # Filter applications in the group first
                filtered_apps = []
                for app in group["apps"]:
                    # Advanced filter
                    if not self.advanced_filter and "advanced" in app.get("filter", []):
                        continue

                    # Desktop filter
                    desktop_filter = app.get("desktop", [])
                    if desktop_filter:
                        show_app = True
                        for desktop in desktop_filter:
                            if desktop.startswith("!"):
                                if self.current_desktop == desktop[1:]:
                                    show_app = False
                                    break
                            elif self.current_desktop not in desktop_filter:
                                show_app = False
                                break
                        if not show_app:
                            continue

                    filtered_apps.append(app)

                # If there are apps to show in this group, add the group and the apps
                if filtered_apps:
                    group_item = QStandardItem(group["name"])
                    group_item.setIcon(QIcon.fromTheme(group.get("icon", "folder")))
                    model.appendRow(group_item)

                    for app in filtered_apps:
                        name_item = QStandardItem(app["name"])
                        name_item.setIcon(QIcon.fromTheme(app.get("icon", "application-x-executable")))

                        desc_item = QStandardItem(app["description"])

                        action_item = QStandardItem()
                        action_item.setCheckable(True)
                        action_item.setCheckState(Qt.Checked if app.get("installed") else Qt.Unchecked)
                        action_item.setData(app, Qt.UserRole)

                        group_item.appendRow([name_item, desc_item, action_item])

        # Adjust column widths
        self.tree_view.header().setSectionsMovable(False)
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.header().setMinimumSectionSize(40)
        self.tree_view.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tree_view.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

        if self.current_group != "*":
            self.tree_view.expandAll()
        else:
            self.tree_view.expandToDepth(0)

    def on_item_changed(self, item):
        if item.isCheckable():
            app_data = item.data(Qt.UserRole)
            if not app_data:
                return

            pkg = app_data["pkg"]
            is_checked = item.checkState() == Qt.Checked
            is_installed = app_data.get("installed", False)

            if is_checked and not is_installed:
                self.pending_changes["install"].add(pkg)
                self.pending_changes["remove"].discard(pkg)
            elif not is_checked and is_installed:
                self.pending_changes["remove"].add(pkg)
                self.pending_changes["install"].discard(pkg)
            else:
                # No change in state
                self.pending_changes["install"].discard(pkg)
                self.pending_changes["remove"].discard(pkg)

            self.update_system_button.setEnabled(bool(self.pending_changes["install"] or self.pending_changes["remove"]))

    def on_group_filter_changed(self, index):
        self.current_group = self.group_combo.itemText(index)
        self.populate_view()

    def on_advanced_toggled(self, checked):
        self.advanced_filter = checked
        self.populate_view()

    def on_reset_clicked(self):
        self.advanced_button.setChecked(False)
        self.group_combo.setCurrentIndex(0)
        self.pending_changes = {"install": set(), "remove": set()}
        self.update_system_button.setEnabled(False)
        self.populate_view()

    def on_update_system_clicked(self):
        print("Pending changes:")
        print(" To install:", self.pending_changes["install"])
        print(" To remove:", self.pending_changes["remove"])
