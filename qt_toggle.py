# qt_toggle.py

from PyQt6.QtCore import Qt, QRect, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QBrush, QPen
from PyQt6.QtWidgets import QCheckBox

class QToggle(QCheckBox):
    bg_color = pyqtProperty(
        QColor, lambda self: self._bg_color,
        lambda self, col: setattr(self, '_bg_color', col))
    circle_color = pyqtProperty(
        QColor, lambda self: self._circle_color,
        lambda self, col: setattr(self, '_circle_color', col))
    active_color = pyqtProperty(
        QColor, lambda self: self._active_color,
        lambda self, col: setattr(self, '_active_color', col))
    disabled_color = pyqtProperty(
        QColor, lambda self: self._disabled_color,
        lambda self, col: setattr(self, '_disabled_color', col))
    text_color = pyqtProperty(
        QColor, lambda self: self._text_color,
        lambda self, col: setattr(self, '_text_color', col))

    def __init__(self, parent=None):
        super().__init__(parent)
        self._bg_color, self._circle_color, self._active_color, \
            self._disabled_color, self._text_color = QColor("#494A4A"), \
            QColor("#FFFFFF"), QColor('#4CAF50'), QColor("#CCCCCC"), QColor("#FFFFFF")
        self._circle_pos, self._intermediate_bg_color = None, None
        self.setFixedHeight(18)
        self._animation_duration = 250  # milliseconds
        self.stateChanged.connect(self.start_transition)
        self._user_checked = False  # Flag for user-initiated changes

    circle_pos = pyqtProperty(
        float, lambda self: self._circle_pos,
        lambda self, pos: (setattr(self, '_circle_pos', pos), self.update()))
    intermediate_bg_color = pyqtProperty(
        QColor, lambda self: self._intermediate_bg_color,
        lambda self, col: setattr(self, '_intermediate_bg_color', col))

    def setDuration(self, duration: int):
        """Set the duration for the animation."""
        self._animation_duration = duration

    def update_pos_color(self, checked=None):
        """Update the position and color based on the checked state."""
        self._circle_pos = self.height() * (0.1 if checked else 0.1)
        self._intermediate_bg_color = self._active_color if self.isChecked() else self._bg_color

    def start_transition(self, state):
        """Start the transition animations based on the state."""
        if not self._user_checked:
            self.update_pos_color(state)
            return
        
        self.create_animation(state, b'circle_pos', self.height() * 0.1, self.height() * 0.9).start()
        self.create_animation(state, b'intermediate_bg_color', self._bg_color, self._active_color).start()
        
        self._user_checked = False

    def mousePressEvent(self, event):
        """Handle mouse press events."""
        self._user_checked = True
        super().mousePressEvent(event)

    def create_animation(self, state, prop, start_val, end_val):
        """Create an animation for a given property."""
        animation = QPropertyAnimation(self, prop, self)
        animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        animation.setDuration(self._animation_duration)
        animation.setStartValue(start_val if state else end_val)
        animation.setEndValue(end_val if state else start_val)
        return animation

    def showEvent(self, event):
        """Handle show events."""
        super().showEvent(event)
        self.update_pos_color(self.isChecked())

    def resizeEvent(self, event):
        """Handle resize events."""
        self.update_pos_color(self.isChecked())

    def sizeHint(self):
        """Provide a recommended size for the widget."""
        size = super().sizeHint()
        size.setWidth(self.height() * 2 + 20)  # Add extra space for circle and margin
        return size

    def hitButton(self, pos):
        """Check if the given position hits the button."""
        return self.contentsRect().contains(pos)

    def paintEvent(self, event):
        """Paint the widget."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        circle_color = QColor(
            self.disabled_color if not self.isEnabled() else self.circle_color)
        bg_color = QColor(
            self.disabled_color if not self.isEnabled() else self.intermediate_bg_color)
        text_color = QColor(
            self.disabled_color if not self.isEnabled() else self.text_color)

        height = self.height()
        width = self.width()
        togglewidth = height * 2
        circlesize = height * 0.8
        radius = height / 2
        circle_radius = circlesize / 2

        # Center the background rectangle
        bg_x = int((width - togglewidth) / 2)
        bg_y = int((height - height) / 2)  # This is just height, so bg_y should be 0

        # Draw the background
        bg_path = QPainterPath()
        bg_path.addRoundedRect(bg_x, bg_y, togglewidth, height, radius, radius)
        painter.fillPath(bg_path, QBrush(bg_color))

        # Calculate the circle's position
        if self.isChecked():
            circle_x = int(bg_x + togglewidth - circlesize)  # Move circle to the right
        else:
            circle_x = int(bg_x)  # Move circle to the left

        circle_y = int(bg_y + (height - circlesize) / 2)  # Center vertically

        # Draw the circle
        circle = QPainterPath()
        circle.addEllipse(circle_x, circle_y, circlesize, circlesize)
        painter.fillPath(circle, QBrush(circle_color))

        # Draw the text
        painter.setPen(QPen(QColor(text_color)))
        painter.setFont(self.font())
        text_width = QFontMetrics(self.font()).boundingRect(self.text()).width()
        text_rect_x = int(bg_x + togglewidth + 10)  # 10 is the margin between the toggle and text
        text_rect_width = int(width - text_rect_x - 10)  # Margin on the right side
        text_rect = QRect(text_rect_x, 0, text_rect_width, height)
        text_rect.adjust(0, (height - painter.fontMetrics().height()) // 2, 0, 0)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.text())
        painter.end()