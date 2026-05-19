import sys
import math
import struct
import psutil
from queue import Empty
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, 
    QVBoxLayout, QTextEdit, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from gui.gemini_status import build_gemini_live_status, CHECKING_COLOR

# --- Colors ---
PRIMARY_COLOR = QColor("#00FFFF")  # Cyan
ACCENT_COLOR = QColor("#FFFFFF")   # White
BG_COLOR = QColor("#000000")       # Black
WARNING_COLOR = QColor("#FFA500")  # Orange (for Pause)


class GeminiLiveStatusThread(QThread):
    status_signal = pyqtSignal(dict)

    def run(self):
        try:
            from gemini_client import validate_runtime

            startup_error = validate_runtime()
        except Exception as exc:
            startup_error = f"Gemini Live is unavailable: status check failed: {exc}"

        self.status_signal.emit(build_gemini_live_status(startup_error))

# --- Mic Monitor Thread ---
class AudioMonitorThread(QThread):
    mic_level_signal = pyqtSignal(float)
    
    def __init__(self):
        super().__init__()
        self.running = True
        
    def run(self):
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                            input=True, frames_per_buffer=1024)
        except Exception as e:
            print(f"[GUI] Audio monitor failed to start: {e}")
            return
            
        while self.running:
            try:
                data = stream.read(1024, exception_on_overflow=False)
                count = len(data) // 2
                format_str = f"{count}h"
                shorts = struct.unpack(format_str, data)
                sum_squares = sum(s * s for s in shorts)
                rms = math.sqrt(sum_squares / count) if count > 0 else 0
                
                # Normalize 0.0 to 1.0
                normalized = min(1.0, rms / 3000.0)
                self.mic_level_signal.emit(normalized)
            except Exception:
                pass
            
            self.msleep(20)
            
        stream.stop_stream()
        stream.close()
        p.terminate()

class HexagonPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        self.opacity = 50
        self.increasing = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(100)
        
        # We can add a label here
        layout = QVBoxLayout(self)
        self.title = QLabel("PROCESS MONITOR")
        self.title.setStyleSheet("color: #00FFFF; font-family: 'Courier New'; font-weight: bold;")
        self.title.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.title)

    def animate(self):
        if self.increasing:
            self.opacity += 5
            if self.opacity >= 200: self.increasing = False
        else:
            self.opacity -= 5
            if self.opacity <= 50: self.increasing = True
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        size = 25
        rows = 6
        cols = 3
        x_offset = 20
        y_offset = 50

        for r in range(rows):
            for c in range(cols):
                color = QColor(PRIMARY_COLOR)
                current_opacity = self.opacity
                if (r + c) % 2 == 0:
                   current_opacity = max(30, current_opacity - 50)
                
                color.setAlpha(current_opacity)
                painter.setPen(QPen(color, 2))
                
                x = x_offset + c * (size * 1.5)
                y = y_offset + r * (size * math.sqrt(3))
                if c % 2 == 1:
                    y += size * math.sqrt(3) / 2
                
                self.draw_hexagon(painter, x, y, size)

    def draw_hexagon(self, painter, x, y, size):
        points = []
        for i in range(6):
            angle_rad = math.radians(60 * i)
            px = x + size * math.cos(angle_rad)
            py = y + size * math.sin(angle_rad)
            points.append(QPointF(px, py))
        painter.drawPolygon(QPolygonF(points))

class TelemetryPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumWidth(250)
        self.cpu = 0
        self.ram = 0
        self.disk = 0
        self.mic = 0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(500)

    def update_telemetry(self):
        self.cpu = psutil.cpu_percent()
        self.ram = psutil.virtual_memory().percent
        self.disk = psutil.disk_usage('/').percent
        self.update()
        
    def set_mic_level(self, level):
        self.mic = level * 100
        # Telemetry updates every 500ms, but mic updates faster. 
        # We can just let paintEvent handle it.
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw Labels and Bars
        labels = ["CPU", "RAM", "DSK", "MIC"]
        values = [self.cpu, self.ram, self.disk, self.mic]
        
        bar_width = 25
        gap = 20
        start_x = 30
        base_y = 220
        max_h = 150
        
        painter.setFont(QFont("Courier New", 10, QFont.Weight.Bold))
        
        for i in range(4):
            x = start_x + i * (bar_width + gap)
            val = values[i]
            
            # Label
            painter.setPen(PRIMARY_COLOR)
            painter.drawText(int(x), int(base_y + 20), labels[i])
            painter.drawText(int(x), int(base_y + 40), f"{int(val)}%")
            
            # Background Track
            painter.setBrush(QBrush(QColor(10, 10, 10, 200)))
            painter.setPen(QPen(PRIMARY_COLOR, 1))
            painter.drawRect(QRectF(x, base_y - max_h, bar_width, max_h))
            
            # Active Bar
            h = (val / 100.0) * max_h
            if val > 85:
                color = QColor("#FF3333") # Red critical
            elif val > 60:
                color = WARNING_COLOR # Orange
            else:
                color = PRIMARY_COLOR
                
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(QRectF(x + 1, base_y - h, bar_width - 2, h))

class CentralReactor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle_outer = 0
        self.angle_inner = 0
        self.is_paused = False
        self.mic_level = 0.0
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def set_mic_level(self, level):
        self.mic_level = level

    def animate(self):
        if not self.is_paused:
            # Spin faster when talking
            speed_boost = 1 + (self.mic_level * 5)
            self.angle_outer = (self.angle_outer + 2 * speed_boost) % 360
            self.angle_inner = (self.angle_inner - 4 * speed_boost) % 360
        self.update()

    def set_paused(self, paused):
        self.is_paused = paused
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        main_color = WARNING_COLOR if self.is_paused else PRIMARY_COLOR
        
        # 1. Draw Core (Solid Circle)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(main_color))
        core_radius = 25
        
        if not self.is_paused:
             pulse = (math.sin(self.angle_outer * 0.1) + 1) * 5
             mic_boost = self.mic_level * 40 # Expand heavily on voice
             total_radius = core_radius + pulse + mic_boost
             painter.drawEllipse(QPointF(center_x, center_y), total_radius, total_radius)
        else:
             painter.drawEllipse(QPointF(center_x, center_y), core_radius, core_radius)

        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 2. Middle Ring (Thick Segmented)
        pen = QPen(main_color)
        pen.setWidth(12)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        pen.setDashPattern([10, 10]) 
        painter.setPen(pen)
        
        radius_mid = 110
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle_outer)
        painter.drawEllipse(QPointF(0, 0), radius_mid, radius_mid)
        painter.restore()

        # 3. Inner Ring (Thin Dashed)
        pen = QPen(ACCENT_COLOR)
        pen.setWidth(4)
        pen.setDashPattern([5, 5])
        painter.setPen(pen)
        
        radius_inner = 80
        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.angle_inner)
        painter.drawEllipse(QPointF(0, 0), radius_inner, radius_inner)
        painter.restore()

        # 4. Outer Bracket (Semi-circles)
        pen = QPen(main_color)
        pen.setWidth(3)
        pen.setStyle(Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        radius_outer = 140
        
        rect_outer = QRectF(center_x - radius_outer, center_y - radius_outer, 2*radius_outer, 2*radius_outer)
        painter.drawArc(rect_outer, 45 * 16, 90 * 16)
        painter.drawArc(rect_outer, 225 * 16, 90 * 16)


class JarvisGUI(QMainWindow):
    def __init__(self, pause_event, command_queue=None, log_queue=None):
        super().__init__()
        self.pause_event = pause_event
        self.command_queue = command_queue
        self.log_queue = log_queue
        self.is_paused = False
        
        self.setWindowTitle("JARVIS PROTOCOL v2.0")
        self.resize(1100, 750)
        
        # Styling
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background-color: #050505;")
        
        # Main Layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("JARVIS PROTOCOL v2.0 :: SECURE LINK ACTIVE")
        header.setStyleSheet("color: #00FFFF; font-family: 'Courier New'; font-size: 16px; font-weight: bold;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header)

        self.gemini_status_label = QLabel("GEMINI LIVE: CHECKING...")
        self.gemini_status_label.setStyleSheet(
            f"color: {CHECKING_COLOR}; font-family: 'Courier New'; font-size: 12px; font-weight: bold;"
        )
        self.gemini_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.gemini_status_label)
        
        # Top HUD row
        hud_layout = QHBoxLayout()
        self.left_panel = HexagonPanel()
        self.reactor = CentralReactor()
        self.right_panel = TelemetryPanel()
        
        hud_layout.addWidget(self.left_panel)
        hud_layout.addWidget(self.reactor, stretch=2)
        hud_layout.addWidget(self.right_panel)
        main_layout.addLayout(hud_layout, stretch=3)
        
        # Bottom Terminal Console
        self.terminal = QTextEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            QTextEdit {
                background-color: rgba(10, 15, 15, 200);
                color: #00FFCC;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                border: 1px solid #005555;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.terminal.append("[SYS] Protocol Initialized. Brain connected.")
        main_layout.addWidget(self.terminal, stretch=1)
        
        # Bottom Command Input
        self.input_bar = QLineEdit()
        self.input_bar.setPlaceholderText("Enter command to JARVIS... (Press Enter to execute)")
        self.input_bar.setStyleSheet("""
            QLineEdit {
                background-color: rgba(20, 25, 25, 220);
                color: #FFFFFF;
                font-family: 'Courier New', monospace;
                font-size: 15px;
                border: 1px solid #00FFFF;
                border-radius: 5px;
                padding: 8px;
            }
            QLineEdit:focus {
                border: 2px solid #00FFFF;
                background-color: rgba(30, 35, 35, 240);
            }
        """)
        self.input_bar.returnPressed.connect(self.submit_command)
        main_layout.addWidget(self.input_bar)
        
        # Setup Mic Monitor
        self.mic_thread = AudioMonitorThread()
        self.mic_thread.mic_level_signal.connect(self.reactor.set_mic_level)
        self.mic_thread.mic_level_signal.connect(self.right_panel.set_mic_level)
        self.mic_thread.start()

        self.last_gemini_status_detail = None
        self.gemini_status_thread = None
        self.refresh_gemini_live_status()

        self.gemini_status_timer = QTimer(self)
        self.gemini_status_timer.timeout.connect(self.refresh_gemini_live_status)
        self.gemini_status_timer.start(30000)
        
        # Setup Log Polling
        if self.log_queue:
            self.log_timer = QTimer(self)
            self.log_timer.timeout.connect(self.poll_logs)
            self.log_timer.start(100)

    def refresh_gemini_live_status(self):
        if self.gemini_status_thread and self.gemini_status_thread.isRunning():
            return

        self.gemini_status_label.setText("GEMINI LIVE: CHECKING...")
        self.gemini_status_label.setStyleSheet(
            f"color: {CHECKING_COLOR}; font-family: 'Courier New'; font-size: 12px; font-weight: bold;"
        )

        self.gemini_status_thread = GeminiLiveStatusThread(self)
        self.gemini_status_thread.status_signal.connect(self.apply_gemini_live_status)
        self.gemini_status_thread.start()

    def apply_gemini_live_status(self, status):
        self.gemini_status_label.setText(status["label"])
        self.gemini_status_label.setStyleSheet(
            f"color: {status['color']}; font-family: 'Courier New'; font-size: 12px; font-weight: bold;"
        )
        self.gemini_status_label.setToolTip(status["detail"])

        if status["detail"] != self.last_gemini_status_detail:
            prefix = "#00FFFF" if "READY" in status["label"] else "#FFA500"
            self.terminal.append(f"<span style='color: {prefix};'>[SYS]</span> {status['detail']}")
            self.last_gemini_status_detail = status["detail"]

    def submit_command(self):
        text = self.input_bar.text().strip()
        if text and self.command_queue:
            self.terminal.append(f"<span style='color: white;'>[USER]</span> {text}")
            self.command_queue.put(text)
            self.input_bar.clear()

    def poll_logs(self):
        if not self.log_queue: return
        while True:
            try:
                log_msg = self.log_queue.get_nowait()
                self.terminal.append(log_msg)
                
                # Auto-scroll to bottom
                scrollbar = self.terminal.verticalScrollBar()
                scrollbar.setValue(scrollbar.maximum())
            except Empty:
                break

    def mousePressEvent(self, event):
        if self._clicked_reactor(event):
            self.toggle_pause()

    def _clicked_reactor(self, event):
        if hasattr(event, "position"):
            point = event.position().toPoint()
        else:
            point = event.pos()
        return self.childAt(point) is self.reactor
        
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.reactor.set_paused(self.is_paused)
        
        if self.is_paused:
            self.pause_event.set()
            self.terminal.append("<span style='color: #FFA500;'>[SYS] Voice Recognition PAUSED. Text mode active.</span>")
        else:
            self.pause_event.clear()
            self.terminal.append("<span style='color: #00FFFF;'>[SYS] Voice Recognition RESUMED.</span>")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

    def closeEvent(self, event):
        self.mic_thread.running = False
        self.mic_thread.wait()
        super().closeEvent(event)

def run_gui(context):
    app = QApplication(sys.argv)
    pause_event = context.get("pause_event")
    command_queue = context.get("command_queue")
    log_queue = context.get("log_queue")
    
    window = JarvisGUI(pause_event, command_queue, log_queue)
    window.show()
    sys.exit(app.exec())
