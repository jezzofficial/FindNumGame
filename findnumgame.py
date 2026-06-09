#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib
import cairo
import math
import getpass
import os
import json
import random 

STATS_FILE = os.path.expanduser("~/.cache/FindNumGame/stats.json")

def load_stats():
    default = {"games": 0, "total_accuracy": 0.0}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, "r") as f:
                data = json.load(f)
                if "games" in data and "total_accuracy" in data:
                    return data
        except:
            pass
    return default

def save_stats(stats):
    os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=2)

def update_stats(accuracy):
    stats = load_stats()
    stats["games"] += 1
    stats["total_accuracy"] += accuracy
    save_stats(stats)
    return stats

def get_average_accuracy(stats=None):
    if stats is None:
        stats = load_stats()
    if stats["games"] == 0:
        return 0.0
    return stats["total_accuracy"] / stats["games"]

class WelcomeScreen(Gtk.Box):
    def __init__(self, start_callback):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        self.set_margin_top(40)
        self.set_margin_bottom(40)
        self.set_margin_start(40)
        self.set_margin_end(40)

        self.username = getpass.getuser()
        self.text = f"Приветствую, {self.username}, не желаешь"
        self.start_callback = start_callback
        self.phase = 0.0

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row.set_halign(Gtk.Align.CENTER)

        self.drawing_area = Gtk.DrawingArea()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
        cr = cairo.Context(surface)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(34)
        ext = cr.text_extents(self.text)
        ascent, descent, _, _, _ = cr.font_extents()
        text_width = int(ext.width + 7)
        text_height = int(ascent + descent + 20)
        self.drawing_area.set_size_request(text_width, text_height)
        self.drawing_area.connect("draw", self.on_draw)
        row.pack_start(self.drawing_area, False, False, 0)

        self.start_button = Gtk.Button(label="Начать игру")
        self.start_button.connect("clicked", lambda w: self.start_callback())
        self.start_button.get_style_context().add_class("start-button")
        self.start_button.set_relief(Gtk.ReliefStyle.NONE)
        self.start_button.set_valign(Gtk.Align.CENTER)
        row.pack_start(self.start_button, False, False, 0)

        q = Gtk.Label()
        q.set_markup("<span size='24000' foreground='#c084fc'>?</span>")
        q.set_valign(Gtk.Align.CENTER)
        row.pack_start(q, False, False, 0)

        self.pack_start(row, False, False, 0)

        self.stats_label = Gtk.Label()
        self.stats_label.set_halign(Gtk.Align.CENTER)
        self.pack_start(self.stats_label, False, False, 10)
        self.update_stats_display()

        dev = Gtk.Label()
        dev.set_markup("<span foreground='#6b7280'>dev by jezzi • gtk3 • arch linux</span>")
        self.pack_start(dev, False, False, 5)

        GLib.timeout_add(50, self.on_timeout)

    def update_stats_display(self):
        stats = load_stats()
        avg = get_average_accuracy(stats)
        self.stats_label.set_markup(
            "<span foreground='#a1a1aa' size='11000'>"
            f"📊 Сыграно игр: {stats['games']}    "
            f"🎯 Средняя точность: {avg:.1f}%"
            "</span>"
        )

    def on_draw(self, widget, cr):
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(34)

        ext = cr.text_extents(self.text)
        ascent, descent, _, _, _ = cr.font_extents()

        x = 0
        y = ascent + 5 

        grad = cairo.LinearGradient(0, 0, ext.width, 0)
        p = self.phase
        grad.add_color_stop_rgb(0.0, 0.6 + 0.4 * math.sin(p), 0.2, 0.9)
        grad.add_color_stop_rgb(0.5, 0.2, 0.5 + 0.4 * math.cos(p), 0.9)
        grad.add_color_stop_rgb(1.0, 0.9, 0.3, 0.6 + 0.4 * math.sin(p))

        cr.set_source(grad)
        cr.move_to(x, y)
        cr.show_text(self.text)

    def on_timeout(self):
        self.phase += 0.08
        self.drawing_area.queue_draw()
        return True

class MainApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="Найди меня в числах")
        self.set_default_size(900, 550)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(True)

        self.phase = 0.0
        GLib.timeout_add(50, self.on_game_timeout)  # таймер для обновления phase

        # CSS
        css = b"""
        window { background-color: #09090f; }
        .start-button {
            background-image: linear-gradient(
                90deg,
                #6d28d9,
                #7c3aed,
                #8b5cf6
            );
            color: white;
            border: 1px solid #9f67ff;
            border-radius: 18px;
            padding: 10px 20px;
            font-size: 16px;
            font-weight: bold;
            box-shadow:
                0 0 8px rgba(124,58,237,0.4);
            transition: 200ms ease;
        }
        .start-button:hover { 
            background-image: linear-gradient(
                90deg,
                #7c3aed,
                #8b5cf6,
                #a855f7
            );
            border-color: #c084fc;
            box-shadow:
                0 0 16px rgba(168,85,247,0.8),
                0 0 32px rgba(168,85,247,0.4);
            color: white; 
        }
        .start-button:active {
            background-image: linear-gradient(
                90deg,
                #5b21b6,
                #6d28d9
            );
        }
        .stats-label {
            color: #a1a1aa;
            font-size: 14px;
        }
        .title-part1 { color: #c084fc; font-size: 36px; font-weight: bold; }
        .title-part2 { color: #60a5fa; font-size: 36px; font-weight: bold; }
        .number { color: #e5e7eb; font-size: 80px; font-weight: bold; }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(300)
        self.add(self.stack)

        self.welcome_screen = WelcomeScreen(self.on_start_game)
        self.stack.add_named(self.welcome_screen, "welcome")

        self.game_box = self.create_game_box()
        self.stack.add_named(self.game_box, "game")

        self.stack.set_visible_child_name("welcome")
        self.update_stats_display()

    def on_game_timeout(self):
        self.phase += 0.08
        if hasattr(self, "game_title_area"):
            self.game_title_area.queue_draw()
        return True

    def update_stats_display(self):
        self.welcome_screen.update_stats_display()

    def on_start_game(self):
        self.stack.set_visible_child_name("game")
        self.reset_game_state()
        self.drawing_area.queue_draw()

    def create_game_box(self):
        self.min_value = 0
        self.max_value = random.randint(50, 10000)
        self.target_number = random.randint(self.min_value, self.max_value)
        self.user_click_x = None
        self.correct_x = None
        self.game_active = True
        self.margin = 60
        self.round_finished = False

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        main_box.set_margin_top(40)
        main_box.set_margin_bottom(40)
        main_box.set_margin_start(30)
        main_box.set_margin_end(30)

        self.game_title_area = Gtk.DrawingArea()
        self.game_title_area.set_size_request(-1, 60)
        self.game_title_area.connect("draw", self.on_game_title_draw)
        main_box.pack_start(self.game_title_area, False, False, 0)

        self.target_label = Gtk.Label()
        self.target_label.set_text(str(self.target_number))
        self.target_label.get_style_context().add_class("number")
        main_box.pack_start(self.target_label, False, False, 10)

        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_hexpand(True)
        self.drawing_area.set_size_request(-1, 150)
        self.drawing_area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
        self.drawing_area.connect("draw", self.on_draw)
        self.drawing_area.connect("button-press-event", self.on_click)
        main_box.pack_start(self.drawing_area, False, False, 0)

        self.reset_button = Gtk.Button(label="Заново")
        self.reset_button.set_visible(False)
        self.reset_button.connect("clicked", self.on_reset)
        main_box.pack_start(self.reset_button, False, False, 20)

        return main_box

    def reset_game_state(self):
        self.max_value = random.randint(50, 10000)
        self.target_number = random.randint(self.min_value, self.max_value)
        self.user_click_x = None
        self.correct_x = None
        self.game_active = True
        self.round_finished = False
        self.target_label.set_text(str(self.target_number))
        self.reset_button.set_visible(False)

    def on_game_title_draw(self, widget, cr):
        text = "Найди меня в числах"
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        cr.set_font_size(36)
        ext = cr.text_extents(text)
        W = widget.get_allocated_width()
        H = widget.get_allocated_height()
        x = (W - ext.width)/2
        y = (H + ext.height)/2
        grad = cairo.LinearGradient(0,0,ext.width,0)
        p = self.phase
        grad.add_color_stop_rgb(0, 0.6 + 0.4*math.sin(p), 0.2, 0.9)
        grad.add_color_stop_rgb(0.5, 0.2, 0.5 + 0.4*math.cos(p), 0.9)
        grad.add_color_stop_rgb(1, 0.9, 0.3, 0.6 + 0.4*math.sin(p))
        cr.set_source(grad)
        cr.move_to(x,y)
        cr.show_text(text)

    def calculate_correct_position(self, start_x, end_x):
        normalized = (self.target_number - self.min_value) / (self.max_value - self.min_value)
        return start_x + (end_x - start_x) * normalized

    def on_draw(self, widget, cr):
        width = widget.get_allocated_width()
        height = widget.get_allocated_height()
        y_line = height / 2
        start_x = self.margin
        end_x = width - self.margin

        cr.set_source_rgb(0.5, 0.5, 0.6)
        cr.set_line_width(3)
        cr.move_to(start_x, y_line)
        cr.line_to(end_x, y_line)
        cr.stroke()

        cr.set_source_rgb(0.6, 0.6, 0.7)
        cr.arc(end_x, y_line, 6, 0, 2 * math.pi)
        cr.fill()

        cr.set_source_rgb(0.6, 0.6, 0.7)
        cr.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(22)
        text = str(self.max_value)
        (x_advance, _) = cr.text_extents(text)[2:4]
        text_x = end_x - x_advance / 2
        text_y = y_line + 40
        cr.move_to(text_x, text_y)
        cr.show_text(text)

        if self.user_click_x is not None and not self.game_active:
            cr.set_source_rgb(0.95, 0.3, 0.45)
            cr.set_line_width(3)
            cr.move_to(self.user_click_x, y_line - 15)
            cr.line_to(self.user_click_x, y_line + 15)
            cr.stroke()
            cr.set_source_rgb(0.95, 0.3, 0.45)
            cr.set_font_size(12)
            text = "YOU"
            (x_adv, _) = cr.text_extents(text)[2:4]
            cr.move_to(self.user_click_x - x_adv/2, y_line - 20)
            cr.show_text(text)

        if self.correct_x is not None and not self.game_active:
            cr.set_source_rgb(0.3, 0.9, 0.5)
            cr.set_line_width(3)
            cr.move_to(self.correct_x, y_line - 15)
            cr.line_to(self.correct_x, y_line + 15)
            cr.stroke()
            cr.set_source_rgb(0.3, 0.9, 0.5)
            cr.set_font_size(12)
            text = "ANSWER"
            (x_adv, _) = cr.text_extents(text)[2:4]
            cr.move_to(self.correct_x - x_adv/2, y_line - 20)
            cr.show_text(text)

    def on_click(self, widget, event):
        if not self.game_active:
            return

        width = widget.get_allocated_width()
        start_x = self.margin
        end_x = width - self.margin
        click_x = event.x
        if click_x < start_x or click_x > end_x:
            return

        self.user_click_x = click_x
        self.correct_x = self.calculate_correct_position(start_x, end_x)

        distance = abs(click_x - self.correct_x)
        max_distance = end_x - start_x
        accuracy = max(0, 100 - (distance / max_distance * 100))
        accuracy = round(accuracy, 1)

        if not self.round_finished:
            update_stats(accuracy)
            self.round_finished = True

        self.target_number = accuracy
        self.target_label.set_text(str(self.target_number))

        self.game_active = False
        self.reset_button.set_visible(True)
        widget.queue_draw()

    def on_reset(self, widget):
        self.reset_game_state()
        self.drawing_area.queue_draw()

def main():
    app = MainApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
