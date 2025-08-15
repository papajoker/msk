#!/usr/bin/env python
from pathlib import Path

from PySide6.QtCore import (
    QLibraryInfo,
    QLocale,
    QTranslator,
)
from PySide6.QtWidgets import QApplication
from ui import MirrorsWidget


def traduction():
    """
    FIX : return QTranslator or is clear in QT
    """
    lang = QLocale.languageToCode(QLocale.system().language())
    if len(lang) < 2:
        return

    trans = [QTranslator()] * 2
    # trans[0] =
    if trans[0].load(
        f"qt_{lang}",
        QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath),
    ):
        QApplication.installTranslator(trans[0])
    else:
        print(
            "QT trad not loaded ?",
            QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath),
        )

    dir_ = Path(__file__).resolve().parent
    locale_dir = Path(f"/usr/share/locale/{lang}/LC_MESSAGES/")
    if not str(dir_).startswith("/usr/"):
        locale_dir = dir_ / f"../../../i18n/{lang}/LC_MESSAGES/"
    locale_dir = locale_dir.resolve() / f"msm_{dir_.parts[-1]}_{lang}.qm"

    if locale_dir.exists():
        if trans[1].load(str(locale_dir)):
            if not QApplication.installTranslator(trans[1]):
                print(f" ??? warning: translation not loaded ! ({locale_dir})")
        else:
            print(f"warning: translation not loaded ! ({locale_dir})")
    else:
        print(f"error: translation not found ! ({locale_dir})")
    return trans


def main():
    app = QApplication([])

    app.translate("NAME", "Mirrors")  # title in plugin.py ?
    _ = traduction()

    win = MirrorsWidget(None)
    win.show()
    app.exec()


if __name__ == "__main__":
    main()
