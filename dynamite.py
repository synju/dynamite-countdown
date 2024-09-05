import os
import sys
import pygame
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMenu, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QFont


class CustomTimeDialog(QDialog):
    """Dialog for entering custom countdown time."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Set Custom Time")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)  # Remove the question mark icon
        self.setFixedSize(300, 220)  # Increased size slightly to account for padding

        # Layout for the custom time input
        layout = QVBoxLayout()

        # Hours input
        self.hours_input = QLineEdit(self)
        self.hours_input.setPlaceholderText("Hours")
        self.hours_input.setFixedHeight(30)  # Increased height
        layout.addWidget(QLabel("Hours:"))
        layout.addWidget(self.hours_input)

        # Minutes input
        self.minutes_input = QLineEdit(self)
        self.minutes_input.setPlaceholderText("Minutes")
        self.minutes_input.setFixedHeight(30)  # Increased height
        layout.addWidget(QLabel("Minutes:"))
        layout.addWidget(self.minutes_input)

        # Seconds input
        self.seconds_input = QLineEdit(self)
        self.seconds_input.setPlaceholderText("Seconds")
        self.seconds_input.setFixedHeight(30)  # Increased height
        layout.addWidget(QLabel("Seconds:"))
        layout.addWidget(self.seconds_input)

        # Spacer to add padding at the bottom
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Set & Start Button
        button_layout = QHBoxLayout()
        set_start_button = QPushButton("Set & Start", self)
        set_start_button.setFixedHeight(40)  # Increased button height
        set_start_button.clicked.connect(self.set_and_start)
        button_layout.addWidget(set_start_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.selected_time = None

    def set_and_start(self):
        """Gather user input and close the dialog with custom time."""
        try:
            hours = int(self.hours_input.text()) if self.hours_input.text() else 0
            minutes = int(self.minutes_input.text()) if self.minutes_input.text() else 0
            seconds = int(self.seconds_input.text()) if self.seconds_input.text() else 0
            self.selected_time = hours * 3600 + minutes * 60 + seconds
        except ValueError:
            # If invalid input, reset to None
            self.selected_time = None
        self.accept()  # Close the dialog


class CountdownWidget(QWidget):
    def __init__(self, image_path, beep_sound_path, explosion_sound_path, font_name="Arial", font_size=48, font_color="red", text_position=(100, 100)):
        super().__init__()

        self.image_path = image_path
        self.font_name = font_name
        self.font_size = font_size
        self.font_color = font_color
        self.text_position = text_position
        self.beep_sound_path = beep_sound_path
        self.explosion_sound_path = explosion_sound_path
        self.is_muted = False  # Variable to track mute status
        self.is_blinking = False  # Track whether blinking mode is active
        self.is_visible = True  # Track whether text is visible for blinking
        self.is_paused = False  # Variable to track if the countdown is paused

        # Default time set to 1 hour (3600 seconds)
        self.reset_time = 3600
        self.remaining_seconds = self.reset_time

        # Initialize pygame for sound playback
        pygame.mixer.init()

        # Load the beep and explosion sounds
        self.beep_sound = pygame.mixer.Sound(self.beep_sound_path)
        self.explosion_sound = pygame.mixer.Sound(self.explosion_sound_path)

        # Set up the window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 300)  # Adjust to your image size

        # Load the image as a background
        self.background_label = QLabel(self)
        pixmap = QPixmap(self.image_path)
        self.background_label.setPixmap(pixmap)
        self.background_label.setFixedSize(pixmap.size())

        # Set up the countdown text label
        self.text_label = QLabel(self)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.update_font_style()
        self.text_label.setStyleSheet(f'color: {self.font_color}')
        self.text_label.setGeometry(self.text_position[0], self.text_position[1], 300, 100)  # Adjust position and size

        # Start the countdown timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.update_time()

        # Enable dragging
        self.old_position = None

    def update_time(self):
        """Update the countdown text every second and play beep sound."""
        if self.is_paused:
            return  # Do nothing if paused

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1

            # Play the beep sound each second, unless muted
            if not self.is_muted:
                self.play_beep()
        else:
            # Start the blinking effect and play explosion sound when the countdown reaches zero
            if not self.is_blinking:
                self.start_blinking()
            return

        hours_left = self.remaining_seconds // 3600
        minutes_left = (self.remaining_seconds % 3600) // 60
        seconds_left = self.remaining_seconds % 60
        time_str = f"{hours_left:02}:{minutes_left:02}:{seconds_left:02}"
        self.text_label.setText(time_str)

    def play_beep(self):
        """Play the beep sound."""
        self.beep_sound.play()

    def play_explosion(self):
        """Play the explosion sound."""
        if not self.is_muted:  # Only play if not muted
            self.explosion_sound.play()

    def update_font_style(self):
        """Update the font style of the countdown text."""
        font = QFont(self.font_name, self.font_size)
        self.text_label.setFont(font)

    def start_blinking(self):
        """Start blinking the countdown text when it reaches zero and play explosion sound."""
        self.is_blinking = True
        self.play_explosion()  # Play explosion sound when the countdown reaches zero
        self.timer.timeout.connect(self.blink_text)

    def blink_text(self):
        """Toggle the visibility of the countdown text for blinking effect."""
        self.is_visible = not self.is_visible
        self.text_label.setVisible(self.is_visible)

    def mousePressEvent(self, event):
        """Enable window dragging by detecting mouse press."""
        if event.button() == Qt.LeftButton:
            self.old_position = event.globalPos()

    def mouseMoveEvent(self, event):
        """Enable window dragging by detecting mouse movement."""
        if self.old_position:
            delta = QPoint(event.globalPos() - self.old_position)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_position = event.globalPos()

    def mouseReleaseEvent(self, event):
        """Reset old position when mouse button is released."""
        self.old_position = None

    def contextMenuEvent(self, event):
        """Create context menu for right-click."""
        context_menu = QMenu(self)

        # Toggle Mute/Unmute option
        mute_action = context_menu.addAction("Unmute" if self.is_muted else "Mute")
        reset_action = context_menu.addAction("Reset Timer")

        # Add Pause/Resume option
        pause_action = context_menu.addAction("Resume" if self.is_paused else "Pause")

        # Add time setting options
        set_8_hours = context_menu.addAction("Set to 8 Hours")
        set_4_hours = context_menu.addAction("Set to 4 Hours")
        set_1_hour = context_menu.addAction("Set to 1 Hour")
        set_30_minutes = context_menu.addAction("Set to 30 Minutes")
        set_15_minutes = context_menu.addAction("Set to 15 Minutes")
        set_10_minutes = context_menu.addAction("Set to 10 Minutes")
        set_5_minutes = context_menu.addAction("Set to 5 Minutes")
        set_1_minute = context_menu.addAction("Set to 1 Minute")
        set_30_seconds = context_menu.addAction("Set to 30 Seconds")

        # Custom time option
        custom_time_action = context_menu.addAction("Set Custom Time")

        quit_action = context_menu.addAction("Quit")

        action = context_menu.exec_(self.mapToGlobal(event.pos()))

        if action == mute_action:
            self.toggle_mute()
        elif action == reset_action:
            self.reset_timer()
        elif action == pause_action:
            self.toggle_pause()
        elif action == set_8_hours:
            self.set_timer(8 * 3600)
        elif action == set_4_hours:
            self.set_timer(4 * 3600)
        elif action == set_1_hour:
            self.set_timer(3600)
        elif action == set_30_minutes:
            self.set_timer(30 * 60)
        elif action == set_15_minutes:
            self.set_timer(15 * 60)
        elif action == set_10_minutes:
            self.set_timer(10 * 60)
        elif action == set_5_minutes:
            self.set_timer(5 * 60)
        elif action == set_1_minute:
            self.set_timer(60)
        elif action == set_30_seconds:
            self.set_timer(30)
        elif action == custom_time_action:
            self.set_custom_time()
        elif action == quit_action:
            self.close()

    def toggle_mute(self):
        """Toggle between Mute and Unmute."""
        self.is_muted = not self.is_muted

    def toggle_pause(self):
        """Toggle between Pause and Resume."""
        self.is_paused = not self.is_paused

    def reset_timer(self):
        """Reset the countdown timer and stop blinking."""
        self.remaining_seconds = self.reset_time
        self.stop_blinking()  # Stop blinking when the timer is reset
        self.text_label.setVisible(True)  # Make sure the text is visible when resetting
        self.update_time()

    def set_timer(self, seconds):
        """Set the timer to a specific amount of seconds."""
        self.reset_time = seconds
        self.reset_timer()

    def set_custom_time(self):
        """Open a dialog to set a custom time."""
        dialog = CustomTimeDialog(self)
        if dialog.exec_() == QDialog.Accepted and dialog.selected_time is not None:
            self.set_timer(dialog.selected_time)

    def stop_blinking(self):
        """Stop blinking and reset the label's visibility."""
        if self.is_blinking:
            self.is_blinking = False
            self.text_label.setVisible(True)  # Ensure the text is fully visible
            try:
                self.timer.timeout.disconnect(self.blink_text)  # Stop the blinking effect safely
            except TypeError:
                # This means there was no connection to blink_text, safe to ignore
                pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Path to your image and sound files
    current_dir = os.path.dirname(os.path.abspath(__file__))

    image_path = os.path.join(current_dir, 'dynamite.png')
    beep_sound_path = os.path.join(current_dir, 'beep.mp3')
    explosion_sound_path = os.path.join(current_dir, 'explosion.mp3')

    # Create the countdown widget with 60-minute countdown, font customization, and positioned text
    countdown = CountdownWidget(image_path=image_path, beep_sound_path=beep_sound_path, explosion_sound_path=explosion_sound_path, font_name="digital-7",  # Font name
                                font_size=14,  # Font size
                                font_color="red",  # Font color
                                text_position=(20, 17)  # Position of the countdown text
                                )

    # Show the widget
    countdown.show()

    # Run the app
    sys.exit(app.exec_())
