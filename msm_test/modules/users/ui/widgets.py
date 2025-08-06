from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QImage, QPainter, QPalette, QPixmap, QBrush, QColor
from PySide6.QtWidgets import QApplication, QWidget, QLabel


class RoundIconLabel(QLabel):
    def __init__(self, parent, image_path: str, size: int = 64):
        super().__init__("", parent=parent)
        self.setMaximumSize(size + 2, size + 2)
        palette = QApplication.palette()
        color = palette.color(QPalette.ColorRole.Shadow)
        color = palette.color(QPalette.ColorRole.Highlight)
        # color = QColor("#666")
        color.setAlpha(150)

        self.setStyleSheet(f"""
            QLabel {{
            border-width: {2 if size > 32 else 1}px; border-color:{color.name(QColor.NameFormat.HexArgb)}; border-style: solid;
            border-radius: {size / 2}px; }}
            """)

        with open(image_path, "rb") as img:
            imgdata = img.read()
            pixmap = self._mask_image(imgdata, size=size)
            self.setPixmap(pixmap)

    @staticmethod
    def _mask_image(imgdata, imgtype="png", size=64):
        image = QImage.fromData(imgdata, imgtype)

        image.convertToFormat(QImage.Format_ARGB32)
        img_size = min(image.width(), image.height())
        rect = QRect(
            (image.width() - img_size) / 2,
            (image.height() - img_size) / 2,
            img_size,
            img_size,
        )

        image = image.copy(rect)

        out_img = QImage(img_size, img_size, QImage.Format_ARGB32)
        out_img.fill(Qt.transparent)

        painter = QPainter(out_img)
        painter.setBrush(QBrush(image))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, img_size, img_size)
        painter.end()

        # Convert the image to a pixmap and rescale it.
        pix_ratio = QWidget().devicePixelRatio()
        pixmap = QPixmap.fromImage(out_img)
        pixmap.setDevicePixelRatio(pix_ratio)
        size *= pix_ratio
        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        return pixmap