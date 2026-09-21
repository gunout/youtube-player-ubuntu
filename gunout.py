import sys
import re
import mpv
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QHBoxLayout, QLineEdit, QPushButton, QListWidget,
                              QListWidgetItem, QLabel, QFrame, QSlider)
from PyQt6.QtCore import (Qt, QTimer, QSize, QThread, pyqtSignal,
                          QPropertyAnimation, QEasingCurve)
from PyQt6.QtGui import (QFont, QColor, QIcon, QPixmap, QPainter, QPainterPath,
                         QPen, QCursor)
import yt_dlp


# ----- Palette épurée, sans bordures -----
BG          = "rgba(12, 12, 14, 240)"
SURFACE     = "rgba(255, 255, 255, 6)"
SURFACE_HOV = "rgba(255, 255, 255, 14)"
ACCENT      = "#00e5ff"
ACCENT_SOFT = "rgba(0, 229, 255, 22)"
TEXT        = "#f5f5f7"
TEXT_DIM    = "rgba(245, 245, 247, 100)"
TEXT_FAINT  = "rgba(245, 245, 247, 40)"
SIGNATURE   = "rgba(245, 245, 247, 30)"
CHEVRON     = "rgba(245, 245, 247, 150)"


STYLE = f"""
QMainWindow, QWidget#root {{
    background: {BG};
    border-radius: 14px;
    border: none;
}}

QLabel#title {{
    color: {TEXT};
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 6px;
    padding: 4px 6px;
}}

QLabel#signature {{
    color: {SIGNATURE};
    font-size: 9px;
    letter-spacing: 3px;
    padding: 0 8px 4px 8px;
}}

QLineEdit {{
    background: {SURFACE};
    color: {TEXT};
    border: none;
    border-radius: 18px;
    padding: 8px 18px;
    font-size: 13px;
    letter-spacing: 1px;
    selection-background-color: {ACCENT};
}}
QLineEdit:focus {{
    border: 1px solid {ACCENT};
    background: {SURFACE_HOV};
}}

QPushButton#go {{
    background: {ACCENT};
    color: #05070a;
    border: none;
    border-radius: 18px;
    padding: 8px 22px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
}}
QPushButton#go:hover  {{ background: #4df0ff; }}
QPushButton#go:pressed {{ background: #00b8cc; }}

QListWidget#overlay {{
    background: rgba(12, 12, 14, 220);
    color: {TEXT};
    border: none;
    border-radius: 14px;
    padding: 8px;
    font-size: 11px;
    letter-spacing: 1px;
    outline: none;
}}
QListWidget#overlay::item {{
    padding: 8px 12px;
    border-radius: 8px;
    margin: 1px 0;
}}
QListWidget#overlay::item:hover {{
    background: {SURFACE_HOV};
}}
QListWidget#overlay::item:selected {{
    background: {ACCENT_SOFT};
    color: {ACCENT};
}}

QFrame#videoCard {{
    background: #000;
    border: none;
    border-radius: 12px;
}}

QFrame#controls {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 rgba(0,0,0,0),
                stop:0.4 rgba(0,0,0,120),
                stop:1 rgba(0,0,0,180));
    border: none;
    border-bottom-left-radius: 12px;
    border-bottom-right-radius: 12px;
}}

QPushButton#ctrl {{
    background: transparent;
    border: none;
    border-radius: 17px;
    padding: 6px;
    min-width: 34px;
    min-height: 34px;
}}
QPushButton#ctrl:hover {{
    background: {SURFACE_HOV};
}}

QSlider::groove:horizontal {{
    height: 3px;
    background: rgba(255,255,255,12);
    border-radius: 2px;
}}
QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    background: #fff;
    width: 10px;
    height: 10px;
    margin: -4px 0;
    border-radius: 5px;
    border: none;
}}
QSlider::handle:horizontal:hover {{
    background: {ACCENT};
    width: 12px;
    height: 12px;
    margin: -5px 0;
    border-radius: 6px;
}}

QLabel#status {{
    color: {TEXT_DIM};
    font-size: 10px;
    letter-spacing: 2px;
    padding: 2px 6px;
}}

QLabel#time {{
    color: {TEXT_DIM};
    font-size: 11px;
    letter-spacing: 0.5px;
    min-width: 90px;
}}
"""


# ================= ICÔNES VECTORIELLES =================
def _make_icon(kind, size=18, color="#f5f5f7"):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color))
    pen.setWidthF(1.4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(QColor(color))
    s = size

    if kind == "play":
        path = QPainterPath()
        path.moveTo(s*0.32, s*0.24)
        path.lineTo(s*0.76, s*0.50)
        path.lineTo(s*0.32, s*0.76)
        path.closeSubpath()
        p.drawPath(path)
    elif kind == "pause":
        p.drawRoundedRect(int(s*0.32), int(s*0.24), int(s*0.12), int(s*0.52), 2, 2)
        p.drawRoundedRect(int(s*0.56), int(s*0.24), int(s*0.12), int(s*0.52), 2, 2)
    elif kind == "stop":
        p.drawRoundedRect(int(s*0.32), int(s*0.32), int(s*0.36), int(s*0.36), 3, 3)
    elif kind == "volume":
        path = QPainterPath()
        path.moveTo(s*0.20, s*0.42)
        path.lineTo(s*0.34, s*0.42)
        path.lineTo(s*0.48, s*0.28)
        path.lineTo(s*0.48, s*0.72)
        path.lineTo(s*0.34, s*0.58)
        path.lineTo(s*0.20, s*0.58)
        path.closeSubpath()
        p.drawPath(path)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawArc(int(s*0.44), int(s*0.34), int(s*0.24), int(s*0.32), -50*16, 100*16)
    elif kind == "mute":
        path = QPainterPath()
        path.moveTo(s*0.20, s*0.42)
        path.lineTo(s*0.34, s*0.42)
        path.lineTo(s*0.48, s*0.28)
        path.lineTo(s*0.48, s*0.72)
        path.lineTo(s*0.34, s*0.58)
        path.lineTo(s*0.20, s*0.58)
        path.closeSubpath()
        p.drawPath(path)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(int(s*0.60), int(s*0.38), int(s*0.80), int(s*0.62))
        p.drawLine(int(s*0.80), int(s*0.38), int(s*0.60), int(s*0.62))
    elif kind == "fullscreen":
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(int(s*0.22), int(s*0.36), int(s*0.22), int(s*0.22))
        p.drawLine(int(s*0.22), int(s*0.22), int(s*0.36), int(s*0.22))
        p.drawLine(int(s*0.64), int(s*0.22), int(s*0.78), int(s*0.22))
        p.drawLine(int(s*0.78), int(s*0.22), int(s*0.78), int(s*0.36))
        p.drawLine(int(s*0.78), int(s*0.64), int(s*0.78), int(s*0.78))
        p.drawLine(int(s*0.78), int(s*0.78), int(s*0.64), int(s*0.78))
        p.drawLine(int(s*0.36), int(s*0.78), int(s*0.22), int(s*0.78))
        p.drawLine(int(s*0.22), int(s*0.78), int(s*0.22), int(s*0.64))
    elif kind == "close":
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(int(s*0.30), int(s*0.30), int(s*0.70), int(s*0.70))
        p.drawLine(int(s*0.70), int(s*0.30), int(s*0.30), int(s*0.70))
    elif kind == "min":
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(int(s*0.28), int(s*0.52), int(s*0.72), int(s*0.52))
    elif kind == "chevron-down":
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(int(s*0.30), int(s*0.42), int(s*0.50), int(s*0.62))
        p.drawLine(int(s*0.50), int(s*0.62), int(s*0.70), int(s*0.42))
    elif kind == "chevron-up":
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawLine(int(s*0.30), int(s*0.58), int(s*0.50), int(s*0.38))
        p.drawLine(int(s*0.50), int(s*0.38), int(s*0.70), int(s*0.58))

    p.end()
    return QIcon(pm)


def fmt_time(sec):
    if sec is None or sec < 0:
        return "00:00"
    sec = int(sec)
    h, r = divmod(sec, 3600)
    m, s = divmod(r, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ================= WORKER DE RECHERCHE =================
class SearchWorker(QThread):
    done = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, query):
        super().__init__()
        self.query = query

    def run(self):
        opts = {'quiet': True, 'extract_flat': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f'ytsearch15:{self.query}', download=False)
                results = []
                for e in info.get('entries', []):
                    title = (e.get('title') or 'SANS TITRE').upper()
                    url = e.get('url') or e.get('id') or ''
                    results.append((title, url))
                self.done.emit(results)
        except Exception as ex:
            self.error.emit(str(ex))


class Gunout(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUNOUT")
        self.resize(1100, 780)
        self.setMinimumSize(640, 480)
        self.player = None
        self.worker = None
        self._seeking = False
        self._drag_pos = None
        self._resize_edge = None
        self._resize_margin = 8
        self._controls_collapsed = False
        self._controls_full_height = 0
        self._auto_hide_enabled = True
        self._window_folded = False
        self._unfolded_height = 780
        self.setMouseTracking(True)
        self.setStyleSheet(STYLE)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)

        root = QWidget()
        root.setObjectName("root")
        self.setCentralWidget(root)

        self.main_layout = QVBoxLayout(root)
        layout = self.main_layout
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(8)

        # --- Barre HUD ---
        top = QHBoxLayout()
        top.setSpacing(10)

        title = QLabel("GUNOUT")
        title.setObjectName("title")
        top.addWidget(title)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Rechercher ou coller un lien...")
        self.input.returnPressed.connect(self.search)
        top.addWidget(self.input, stretch=1)

        btn = QPushButton("GO")
        btn.setObjectName("go")
        btn.clicked.connect(self.search)
        top.addWidget(btn)

        btn_min = QPushButton()
        btn_min.setObjectName("ctrl")
        btn_min.setIcon(_make_icon("min", 16, TEXT))
        btn_min.setIconSize(QSize(16, 16))
        btn_min.clicked.connect(self.showMinimized)
        top.addWidget(btn_min)

        btn_close = QPushButton()
        btn_close.setObjectName("ctrl")
        btn_close.setIcon(_make_icon("close", 16, TEXT))
        btn_close.setIconSize(QSize(16, 16))
        btn_close.clicked.connect(self.close)
        top.addWidget(btn_close)

        self.btn_fold = QPushButton()
        self.btn_fold.setObjectName("ctrl")
        self.btn_fold.setIcon(_make_icon("chevron-up", 16, CHEVRON))
        self.btn_fold.setIconSize(QSize(16, 16))
        self.btn_fold.setToolTip("Replier la fenêtre")
        self.btn_fold.clicked.connect(self.toggle_window_fold)
        top.addWidget(self.btn_fold)

        layout.addLayout(top)

        # --- Signature ---
        self.signature = QLabel("by gleaphe")
        self.signature.setObjectName("signature")
        layout.addWidget(self.signature)

        # --- Carte vidéo ---
        self.video_card = QFrame()
        self.video_card.setObjectName("videoCard")
        v_layout = QVBoxLayout(self.video_card)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(0)

        self.video_widget = QWidget()
        self.video_widget.setAttribute(Qt.WidgetAttribute.WA_NativeWindow, True)
        v_layout.addWidget(self.video_widget, stretch=1)

        # Overlay résultats
        self.results = QListWidget(self.video_card)
        self.results.setObjectName("overlay")
        self.results.itemActivated.connect(self.play)
        self.results.itemDoubleClicked.connect(self.play)
        self.results.hide()

        # --- Barre de contrôles ---
        self.controls = QFrame()
        self.controls.setObjectName("controls")
        controls = self.controls
        c_layout = QVBoxLayout(controls)
        c_layout.setContentsMargins(18, 8, 18, 12)
        c_layout.setSpacing(4)

        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setRange(0, 1000)
        self.seek.sliderPressed.connect(self._seek_start)
        self.seek.sliderReleased.connect(self._seek_end)
        c_layout.addWidget(self.seek)

        row = QHBoxLayout()
        row.setSpacing(4)

        self.btn_play = QPushButton()
        self.btn_play.setObjectName("ctrl")
        self.btn_play.setIcon(_make_icon("pause", 18, TEXT))
        self.btn_play.setIconSize(QSize(18, 18))
        self.btn_play.clicked.connect(self.toggle_pause)
        row.addWidget(self.btn_play)

        self.btn_stop = QPushButton()
        self.btn_stop.setObjectName("ctrl")
        self.btn_stop.setIcon(_make_icon("stop", 14, TEXT))
        self.btn_stop.setIconSize(QSize(14, 14))
        self.btn_stop.clicked.connect(self._stop)
        row.addWidget(self.btn_stop)

        self.time_lbl = QLabel("00:00 / 00:00")
        self.time_lbl.setObjectName("time")
        row.addWidget(self.time_lbl)

        row.addStretch()

        self.btn_mute = QPushButton()
        self.btn_mute.setObjectName("ctrl")
        self.btn_mute.setIcon(_make_icon("volume", 16, TEXT))
        self.btn_mute.setIconSize(QSize(16, 16))
        self.btn_mute.clicked.connect(self.toggle_mute)
        row.addWidget(self.btn_mute)

        self.vol = QSlider(Qt.Orientation.Horizontal)
        self.vol.setRange(0, 100)
        self.vol.setValue(100)
        self.vol.setFixedWidth(90)
        self.vol.valueChanged.connect(self.set_volume)
        row.addWidget(self.vol)

        self.btn_fs = QPushButton()
        self.btn_fs.setObjectName("ctrl")
        self.btn_fs.setIcon(_make_icon("fullscreen", 14, TEXT))
        self.btn_fs.setIconSize(QSize(14, 14))
        self.btn_fs.clicked.connect(self.toggle_fullscreen)
        row.addWidget(self.btn_fs)

        self.btn_toggle = QPushButton()
        self.btn_toggle.setObjectName("ctrl")
        self.btn_toggle.setIcon(_make_icon("chevron-down", 14, CHEVRON))
        self.btn_toggle.setIconSize(QSize(14, 14))
        self.btn_toggle.setToolTip("Replier les contrôles")
        self.btn_toggle.clicked.connect(self.toggle_controls)
        row.addWidget(self.btn_toggle)

        c_layout.addLayout(row)
        v_layout.addWidget(controls)

        # --- Bouton flottant pour rouvrir les contrôles ---
        self.btn_reopen = QPushButton(self.video_card)
        self.btn_reopen.setObjectName("ctrl")
        self.btn_reopen.setIcon(_make_icon("chevron-up", 16, CHEVRON))
        self.btn_reopen.setIconSize(QSize(16, 16))
        self.btn_reopen.setToolTip("Déplier les contrôles")
        self.btn_reopen.setFixedSize(36, 36)
        self.btn_reopen.setStyleSheet(f"""
            QPushButton {{
                background: rgba(12, 12, 14, 180);
                border: none;
                border-radius: 18px;
            }}
            QPushButton:hover {{
                background: rgba(0, 229, 255, 40);
            }}
        """)
        self.btn_reopen.clicked.connect(self.toggle_controls)
        self.btn_reopen.hide()

        layout.addWidget(self.video_card, stretch=1)

        self.status = QLabel("PRÊT")
        self.status.setObjectName("status")
        layout.addWidget(self.status)

        # --- Timer seek ---
        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self._update_seek)
        self.timer.start()

        # --- Timer auto-hide des contrôles ---
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.setInterval(3000)
        self.hide_timer.timeout.connect(self._auto_hide_controls)

    # ===== Replis de la fenêtre =====
    def toggle_window_fold(self):
        if self._window_folded:
            # Déplier
            self.video_card.show()
            self.signature.show()
            self.status.show()
            target_h = self._unfolded_height
            self.btn_fold.setIcon(_make_icon("chevron-up", 16, CHEVRON))
            self.btn_fold.setToolTip("Replier la fenêtre")
            self._window_folded = False
            self.setMinimumSize(640, 480)
        else:
            # Replier
            self._unfolded_height = self.height()
            self.video_card.hide()
            self.signature.hide()
            self.status.hide()
            target_h = self._folded_height()
            self.btn_fold.setIcon(_make_icon("chevron-down", 16, CHEVRON))
            self.btn_fold.setToolTip("Déplier la fenêtre")
            self._window_folded = True
            self.setMinimumSize(400, target_h)

        self.anim_fold = QPropertyAnimation(self, b"size")
        self.anim_fold.setDuration(260)
        self.anim_fold.setStartValue(self.size())
        self.anim_fold.setEndValue(QSize(self.width(), target_h))
        self.anim_fold.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim_fold.start()

    def _folded_height(self):
        # Hauteur : marges + barre HUD (environ 50px) + un peu d'air
        return 90

    # ===== Auto-hide =====
    def _reset_auto_hide(self):
        if not self._auto_hide_enabled:
            return
        if self._controls_collapsed:
            return
        if self._window_folded:
            return
        self.hide_timer.start()

    def _auto_hide_controls(self):
        if self._controls_collapsed:
            return
        if self._window_folded:
            return
        if self.controls.underMouse() or self.btn_reopen.underMouse():
            self.hide_timer.start()
            return
        self._controls_collapsed = True
        self._controls_full_height = self.controls.height()
        self.btn_toggle.setIcon(_make_icon("chevron-up", 14, CHEVRON))
        self.btn_reopen.show()
        self.btn_reopen.raise_()
        self._place_reopen_button()

        self.anim = QPropertyAnimation(self.controls, b"maximumHeight")
        self.anim.setDuration(220)
        self.anim.setStartValue(self.controls.height())
        self.anim.setEndValue(0)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.start()

    # ===== Replis manuel des contrôles =====
    def toggle_controls(self):
        if self._controls_collapsed:
            target = self._controls_full_height or 80
            self.btn_toggle.setIcon(_make_icon("chevron-down", 14, CHEVRON))
            self.btn_toggle.setToolTip("Replier les contrôles")
            self._controls_collapsed = False
            self.btn_reopen.hide()
        else:
            self._controls_full_height = self.controls.height()
            target = 0
            self.btn_toggle.setIcon(_make_icon("chevron-up", 14, CHEVRON))
            self.btn_toggle.setToolTip("Déplier les contrôles")
            self._controls_collapsed = True
            self.btn_reopen.show()
            self.btn_reopen.raise_()
            self._place_reopen_button()

        self.anim = QPropertyAnimation(self.controls, b"maximumHeight")
        self.anim.setDuration(220)
        self.anim.setStartValue(self.controls.height())
        self.anim.setEndValue(target)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.anim.start()

        if not self._controls_collapsed:
            self._reset_auto_hide()

    def _place_reopen_button(self):
        w = self.video_card.width()
        h = self.video_card.height()
        self.btn_reopen.move(w - 56, h - 56)

    # ===== Resize & drag =====
    def _edge_at(self, pos):
        if self._window_folded:
            return None
        m = self._resize_margin
        r = self.rect()
        x, y = pos.x(), pos.y()
        left, right = x <= m, x >= r.width() - m
        top, bottom = y <= m, y >= r.height() - m
        if top and left:     return "NW"
        if top and right:    return "NE"
        if bottom and left:  return "SW"
        if bottom and right: return "SE"
        if left:             return "W"
        if right:            return "E"
        if top:              return "N"
        if bottom:           return "S"
        return None

    def _cursor_for_edge(self, edge):
        return {
            "N": Qt.CursorShape.SizeVerCursor, "S": Qt.CursorShape.SizeVerCursor,
            "E": Qt.CursorShape.SizeHorCursor, "W": Qt.CursorShape.SizeHorCursor,
            "NE": Qt.CursorShape.SizeBDiagCursor, "SW": Qt.CursorShape.SizeBDiagCursor,
            "NW": Qt.CursorShape.SizeFDiagCursor, "SE": Qt.CursorShape.SizeFDiagCursor,
        }.get(edge, Qt.CursorShape.ArrowCursor)

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            edge = self._edge_at(e.position().toPoint())
            if edge:
                self._resize_edge = edge
                self._resize_start_geo = self.geometry()
                self._resize_start_pos = e.globalPosition().toPoint()
                return
            self._drag_pos = e.globalPosition().toPoint()

    def mouseMoveEvent(self, e):
        pos = e.position().toPoint()
        if self._resize_edge and (e.buttons() & Qt.MouseButton.LeftButton):
            delta = e.globalPosition().toPoint() - self._resize_start_pos
            g = self._resize_start_geo
            x, y, w, h = g.x(), g.y(), g.width(), g.height()
            edge = self._resize_edge
            min_w, min_h = self.minimumWidth(), self.minimumHeight()
            if "E" in edge: w = max(min_w, g.width() + delta.x())
            if "S" in edge: h = max(min_h, g.height() + delta.y())
            if "W" in edge:
                new_w = max(min_w, g.width() - delta.x())
                x = g.x() + (g.width() - new_w); w = new_w
            if "N" in edge:
                new_h = max(min_h, g.height() - delta.y())
                y = g.y() + (g.height() - new_h); h = new_h
            self.setGeometry(x, y, w, h)
            return
        edge = self._edge_at(pos)
        self.setCursor(QCursor(self._cursor_for_edge(edge)))
        if self._drag_pos is not None:
            delta = e.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = e.globalPosition().toPoint()

        self._reset_auto_hide()

    def mouseReleaseEvent(self, e):
        self._resize_edge = None
        self._drag_pos = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._place_overlay()
        if self.btn_reopen.isVisible():
            self._place_reopen_button()

    def _place_overlay(self):
        if self.results.isVisible():
            w = self.video_card.width()
            h = self.video_card.height()
            ow = min(680, max(200, w - 80))
            oh = min(380, max(150, h - 120))
            self.results.setGeometry((w - ow)//2, 70, ow, oh)
            self.results.raise_()

    # ===== mpv =====
    def showEvent(self, event):
        super().showEvent(event)
        if self.player is None:
            wid = int(self.video_widget.winId())
            self.player = mpv.MPV(
                wid=wid,
                vo='gpu',
                hwdec='auto-safe',
                osc=False,
                input_default_bindings=False,
                input_vo_keyboard=False,
                ytdl=True,
                ytdl_format='bestvideo+bestaudio/best',
                cache=True,
                demuxer_max_bytes='50M',
                demuxer_max_back_bytes='20M',
            )
        self._reset_auto_hide()

    # ===== Recherche / lecture =====
    def search(self):
        q = self.input.text().strip()
        if not q:
            return

        if re.search(r'(youtube\.com|youtu\.be)/', q):
            self.status.setText("LECTURE DIRECTE")
            self.results.hide()
            if self.player is None:
                self.status.setText("LECTEUR NON PRÊT")
                return
            try:
                self.player.play(q)
                self.btn_play.setIcon(_make_icon("pause", 18, TEXT))
            except Exception as ex:
                self.status.setText(f"ERREUR : {ex}")
            return

        self.status.setText(f"RECHERCHE : {q.upper()}")
        self.results.clear()
        self.results.show()
        self.results.raise_()
        self._place_overlay()

        self.worker = SearchWorker(q)
        self.worker.done.connect(self._on_search_done)
        self.worker.error.connect(lambda e: self.status.setText(f"ERREUR : {e}"))
        self.worker.start()

    def _on_search_done(self, results):
        self.results.clear()
        for title, url in results:
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.results.addItem(item)
        self.results.show()
        self.results.raise_()
        self._place_overlay()
        self.status.setText(f"{len(results)} RÉSULTATS")

    def play(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if not url:
            return
        if not url.startswith('http'):
            url = f"https://www.youtube.com/watch?v={url}"
        self.status.setText("LECTURE")
        self.results.hide()
        try:
            self.player.play(url)
            self.btn_play.setIcon(_make_icon("pause", 18, TEXT))
        except Exception as ex:
            self.status.setText(f"ERREUR : {ex}")

    # ===== Contrôles =====
    def toggle_pause(self):
        if not self.player: return
        self.player.pause = not self.player.pause
        self.btn_play.setIcon(_make_icon("play" if self.player.pause else "pause", 18, TEXT))

    def toggle_mute(self):
        if not self.player: return
        self.player.mute = not self.player.mute
        self.btn_mute.setIcon(_make_icon("mute" if self.player.mute else "volume", 16, TEXT))

    def set_volume(self, v):
        if self.player: self.player.volume = v

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _stop(self):
        if self.player:
            self.player.command('stop')
        self.btn_play.setIcon(_make_icon("play", 18, TEXT))

    def _seek_start(self): self._seeking = True

    def _seek_end(self):
        if self.player:
            dur = self.player.duration or 0
            self.player.command('seek', (self.seek.value()/1000.0)*dur, 'absolute')
        self._seeking = False

    def _update_seek(self):
        if not self.player or self._seeking: return
        try:
            dur = self.player.duration or 0
            pos = self.player.time_pos or 0
            if dur > 0:
                self.seek.setValue(int((pos/dur)*1000))
            self.time_lbl.setText(f"{fmt_time(pos)} / {fmt_time(dur)}")
        except Exception:
            pass

    def closeEvent(self, event):
        if self.player is not None:
            try: self.player.terminate()
            except Exception: pass
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Inter", 10))
    w = Gunout()
    w.show()
    sys.exit(app.exec())
