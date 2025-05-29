from exercise_factory import ExerciseFactoryProvider
from user_profile import UserProfile, ExerciseFeedback
from training_plan_manager import TrainingPlanManager
from training_archive_manager import TrainingArchiveManager
from user_profile_manager import UserProfileManager
from trainer import Trainer
import customtkinter as ctk
import json
import os
import random
from datetime import datetime
from customtkinter import CTkImage
import time
import threading
from enum import Enum
from abc import ABC, abstractmethod
from PIL import Image, ImageTk
import uuid
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import math


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class TrainingApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fitness Trainer")
        self.geometry("1000x700")
        self.configure(fg_color="#1e1e1e")
        self.profile_manager = UserProfileManager()
        self.plan_manager = TrainingPlanManager()
        self.archive_manager = TrainingArchiveManager()
        self.user_profile = self.profile_manager.load_user_profile()
        self.user_profile._tk_root = self
        self.current_plan = None
        self.trainer = None
        self.confirm_response = ctk.BooleanVar()
        self.current_page = None
        self.muscle_groups_var = []
        self.muscle_buttons = {}
        self.location_buttons = {}
        self.plan_type_buttons = {}
        self.workout_type_buttons = {}
        self.training_mode_buttons = {}
        self.feedback_buttons = {}
        self.training_confirmation_buttons = {}
        self.nav_buttons = {}
        self.theme_var = ctk.StringVar(value="dark")
        self.themed_widgets = {"frames": [], "buttons": [], "labels": [], "canvases": [], "segmented_buttons": [], "option_menus": []}
        self.theme_colors = {
            "dark": {"main_bg": "#1e1e1e", "navbar_bg": "#2a2a2a", "card_bg": "#2a2a2a", "inner_card_bg": "#3a3a3a",
                     "exercise_card_bg": "#4a4a4a", "canvas_bg": "#2a2a2a", "text_color": "#10b981", "text_accent": "#12d1a1",
                     "button_fg": "#3a3a3a", "button_active": "#10b981", "button_hover": "#12d1a1", "theme_button_fg": "#3a3a3a",
                     "option_menu_fg": "#4a4a4a", "option_menu_button": "#10b981", "shadow_color": "#10b981"},
            "light": {"main_bg": "#f0f0f0", "navbar_bg": "#d9d9d9", "card_bg": "#ffffff", "inner_card_bg": "#e6e6e6",
                      "exercise_card_bg": "#d1d1d1", "canvas_bg": "#ffffff", "text_color": "#166534", "text_accent": "#22c55e",
                      "button_fg": "#a3a3a3", "button_active": "#15803d", "button_hover": "#22c55e", "theme_button_fg": "#d97706",
                      "option_menu_fg": "#d1d1d1", "option_menu_button": "#15803d", "shadow_color": "#15803d"}
        }
        self.timer_running = False
        self.timer_thread = None
        self.timer_duration = 0
        self.timer_remaining = 0
        self.timer_canvas = None
        self.timer_text = None
        self.timer_arc = None
        self.timer_label = None
        self.exercise_status = {}
        self.create_widgets()
        if self.profile_manager.is_user_profile_file_empty():
            self.show_profile_page()

    def create_widgets(self):
        self.navbar = ctk.CTkFrame(self, height=60, fg_color=self.theme_colors["dark"]["navbar_bg"], corner_radius=0)
        self.navbar.pack(side="top", fill="x")
        self.themed_widgets["frames"].append((self.navbar, "fg_color", "navbar_bg"))
        self.content = ctk.CTkFrame(self, fg_color=self.theme_colors["dark"]["main_bg"])
        self.content.pack(fill="both", expand=True)
        self.themed_widgets["frames"].append((self.content, "fg_color", "main_bg"))
        self.home_frame = ctk.CTkFrame(self.content, fg_color=self.theme_colors["dark"]["main_bg"])
        self.training_frame = ctk.CTkFrame(self.content, fg_color=self.theme_colors["dark"]["main_bg"])
        self.archive_frame = ctk.CTkFrame(self.content, fg_color=self.theme_colors["dark"]["main_bg"])
        self.stats_frame = ctk.CTkFrame(self.content, fg_color=self.theme_colors["dark"]["main_bg"])
        self.profile_frame = ctk.CTkFrame(self.content, fg_color=self.theme_colors["dark"]["main_bg"])
        self.themed_widgets["frames"].extend([(self.home_frame, "fg_color", "main_bg"), (self.training_frame, "fg_color", "main_bg"),
                                              (self.archive_frame, "fg_color", "main_bg"), (self.stats_frame, "fg_color", "main_bg"),
                                              (self.profile_frame, "fg_color", "main_bg")])
        nav_buttons = [("🏠 Про нас", self.show_home_page, self.home_frame), (" 💪 Тренування", self.show_training_page, self.training_frame),
                       ("📚 Архів", self.show_archive_page, self.archive_frame), ("📊 Статистика", self.show_statistics_page, self.stats_frame),
                       ("👤 Характеристики", self.show_profile_page, self.profile_frame), ("🚪 Вихід", self.quit_application, None)]
        for text, command, frame in nav_buttons:
            button = ctk.CTkButton(self.navbar, text=text, font=("Roboto", 14), command=command, fg_color=self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], corner_radius=8, width=150)
            button.pack(side="left", padx=5, pady=5, anchor="center")
            self.nav_buttons[text] = {"button": button, "frame": frame}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_fg"), (button, "hover_color", "button_hover")])
        theme_button = ctk.CTkButton(self.navbar, text="🌙", font=("Roboto", 14), command=self.toggle_theme,
                                     fg_color=self.theme_colors["dark"]["theme_button_fg"], hover_color=self.theme_colors["dark"]["button_hover"],
                                     corner_radius=8, width=60)
        theme_button.pack(side="right", padx=5, pady=5, anchor="center")
        self.nav_buttons["theme"] = {"button": theme_button, "frame": None}
        self.themed_widgets["buttons"].extend([(theme_button, "fg_color", "theme_button_fg"), (theme_button, "hover_color", "button_hover")])
        self.setup_home_page()
        self.setup_training_page()
        self.setup_archive_page()
        self.setup_statistics_page()
        self.setup_profile_page()
        self.show_home_page()

    def toggle_theme(self):
        new_theme = "light" if self.theme_var.get() == "dark" else "dark"
        ctk.set_appearance_mode(new_theme)
        self.theme_var.set(new_theme)
        self.nav_buttons["theme"]["button"].configure(text="☀️" if new_theme == "light" else "🌙")
        for widget_type, widgets in self.themed_widgets.items():
            for widget_info in widgets:
                widget, attr, color_key, *extra = widget_info
                if widget is None: continue
                if widget_type == "labels" and extra:
                    widget.itemconfig(extra[0], **{attr: self.theme_colors[new_theme][color_key]})
                else:
                    widget.configure(**{attr: self.theme_colors[new_theme][color_key]})

    def _switch_page(self, frame):
        if self.current_page:
            self.current_page.pack_forget()
        self.current_page = frame
        frame.pack(fill="both", expand=True)
        for text, info in self.nav_buttons.items():
            if text != "theme":
                info["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if info["frame"] == frame else self.theme_colors[self.theme_var.get()]["button_fg"])

    def show_home_page(self): self._switch_page(self.home_frame)
    def show_training_page(self): self._switch_page(self.training_frame)
    def show_archive_page(self):
        self._switch_page(self.archive_frame)
        self.update_archive_display()
    def show_statistics_page(self):
        self._switch_page(self.stats_frame)
        self.update_statistics_display()
    def show_profile_page(self):
        self._switch_page(self.profile_frame)
        self.update_profile_display()

    def setup_home_page(self):
        def interpolate_color(start_rgb, end_rgb, factor):
            return tuple(int(start + (end - start) * factor) for start, end in zip(start_rgb, end_rgb))

        for widget in self.home_frame.winfo_children():
            widget.destroy()

        motivational_titles = [
            "Досягай нових вершин з кожним тренуванням!",
            "Твоя сила – у регулярності!",
            "Стань кращою версією себе!",
            "Крок за кроком до твоєї мети!",
            "Тренуйся сьогодні, щоб сяяти завтра!"
        ]

        selected_title = random.choice(motivational_titles)

        welcome_label = ctk.CTkLabel(
            self.home_frame,
            text=selected_title,
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors["dark"]["text_color"]
        )
        welcome_label.pack(pady=(10, 2))
        self.themed_widgets["labels"].append((welcome_label, "text_color", "text_color"))

        image_path = r"C:\Users\Asus\PycharmProjects\CW\assets\Images\Image2.png"
        try:
            img = Image.open(image_path).convert("RGBA")
            original_width, original_height = img.size
            new_width = 550
            new_height = int(original_height * (new_width / original_width))
            img = img.resize((new_width, new_height), Image.LANCZOS)
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(new_width, new_height))
            image_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
            image_frame.pack(pady=(0, 2))
            image_label = ctk.CTkLabel(image_frame, image=ctk_img, text="", fg_color="transparent")
            image_label.pack()
        except Exception:
            error_label = ctk.CTkLabel(
                self.home_frame,
                text="Не вдалося завантажити зображення.",
                font=("Roboto", 14),
                text_color=self.theme_colors["dark"]["text_color"]
            )
            error_label.pack(pady=(0, 2))
            self.themed_widgets["labels"].append((error_label, "text_color", "text_color"))

        cards_container = ctk.CTkFrame(self.home_frame, fg_color="transparent")
        cards_container.pack(pady=5, fill="x", padx=20)
        cards_container.grid_columnconfigure(0, weight=1)
        cards_container.grid_columnconfigure(1, weight=1)

        why_us_lines = random.choice([
            [
                "🔥 Індивідуальні плани тренувань під твої цілі та потреби.",
                "📊 Аналітика прогресу в зручному та інтуїтивному інтерфейсі.",
                "🤝 Спільнота для підтримки, мотивації та обміну досвідом.",
                "💬 Відгуки від користувачів, які вже досягнули результатів.",
            ],
            [
                "🔥 Персоналізовані програми для всіх рівнів підготовки.",
                "📈 Стеження за результатами в реальному часі з графіками.",
                "🌟 Спільнота, яка надихає та допомагає не зупинятися.",
                "💡 Поради від реальних людей, що змінили своє життя.",
            ],
            [
                "🔥 Тренування, розроблені спеціально під твої завдання.",
                "📉 Контроль прогресу з чіткими та зрозумілими звітами.",
                "👥 Об’єднання з іншими для спільної мотивації та цілей.",
                "🌟 Досвід тих, хто досяг успіху завдяки додатку.",
            ],
        ])

        why_us_card = ctk.CTkFrame(
            cards_container,
            fg_color=self.theme_colors["dark"]["card_bg"],
            corner_radius=15,
            border_width=0
        )
        why_us_card.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=5)
        self.themed_widgets["frames"].append((why_us_card, "fg_color", "card_bg"))

        why_us_title = ctk.CTkLabel(
            why_us_card,
            text="🔥 Чому варто обрати нас",
            font=("Roboto", 17, "bold"),
            text_color=self.theme_colors["dark"]["text_accent"],
            anchor="w", justify="left"
        )
        why_us_title.pack(anchor="w", padx=15, pady=(15, 5))
        self.themed_widgets["labels"].append((why_us_title, "text_color", "text_accent"))

        start_color = (0, 255, 170)
        end_color = (0, 180, 90)

        for i, line in enumerate(why_us_lines):
            factor = i / (len(why_us_lines) - 1) if len(why_us_lines) > 1 else 0
            gradient_color_rgb = interpolate_color(start_color, end_color, factor)
            # Конвертуємо RGB у hex
            gradient_color_hex = f"#{gradient_color_rgb[0]:02x}{gradient_color_rgb[1]:02x}{gradient_color_rgb[2]:02x}"
            label = ctk.CTkLabel(
                why_us_card,
                text=line,
                font=("Roboto", 13, "bold"),
                text_color=gradient_color_hex,
                anchor="w", justify="left",
                wraplength=480
            )
            if i == len(why_us_lines) - 1:
                label.pack(anchor="w", padx=20, pady=(1, 10))
            else:
                label.pack(anchor="w", padx=20, pady=1)
            self.themed_widgets["labels"].append((label, "text_color", None))

        community_lines = random.choice([
            [
                "💬 «Мотивує повертатися до тренувань щодня!» — Олена, 29",
                "💬 «Спільнота допомагає не здаватися на шляху!» — Артем, 34",
                "💬 «Гнучкі плани і стильний дизайн — ідеально!» — Ірина, 22",
                "💬 «Додаток, який змінив мої звички!» — Максим, 30",
            ],
            [
                "💬 «Змінив мій підхід до фітнесу назавжди!» — Марія, 27",
                "💬 «Підтримка спільноти — це справжня сила!» — Олег, 31",
                "💬 «Зручний інтерфейс і надихаючі плани!» — Софія, 25",
                "💬 «Тренування стали частиною життя!» — Віктор, 33",
            ],
            [
                "💬 «Тренування — тепер мій щоденний ритуал!» — Анна, 30",
                "💬 «Спільнота заряджає енергією та мотивацією!» — Дмитро, 28",
                "💬 «Найкращий додаток для фітнесу, що я пробувала!» — Ольга, 23",
                "💬 «Простота і ефективність у кожному кроці!» — Юлія, 26",
            ],
        ])

        community_card = ctk.CTkFrame(
            cards_container,
            fg_color=self.theme_colors["dark"]["card_bg"],
            corner_radius=15,
            border_width=0
        )
        community_card.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=5)
        self.themed_widgets["frames"].append((community_card, "fg_color", "card_bg"))

        community_title = ctk.CTkLabel(
            community_card,
            text="👥 Що каже наша спільнота",
            font=("Roboto", 17, "bold"),
            text_color=self.theme_colors["dark"]["text_accent"],
            anchor="w", justify="left"
        )
        community_title.pack(anchor="w", padx=15, pady=(15, 5))
        self.themed_widgets["labels"].append((community_title, "text_color", "text_accent"))

        for i, line in enumerate(community_lines):
            factor = i / (len(community_lines) - 1) if len(community_lines) > 1 else 0  # Фактор для градієнта
            gradient_color_rgb = interpolate_color(start_color, end_color, factor)
            # Конвертуємо RGB у hex
            gradient_color_hex = f"#{gradient_color_rgb[0]:02x}{gradient_color_rgb[1]:02x}{gradient_color_rgb[2]:02x}"
            label = ctk.CTkLabel(
                community_card,
                text=line,
                font=("Roboto", 13, "bold"),
                text_color=gradient_color_hex,
                anchor="w", justify="left",
                wraplength=480
            )
            if i == len(community_lines) - 1:
                label.pack(anchor="w", padx=20, pady=(1, 10))
            else:
                label.pack(anchor="w", padx=20, pady=1)
            self.themed_widgets["labels"].append((label, "text_color", None))

    def animate_fade_in(self, widget, duration=500, steps=20):
        for i in range(steps):
            alpha = i / steps
            text_color = f"{self.theme_colors[self.theme_var.get()]['text_color']}{int(alpha*255):02x}"
            widget.configure(text_color=text_color)
            self.update()
            time.sleep(duration / steps / 1000)

    def animate_button_hover(self, button, enter=True):

        is_feedback_button = any(button == info["button"] for info in self.feedback_buttons.values())
        is_confirmation_button = any(button == info["button"] for info in self.training_confirmation_buttons.values())

        if is_feedback_button or is_confirmation_button:

            button_key = None
            buttons_dict = self.feedback_buttons if is_feedback_button else self.training_confirmation_buttons
            for key, info in buttons_dict.items():
                if button == info["button"]:
                    button_key = key
                    break

            if button_key:
                selected = buttons_dict[button_key]["selected"]
                if enter and not selected:

                    button.configure(
                        border_width=2,
                        border_color=self.theme_colors[self.theme_var.get()]["shadow_color"],
                        fg_color=self.theme_colors[self.theme_var.get()]["button_hover"]
                    )
                elif not selected:

                    button.configure(
                        border_width=0,
                        border_color="",
                        fg_color=self.theme_colors[self.theme_var.get()]["button_fg"]
                    )

        else:
            button.configure(
                border_width=2 if enter else 0,
                border_color=self.theme_colors[self.theme_var.get()]["shadow_color"] if enter else "",
                fg_color=self.theme_colors[self.theme_var.get()]["button_hover"] if enter else
                self.theme_colors[self.theme_var.get()]["button_active"]
            )

    def setup_training_page(self):
        input_card = ctk.CTkFrame(self.training_frame, fg_color=self.theme_colors["dark"]["card_bg"], corner_radius=12, width=300)
        input_card.pack(side="left", fill="y", padx=10, pady=10, ipadx=10, ipady=10)
        self.themed_widgets["frames"].append((input_card, "fg_color", "card_bg"))
        label = ctk.CTkLabel(input_card, text="Створити План", font=("Roboto", 20, "bold"), text_color=self.theme_colors["dark"]["text_color"])
        label.pack(pady=8)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))

        label_loc = ctk.CTkLabel(input_card, text=" Місце тренування:", font=("Roboto", 14), text_color=self.theme_colors["dark"]["text_color"])
        label_loc.pack(anchor="w", padx=13, pady=4)
        self.themed_widgets["labels"].append((label_loc, "text_color", "text_color"))
        location_frame = ctk.CTkFrame(input_card, fg_color=self.theme_colors["dark"]["card_bg"])
        location_frame.pack(fill="x", padx=8, pady=4)
        self.themed_widgets["frames"].append((location_frame, "fg_color", "card_bg"))
        self.location_var = ctk.StringVar(value="Gym")
        locations = ["Gym", "Home", "Park"]
        for i, loc in enumerate(locations):
            button = ctk.CTkButton(location_frame, text=loc, font=("Roboto", 14), width=80, fg_color=self.theme_colors["dark"]["button_active"] if loc == "Gym" else self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], command=lambda l=loc: self.select_location(l))
            button.grid(row=0, column=i, padx=4, pady=4, sticky="ew")
            self.location_buttons[loc] = {"button": button, "selected": loc == "Gym"}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_active" if loc == "Gym" else "button_fg"), (button, "hover_color", "button_hover")])
        for i in range(len(locations)):
            location_frame.grid_columnconfigure(i, weight=1)

        label_plan = ctk.CTkLabel(input_card, text=" Тип плану:", font=("Roboto", 14), text_color=self.theme_colors["dark"]["text_color"])
        label_plan.pack(anchor="w", padx=13, pady=4)
        self.themed_widgets["labels"].append((label_plan, "text_color", "text_color"))
        plan_type_frame = ctk.CTkFrame(input_card, fg_color=self.theme_colors["dark"]["card_bg"])
        plan_type_frame.pack(fill="x", padx=8, pady=4)
        self.themed_widgets["frames"].append((plan_type_frame, "fg_color", "card_bg"))
        self.plan_type_var = ctk.StringVar(value="Cardio")
        plan_types = ["Cardio", "Strength"]
        for i, pt in enumerate(plan_types):
            button = ctk.CTkButton(plan_type_frame, text=pt, font=("Roboto", 14), width=80, fg_color=self.theme_colors["dark"]["button_active"] if pt == "Cardio" else self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], command=lambda p=pt: self.select_plan_type(p))
            button.grid(row=0, column=i, padx=4, pady=4, sticky="ew")
            self.plan_type_buttons[pt] = {"button": button, "selected": pt == "Cardio"}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_active" if pt == "Cardio" else "button_fg"), (button, "hover_color", "button_hover")])
        for i in range(len(plan_types)):
            plan_type_frame.grid_columnconfigure(i, weight=1)

        label_workout = ctk.CTkLabel(input_card, text=" Тип тренування:", font=("Roboto", 14), text_color=self.theme_colors["dark"]["text_color"])
        label_workout.pack(anchor="w", padx=13, pady=4)
        self.themed_widgets["labels"].append((label_workout, "text_color", "text_color"))
        workout_type_frame = ctk.CTkFrame(input_card, fg_color=self.theme_colors["dark"]["card_bg"])
        workout_type_frame.pack(fill="x", padx=8, pady=4)
        self.themed_widgets["frames"].append((workout_type_frame, "fg_color", "card_bg"))
        self.workout_type_var = ctk.StringVar(value="Full-body")
        workout_types = ["Full-body", "Split"]
        for i, wt in enumerate(workout_types):
            button = ctk.CTkButton(workout_type_frame, text=wt, font=("Roboto", 14), width=80, fg_color=self.theme_colors["dark"]["button_active"] if wt == "Full-body" else self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], state="disabled", command=lambda w=wt: self.select_workout_type(w))
            button.grid(row=0, column=i, padx=4, pady=4, sticky="ew")
            self.workout_type_buttons[wt] = {"button": button, "selected": wt == "Full-body"}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_active" if wt == "Full-body" else "button_fg"), (button, "hover_color", "button_hover")])
        for i in range(len(workout_types)):
            workout_type_frame.grid_columnconfigure(i, weight=1)

        label_muscle = ctk.CTkLabel(input_card, text=" М’язові групи:", font=("Roboto", 14), text_color=self.theme_colors["dark"]["text_color"])
        label_muscle.pack(anchor="w", padx=13, pady=4)
        self.themed_widgets["labels"].append((label_muscle, "text_color", "text_color"))
        muscle_frame = ctk.CTkFrame(input_card, fg_color=self.theme_colors["dark"]["card_bg"])
        muscle_frame.pack(fill="x", padx=8, pady=4)
        self.themed_widgets["frames"].append((muscle_frame, "fg_color", "card_bg"))
        muscle_groups = ["Arms", "Chest", "Back", "Legs", "Shoulders", "Core"]
        for i, group in enumerate(muscle_groups):
            button = ctk.CTkButton(muscle_frame, text=group, font=("Roboto", 14), width=80, fg_color=self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], state="disabled", command=lambda g=group: self.toggle_muscle_group(g))
            button.grid(row=i // 3, column=i % 3, padx=4, pady=4, sticky="ew")
            self.muscle_buttons[group] = {"button": button, "selected": False}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_fg"), (button, "hover_color", "button_hover")])
        muscle_frame.grid_columnconfigure((0, 1, 2), weight=1)

        label_mode = ctk.CTkLabel(input_card, text=" Режим тренування:", font=("Roboto", 14), text_color=self.theme_colors["dark"]["text_color"])
        label_mode.pack(anchor="w", padx=13, pady=4)
        self.themed_widgets["labels"].append((label_mode, "text_color", "text_color"))
        training_mode_frame = ctk.CTkFrame(input_card, fg_color=self.theme_colors["dark"]["card_bg"])
        training_mode_frame.pack(fill="x", padx=8, pady=4)
        self.themed_widgets["frames"].append((training_mode_frame, "fg_color", "card_bg"))
        self.training_mode_var = ctk.StringVar(value="Тренер")
        training_modes = ["Тренер", "Самостійно"]
        for i, tm in enumerate(training_modes):
            button = ctk.CTkButton(training_mode_frame, text=tm, font=("Roboto", 14), width=80, fg_color=self.theme_colors["dark"]["button_active"] if tm == "Тренер" else self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], command=lambda m=tm: self.select_training_mode(m))
            button.grid(row=0, column=i, padx=4, pady=4, sticky="ew")
            self.training_mode_buttons[tm] = {"button": button, "selected": tm == "Тренер"}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_active" if tm == "Тренер" else "button_fg"), (button, "hover_color", "button_hover")])
        for i in range(len(training_modes)):
            training_mode_frame.grid_columnconfigure(i, weight=1)

        button_create = ctk.CTkButton(input_card, text="Створення Плану", font=("Roboto", 16), command=self.generate_plan, fg_color=self.theme_colors["dark"]["button_active"], hover_color=self.theme_colors["dark"]["button_hover"], width=242)
        button_create.pack(fill="x", padx=14, pady=10)
        self.themed_widgets["buttons"].extend([(button_create, "fg_color", "button_active"), (button_create, "hover_color", "button_hover")])

        self.display_card = ctk.CTkFrame(self.training_frame, fg_color=self.theme_colors["dark"]["card_bg"], corner_radius=12)
        self.display_card.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        self.themed_widgets["frames"].append((self.display_card, "fg_color", "card_bg"))
        label_display = ctk.CTkLabel(self.display_card, text="План Тренувань", font=("Roboto", 20, "bold"), text_color=self.theme_colors["dark"]["text_color"])
        label_display.pack(pady=8)
        self.themed_widgets["labels"].append((label_display, "text_color", "text_color"))
        self.plan_canvas = ctk.CTkCanvas(self.display_card, bg=self.theme_colors["dark"]["canvas_bg"], highlightthickness=0)
        self.plan_scrollbar = ctk.CTkScrollbar(self.display_card, orientation="vertical", command=self.plan_canvas.yview)
        self.plan_scrollbar.pack(side="right", fill="y")
        self.plan_canvas.configure(yscrollcommand=self.plan_scrollbar.set)
        self.plan_canvas.pack(fill="both", expand=True, padx=(8, 0), pady=8)
        self.themed_widgets["canvases"].append((self.plan_canvas, "bg", "canvas_bg"))
        self.plan_frame_inner = ctk.CTkFrame(self.plan_canvas, fg_color=self.theme_colors["dark"]["card_bg"])
        self.plan_canvas.create_window((0, 0), window=self.plan_frame_inner, anchor="nw", width=self.display_card.winfo_screenwidth())
        self.themed_widgets["frames"].append((self.plan_frame_inner, "fg_color", "card_bg"))
        self.plan_frame_inner.bind("<Configure>", lambda e: self.plan_canvas.configure(scrollregion=self.plan_canvas.bbox("all")))

        self.trainer_card = ctk.CTkFrame(self.display_card, fg_color=self.theme_colors["dark"]["inner_card_bg"], corner_radius=16, width=450, height=200)
        self.trainer_card.pack_propagate(False)
        self.themed_widgets["frames"].append((self.trainer_card, "fg_color", "inner_card_bg"))
        self.trainer_details_frame = ctk.CTkFrame(self.trainer_card, fg_color=self.theme_colors["dark"]["inner_card_bg"], width=380, height=180)
        self.trainer_details_frame.pack_propagate(False)
        self.trainer_details_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.themed_widgets["frames"].append((self.trainer_details_frame, "fg_color", "inner_card_bg"))
        self.trainer_label = ctk.CTkLabel(self.trainer_details_frame, text="", font=("Roboto", 16, "bold"), wraplength=360, text_color=self.theme_colors["dark"]["text_color"])
        self.themed_widgets["labels"].append((self.trainer_label, "text_color", "text_color"))
        self.set_label = ctk.CTkLabel(self.trainer_details_frame, text="", font=("Roboto", 14), text_color=self.theme_colors["dark"]["text_color"])
        self.themed_widgets["labels"].append((self.set_label, "text_color", "text_color"))
        self.button_container = ctk.CTkFrame(self.trainer_details_frame, fg_color=self.theme_colors["dark"]["inner_card_bg"], corner_radius=12)
        self.themed_widgets["frames"].append((self.button_container, "fg_color", "inner_card_bg"))
        self.start_training_button = ctk.CTkButton(
            self.button_container,
            text="🏋️Розпочати",
            font=("Roboto", 16),
            command=self.start_trainer_mode,
            fg_color=self.theme_colors["dark"]["button_active"],
            hover_color=self.theme_colors["dark"]["button_hover"],
            corner_radius=10,
            width=150,
        )
        self.start_training_button.bind("<Enter>",
                                        lambda e: self.animate_button_hover(self.start_training_button, True))
        self.start_training_button.bind("<Leave>",
                                        lambda e: self.animate_button_hover(self.start_training_button, False))
        self.themed_widgets["buttons"].extend([
            (self.start_training_button, "fg_color", "button_active"),
            (self.start_training_button, "hover_color", "button_hover")
        ])
        self.start_training_button.bind("<Enter>", lambda e: self.animate_button_hover(self.start_training_button, True))
        self.start_training_button.bind("<Leave>", lambda e: self.animate_button_hover(self.start_training_button, False))
        self.themed_widgets["buttons"].extend([(self.start_training_button, "fg_color", "button_active"), (self.start_training_button, "hover_color", "button_hover")])
        self.trainer_button = ctk.CTkButton(self.button_container, text="✅ Закінчив", font=("Roboto", 16), command=self.confirm_trainer_action,
                                            fg_color=self.theme_colors["dark"]["button_active"], hover_color=self.theme_colors["dark"]["button_hover"], corner_radius=10, width=200)
        self.trainer_button.bind("<Enter>", lambda e: self.animate_button_hover(self.trainer_button, True))
        self.trainer_button.bind("<Leave>", lambda e: self.animate_button_hover(self.trainer_button, False))
        self.themed_widgets["buttons"].extend([(self.trainer_button, "fg_color", "button_active"), (self.trainer_button, "hover_color", "button_hover")])
        self.feedback_frame = ctk.CTkFrame(self.button_container, fg_color="transparent")
        self.themed_widgets["frames"].append((self.feedback_frame, "fg_color", "inner_card_bg"))
        self.feedback_var = ctk.StringVar(value="")
        feeds = ["😊 Easy", "😐 Normal", "😓 Hard"]
        for i, fb in enumerate(feeds):
            button = ctk.CTkButton(self.feedback_frame, text=fb, font=("Roboto", 14), width=80, fg_color=self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], corner_radius=10, command=lambda f=fb.split()[-1]: self.select_feedback(f))
            button.pack(side="left", padx=4, pady=4)
            button.bind("<Enter>", lambda e, b=button: self.animate_button_hover(b, True))
            button.bind("<Leave>", lambda e, b=button: self.animate_button_hover(b, False))
            self.feedback_buttons[fb] = {"button": button, "selected": False}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_fg"), (button, "hover_color", "button_hover")])
        self.feedback_submit_button = ctk.CTkButton(self.button_container, text="📤 Надіслати", font=("Roboto", 16), command=self.submit_feedback,
                                                   fg_color=self.theme_colors["dark"]["button_active"], hover_color=self.theme_colors["dark"]["button_hover"], corner_radius=10, width=200)
        self.feedback_submit_button.bind("<Enter>", lambda e: self.animate_button_hover(self.feedback_submit_button, True))
        self.feedback_submit_button.bind("<Leave>", lambda e: self.animate_button_hover(self.feedback_submit_button, False))
        self.themed_widgets["buttons"].extend([(self.feedback_submit_button, "fg_color", "button_active"), (self.feedback_submit_button, "hover_color", "button_hover")])
        self.training_confirmation_frame = ctk.CTkFrame(self.button_container, fg_color="transparent")
        self.themed_widgets["frames"].append((self.training_confirmation_frame, "fg_color", "inner_card_bg"))
        self.training_confirmation_var = ctk.StringVar(value="")
        confirmations = ["Yes", "No"]
        for i, tc in enumerate(confirmations):
            button = ctk.CTkButton(self.training_confirmation_frame, text=tc, font=("Roboto", 14), width=80, fg_color=self.theme_colors["dark"]["button_fg"],
                                   hover_color=self.theme_colors["dark"]["button_hover"], corner_radius=10, command=lambda c=tc: self.select_training_confirmation(c))
            button.pack(side="left", padx=4, pady=4)
            button.bind("<Enter>", lambda e, b=button: self.animate_button_hover(b, True))
            button.bind("<Leave>", lambda e, b=button: self.animate_button_hover(b, False))
            self.training_confirmation_buttons[tc] = {"button": button, "selected": False}
            self.themed_widgets["buttons"].extend([(button, "fg_color", "button_fg"), (button, "hover_color", "button_hover")])
        self.plan_type_var.trace("w", self.update_workout_type_state)

    def start_timer(self, duration, label_text=""):
        self.timer_duration = duration
        self.timer_remaining = duration
        self.timer_running = True
        card_width = 180
        self.timer_canvas = ctk.CTkCanvas(self.trainer_details_frame, width=card_width, height=card_width,
                                          bg=self.theme_colors["dark"]["inner_card_bg"], highlightthickness=0)
        self.themed_widgets["canvases"].append((self.timer_canvas, "bg", "inner_card_bg"))
        self.timer_label = ctk.CTkLabel(self.trainer_details_frame, text=label_text, font=("Roboto", 16),
                                        text_color=self.theme_colors["dark"]["text_color"])
        self.timer_label.pack(pady=(10, 0))
        self.themed_widgets["labels"].append((self.timer_label, "text_color", "text_color"))
        self.timer_canvas.pack(pady=0)
        center = card_width / 2
        self.timer_arc = self.timer_canvas.create_arc(15, 15, card_width - 15, card_width - 15, start=90, extent=-360,
                                                      outline=self.theme_colors[self.theme_var.get()]["text_accent"],
                                                      width=8, style="arc")
        self.timer_text = self.timer_canvas.create_text(center, center, text="", font=("Roboto", 24, "bold"),
                                                        fill=self.theme_colors[self.theme_var.get()]["text_accent"])
        self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
        self.timer_thread.start()

    def run_timer(self):
        while self.timer_remaining > 0 and self.timer_running:
            minutes = self.timer_remaining // 60
            seconds = self.timer_remaining % 60
            try:
                if self.timer_canvas and self.timer_text and self.timer_canvas.winfo_exists():
                    self.timer_canvas.itemconfig(self.timer_text, text=f"{minutes:02d}:{seconds:02d}")
                if self.timer_canvas and self.timer_arc and self.timer_canvas.winfo_exists():
                    percent = self.timer_remaining / self.timer_duration
                    self.timer_canvas.itemconfig(self.timer_arc, extent=-360 * percent)
            except Exception:
                break

            self.timer_remaining -= 1
            self.update()
            time.sleep(1)

        if self.timer_running:
            try:
                if self.timer_canvas and self.timer_text and self.timer_canvas.winfo_exists():
                    self.timer_canvas.itemconfig(self.timer_text, text="00:00")
                if self.timer_canvas and self.timer_arc and self.timer_canvas.winfo_exists():
                    self.timer_canvas.itemconfig(self.timer_arc, extent=0)
            except Exception:
                pass
            self.confirm_response.set(True)
            self.stop_timer()

    def stop_timer(self):
        self.timer_running = False
        if self.timer_thread:
            try:
                self.timer_thread.join(timeout=0.1)
            except Exception:
                pass
            self.timer_thread = None

        if self.timer_canvas:
            try:
                if self.timer_canvas.winfo_exists():
                    self.timer_canvas.pack_forget()
                    self.timer_canvas.delete("all")
            except Exception:
                pass
            self.timer_canvas = None

        self.timer_text = None
        self.timer_arc = None

        if self.timer_label:
            try:
                if self.timer_label.winfo_exists():
                    self.timer_label.pack_forget()
            except Exception:
                pass
            self.timer_label = None

    def clear_trainer_card(self):
        self.trainer_label.pack_forget()
        self.set_label.pack_forget()
        self.button_container.pack_forget()
        self.start_training_button.pack_forget()
        self.trainer_button.pack_forget()
        self.feedback_frame.pack_forget()
        self.feedback_submit_button.pack_forget()
        self.training_confirmation_frame.pack_forget()
        self.stop_timer()

    def start_training_mode(self):
        training_mode = self.training_mode_var.get()
        if not training_mode:
            self._show_error("Оберіть режим тренування.")
            return
        if not self.current_plan:
            self._show_error("План тренування не створено.")
            return
        self.trainer_card.pack(fill="x", padx=8, pady=8)
        self.clear_trainer_card()
        if training_mode == "Тренер":
            self.trainer_label.configure(text="Привіт! Розпочнемо тренування?")
            self.trainer_label.pack(pady=20)
            self.button_container.pack(pady=20)
            self.start_training_button.pack()
            # Ініціалізація статусу вправ
            self.exercise_status = {ex.name: False for ex in self.current_plan.get_generated_plan()}
        else:
            self.get_training_confirmation()

    def get_training_confirmation(self):
        self.clear_trainer_card()
        self.trainer_label.configure(text="Чи проводили ви тренування?")
        self.trainer_label.pack(pady=20)
        self.button_container.pack(pady=20)
        self.training_confirmation_frame.pack()

    def start_trainer_mode(self):
        if not self.current_plan:
            self._show_error("План тренування не створено.")
            return
        self.clear_trainer_card()
        self.trainer = Trainer(self.current_plan, self.user_profile, self.update_trainer_display)
        self.trainer.start_training()

    def update_trainer_display(self, message="", prompt=False, rest=False, feedback=False, show_timer=False,
                              timer_duration=0, set_info=None, exercise_name=None):
        self.clear_trainer_card()

        if show_timer:
            self.start_timer(timer_duration, message)
            return

        self.trainer_label.configure(text=message)
        self.trainer_label.pack(pady=20)

        if set_info:
            self.set_label.configure(text=f"Підхід {set_info['current']} / {set_info['total']}")
            self.set_label.pack(pady=10)

        self.button_container.pack(pady=20)
        if prompt:
            self.trainer_button.pack()
        if feedback:
            self.trainer_label.configure(text="Тренування завершено!\nЯк пройшло тренування?")
            self.feedback_frame.pack()
            self.feedback_submit_button.pack()

    def confirm_trainer_action(self):
        self.confirm_response.set(True)

        should_update_plan = False

        if hasattr(self.trainer, 'current_exercise_name') and self.trainer.current_exercise_name:
            name = self.trainer.current_exercise_name
            current_set = getattr(self.trainer, 'current_set', 1)
            for ex in self.current_plan.get_generated_plan():
                if ex.name == name:
                    if current_set >= ex.sets:
                        self.exercise_status[name] = True
                        should_update_plan = True
                    break

        if should_update_plan:
            self.after(100, lambda: self.display_plan(
                self.plan_manager._format_plan(self.current_plan, self.plan_type_var.get())
            ))

    def submit_feedback(self):
        feedback = self.feedback_var.get()
        if not feedback:
            self._show_error("Оберіть зворотний зв’язок.")
            return


        feedback_messages = {
            "Easy": "Чудово, ви великий молодець! Тренування було легким, можливо, наступного разу спробуйте складніше?",
            "Normal": "Відмінна робота! Тренування пройшло як треба, продовжуйте в тому ж дусі!",
            "Hard": "Шкода, що було важко. Не хвилюйтеся, ми підлаштуємо наступний план, щоб було комфортніше!"
        }


        message = feedback_messages.get(feedback, "Зворотний зв’язок збережено, тренування додано до архіву.")

        self.apply_feedback(feedback)
        self.archive_manager.save_plan_to_archive(self.current_plan, self.plan_type_var.get())
        self.trainer_card.pack_forget()
        self.clear_plan()
        self.profile_manager.save_user_profile(self.user_profile)
        self._show_info("Результати тренування", message)

    def select_location(self, location):
        self.location_var.set(location)
        for loc, info in self.location_buttons.items():
            info["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if loc == location else self.theme_colors[self.theme_var.get()]["button_fg"])
            info["selected"] = (loc == location)

    def select_plan_type(self, plan_type):
        self.plan_type_var.set(plan_type)
        for pt, info in self.plan_type_buttons.items():
            info["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if pt == plan_type else self.theme_colors[self.theme_var.get()]["button_fg"])
            info["selected"] = (pt == plan_type)
        self.update_workout_type_state()

    def select_workout_type(self, workout_type):
        self.workout_type_var.set(workout_type)
        for wt, info in self.workout_type_buttons.items():
            info["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if wt == workout_type else self.theme_colors[self.theme_var.get()]["button_fg"])
            info["selected"] = (wt == workout_type)
        self.update_workout_type_state()

    def select_training_mode(self, training_mode):
        self.training_mode_var.set(training_mode)
        for tm, info in self.training_mode_buttons.items():
            info["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if tm == training_mode else self.theme_colors[self.theme_var.get()]["button_fg"])
            info["selected"] = (tm == training_mode)

    def toggle_muscle_group(self, group):
        if self.muscle_buttons[group]["selected"]:
            self.muscle_groups_var.remove(group.lower())
            self.muscle_buttons[group]["selected"] = False
            self.muscle_buttons[group]["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_fg"])
        else:
            self.muscle_groups_var.append(group.lower())
            self.muscle_buttons[group]["selected"] = True
            self.muscle_buttons[group]["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_active"])

    def select_feedback(self, feedback):
        self.feedback_var.set(feedback)
        for fb, info in self.feedback_buttons.items():
            is_selected = (fb.split()[-1] == feedback)
            info["selected"] = is_selected
            info["button"].configure(
                fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if is_selected else
                self.theme_colors[self.theme_var.get()]["button_fg"],
                border_width=2 if is_selected else 0,
                border_color=self.theme_colors[self.theme_var.get()]["shadow_color"] if is_selected else ""
            )

    def select_training_confirmation(self, confirmation):
        self.training_confirmation_var.set(confirmation)
        for tc, info in self.training_confirmation_buttons.items():
            is_selected = (tc == confirmation)
            info["selected"] = is_selected
            info["button"].configure(
                fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if is_selected else
                self.theme_colors[self.theme_var.get()]["button_fg"],
                border_width=2 if is_selected else 0,
                border_color=self.theme_colors[self.theme_var.get()]["shadow_color"] if is_selected else ""
            )
        if confirmation == "No":
            self.clear_plan()
            self.trainer_card.pack_forget()
        else:
            self.clear_trainer_card()
            self.trainer_label.configure(text="Тренування завершено!\nЯк пройшло тренування?")
            self.trainer_label.pack(pady=20)
            self.button_container.pack(pady=20)
            self.feedback_frame.pack()
            self.feedback_submit_button.pack()


    def update_workout_type_state(self, *args):
        if self.plan_type_var.get() == "Strength":
            for button_info in self.workout_type_buttons.values():
                button_info["button"].configure(state="normal")
            if self.workout_type_var.get() == "Split":
                for button in self.muscle_buttons.values():
                    button["button"].configure(state="normal")
            else:
                for button in self.muscle_buttons.values():
                    button["button"].configure(state="disabled")
                    if button["selected"]:
                        self.muscle_groups_var.remove(button["button"].cget("text").lower())
                        button["selected"] = False
                        button["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_fg"])
        else:
            for button_info in self.workout_type_buttons.values():
                button_info["button"].configure(state="disabled")
            for button in self.muscle_buttons.values():
                button["button"].configure(state="disabled")
                if button["selected"]:
                    self.muscle_groups_var.remove(button["button"].cget("text").lower())
                    button["selected"] = False
                    button["button"].configure(fg_color=self.theme_colors[self.theme_var.get()]["button_fg"])

    def generate_plan(self):
        location = self.location_var.get()
        if not location:
            self._show_error("Оберіть місце тренування.")
            return
        plan_type = self.plan_type_var.get()
        if not plan_type:
            self._show_error("Оберіть тип плану.")
            return
        difficulty = self.user_profile._preferred_difficulty
        try:
            factory = ExerciseFactoryProvider.get_factory(self.user_profile, plan_type, location)
            exercises = factory.create_exercises(self.user_profile, location)
        except ValueError as e:
            self._show_error(str(e))
            return
        if plan_type == "Cardio":
            self.current_plan, plan_data = self.plan_manager.create_cardio_plan(difficulty, exercises, self.user_profile)
            self.display_plan(plan_data)
            self.start_training_mode()
        else:
            workout_type = self.workout_type_var.get()
            if not workout_type:
                self._show_error("Оберіть тип тренування.")
                return
            is_full_body = workout_type == "Full-body"
            muscle_groups = self.user_profile._goal_muscle_groups if is_full_body else self.muscle_groups_var
            if not is_full_body and not self.muscle_groups_var:
                self._show_error("Оберіть хоча б одну м’язову групу.")
                return
            self.current_plan, plan_data = self.plan_manager.create_strength_plan(is_full_body, muscle_groups, difficulty, exercises, self.user_profile)
            self.display_plan(plan_data)
            self.start_training_mode()

    def display_plan(self, plan_data):
        for widget in self.plan_frame_inner.winfo_children():
            widget.destroy()
        for ex in plan_data["exercises"]:
            if ex["name"].startswith("Ціль:"):
                goal_card = ctk.CTkFrame(self.plan_frame_inner,
                                         fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                                         corner_radius=8, height=30)
                goal_card.pack(fill="x", padx=(8, 16), pady=2, expand=False)
                goal_card.pack_propagate(False)
                self.themed_widgets["frames"].append((goal_card, "fg_color", "inner_card_bg"))
                goal_label = ctk.CTkLabel(goal_card, text=ex["name"], font=("Roboto", 14, "bold"),
                                          text_color=self.theme_colors[self.theme_var.get()]["text_color"])
                goal_label.pack(anchor="w", padx=8, pady=2)
                self.themed_widgets["labels"].append((goal_label, "text_color", "text_color"))
                continue
            ex_card = ctk.CTkFrame(self.plan_frame_inner,
                                   fg_color=self.theme_colors[self.theme_var.get()]["exercise_card_bg"],
                                   corner_radius=8)
            ex_card.pack(fill="x", padx=(8, 16), pady=4, expand=True)
            ex_card.grid_columnconfigure(1, weight=1)
            ex_card.grid_columnconfigure(2, minsize=80)
            placeholder = ctk.CTkFrame(ex_card, fg_color="#2ecc71", width=100, height=100)
            placeholder.grid(row=0, column=0, padx=8, pady=8, sticky="nsw")
            self.themed_widgets["frames"].append((placeholder, "fg_color", "exercise_card_bg"))
            details_frame = ctk.CTkFrame(ex_card, fg_color=self.theme_colors[self.theme_var.get()]["exercise_card_bg"])
            details_frame.grid(row=0, column=1, padx=8, pady=8, sticky="nsew")
            name_label = ctk.CTkLabel(details_frame, text=ex["name"], font=("Roboto", 16, "bold"), wraplength=400,
                                      text_color=self.theme_colors[self.theme_var.get()]["text_color"])
            name_label.pack(anchor="w", pady=2)
            self.themed_widgets["labels"].append((name_label, "text_color", "text_color"))
            if ex["details"]:
                details_label = ctk.CTkLabel(details_frame, text=ex["details"], font=("Roboto", 14), wraplength=400,
                                             text_color=self.theme_colors[self.theme_var.get()]["text_color"])
                details_label.pack(anchor="w", pady=2)
                self.themed_widgets["labels"].append((details_label, "text_color", "text_color"))
            if ex["name"] in self.exercise_status and self.exercise_status[ex["name"]]:
                completed_label = ctk.CTkLabel(ex_card, text="✅ Виконано", font=("Roboto", 12),
                                               text_color=self.theme_colors[self.theme_var.get()]["text_accent"])
                completed_label.grid(row=0, column=2, padx=(0, 8), pady=8, sticky="ne")
                self.themed_widgets["labels"].append((completed_label, "text_color", "text_accent"))
            self.themed_widgets["frames"].extend(
                [(ex_card, "fg_color", "exercise_card_bg"), (details_frame, "fg_color", "exercise_card_bg")])
        calories_label = ctk.CTkLabel(self.plan_frame_inner, text=f"Калорії: {plan_data['calories']}",
                                      font=("Roboto", 16, "bold"),
                                      text_color=self.theme_colors[self.theme_var.get()]["text_color"])
        calories_label.pack(anchor="w", pady=8, padx=8)
        self.themed_widgets["labels"].append((calories_label, "text_color", "text_color"))
        self.plan_canvas.configure(
            width=self.display_card.winfo_width() - 20)
        self.plan_canvas.itemconfigure(
            self.plan_canvas.create_window((0, 0), window=self.plan_frame_inner, anchor="nw"),
            width=self.display_card.winfo_width() - 20)

    def clear_plan(self):
        for widget in self.plan_frame_inner.winfo_children():
            widget.destroy()
        self.current_plan = None
        self.exercise_status = {}

    def apply_feedback(self, feedback_input):
        feedback = {"Easy": ExerciseFeedback.EASY, "Normal": ExerciseFeedback.NORMAL, "Hard": ExerciseFeedback.HARD}.get(feedback_input, ExerciseFeedback.NORMAL)
        for exercise in self.current_plan.get_generated_plan():
            self.profile_manager.update_exercise_feedback(self.user_profile, exercise.name, feedback)

    def setup_archive_page(self):
        # Очищення попередніх віджетів
        for widget in self.archive_frame.winfo_children():
            widget.destroy()


        label = ctk.CTkLabel(
            self.archive_frame,
            text="Архів Тренувань",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        label.pack(pady=10)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))


        canvas_container = ctk.CTkFrame(
            self.archive_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        canvas_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.themed_widgets["frames"].append((canvas_container, "fg_color", "main_bg"))


        self.archive_canvas = ctk.CTkCanvas(
            canvas_container,
            bg=self.theme_colors[self.theme_var.get()]["main_bg"],
            highlightthickness=0
        )
        self.archive_canvas.pack(side="left", fill="both", expand=True)
        self.themed_widgets["canvases"].append((self.archive_canvas, "bg", "main_bg"))

        # Scrollbar
        self.archive_scrollbar = ctk.CTkScrollbar(
            canvas_container,
            orientation="vertical",
            command=self.archive_canvas.yview
        )
        self.archive_scrollbar.pack(side="right", fill="y")
        self.archive_canvas.configure(yscrollcommand=self.archive_scrollbar.set)


        self.archive_frame_inner = ctk.CTkFrame(
            self.archive_canvas,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        self.themed_widgets["frames"].append((self.archive_frame_inner, "fg_color", "main_bg"))


        self.archive_window_id = self.archive_canvas.create_window(
            (0, 0),
            window=self.archive_frame_inner,
            anchor="nw"
        )

        def update_scrollregion(event):
            self.archive_canvas.configure(scrollregion=self.archive_canvas.bbox("all"))
            # Оновлення ширини вікна, щоб відповідати ширині canvas
            canvas_width = self.archive_canvas.winfo_width()
            self.archive_canvas.itemconfigure(self.archive_window_id, width=canvas_width)

        self.archive_frame_inner.bind("<Configure>", update_scrollregion)

        clear_button = ctk.CTkButton(
            self.archive_frame,
            text="Очистити Архів",
            font=("Roboto", 14),
            command=self.clear_archive,
            fg_color=self.theme_colors[self.theme_var.get()]["button_active"],
            hover_color=self.theme_colors[self.theme_var.get()]["button_hover"]
        )
        clear_button.pack(side="bottom", pady=(5, 10))
        self.themed_widgets["buttons"].extend([
            (clear_button, "fg_color", "button_active"),
            (clear_button, "hover_color", "button_hover")
        ])

    def update_archive_display(self):

        for widget in self.archive_frame_inner.winfo_children():
            widget.destroy()


        summary = self.archive_manager.get_archived_plans_summary()
        if not summary:
            no_data_label = ctk.CTkLabel(
                self.archive_frame_inner,
                text="Архів порожній.",
                font=("Roboto", 16),
                text_color=self.theme_colors[self.theme_var.get()]["text_color"]
            )
            no_data_label.pack(pady=20)
            self.themed_widgets["labels"].append((no_data_label, "text_color", "text_color"))
        else:
            for entry in summary:

                date_time_parts = entry['date'].split()
                if len(date_time_parts) > 1:
                    date_part = date_time_parts[0].split('-')
                    time_part = date_time_parts[1].split(':')
                    formatted_date = f"{date_part[2]}.{date_part[1]} | {time_part[0]}:{time_part[1]}"
                else:
                    date_part = entry['date'].split('-')
                    formatted_date = f"{date_part[2]}.{date_part[1]}"


                card = ctk.CTkFrame(
                    self.archive_frame_inner,
                    fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                    corner_radius=12
                )
                card.pack(fill="x", padx=20, pady=6)
                card.grid_columnconfigure(0, weight=1)


                inner_frame = ctk.CTkFrame(
                    card,
                    fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                    corner_radius=0
                )
                inner_frame.grid(row=0, column=0, sticky="w", padx=12, pady=12)
                inner_frame.grid_columnconfigure(0, weight=1)


                date_subcard = ctk.CTkFrame(
                    inner_frame,
                    fg_color="#2a2a2a",
                    corner_radius=8
                )
                date_subcard.grid(row=0, column=0, padx=(0, 5), pady=2, sticky="w")
                date_label = ctk.CTkLabel(
                    date_subcard,
                    text=formatted_date,
                    font=("Roboto", 14),
                    text_color="#ffffff",
                    width=100
                )
                date_label.pack(padx=10, pady=5)


                type_subcard = ctk.CTkFrame(
                    inner_frame,
                    fg_color="#2a2a2a",
                    corner_radius=8
                )
                type_subcard.grid(row=0, column=1, padx=5, pady=2, sticky="w")
                type_label = ctk.CTkLabel(
                    type_subcard,
                    text=entry['type'],
                    font=("Roboto", 14),
                    text_color="#ffffff",
                    width=100
                )
                type_label.pack(padx=10, pady=5)


                calories_subcard = ctk.CTkFrame(
                    inner_frame,
                    fg_color="#2a2a2a",
                    corner_radius=8
                )
                calories_subcard.grid(row=0, column=2, padx=(5, 0), pady=2, sticky="w")
                calories_label = ctk.CTkLabel(
                    calories_subcard,
                    text=f"{entry['calories']} ккал",
                    font=("Roboto", 14),
                    text_color="#ffffff",
                    width=100
                )
                calories_label.pack(padx=10, pady=5)


                button = ctk.CTkButton(
                    card,
                    text="Деталі",
                    font=("Roboto", 14),
                    command=lambda i=entry['id'] - 1: self.view_archive_details(i),
                    fg_color=self.theme_colors[self.theme_var.get()]["button_active"],
                    hover_color=self.theme_colors[self.theme_var.get()]["button_hover"],
                    width=100
                )
                button.grid(row=0, column=1, sticky="e", padx=12, pady=12)


                self.themed_widgets["labels"].extend([
                    (date_label, "text_color", "text_color"),
                    (type_label, "text_color", "text_color"),
                    (calories_label, "text_color", "text_color")
                ])
                self.themed_widgets["buttons"].extend([
                    (button, "fg_color", "button_active"),
                    (button, "hover_color", "button_hover")
                ])
                self.themed_widgets["frames"].extend([
                    (card, "fg_color", "inner_card_bg"),
                    (inner_frame, "fg_color", "inner_card_bg"),
                    (date_subcard, "fg_color", "inner_card_bg"),
                    (type_subcard, "fg_color", "inner_card_bg"),
                    (calories_subcard, "fg_color", "inner_card_bg")
                ])


        self.archive_frame_inner.update_idletasks()
        canvas_width = self.archive_canvas.winfo_width()
        self.archive_canvas.configure(scrollregion=self.archive_canvas.bbox("all"))
        self.archive_canvas.itemconfigure(self.archive_window_id, width=canvas_width)

    def view_archive_details(self, index):

        details = self.archive_manager.get_plan_details(index)
        if "error" in details:
            self._show_error(details["error"])
            return


        modal = ctk.CTkToplevel(self)
        modal.transient(self)
        modal.title("Деталі Тренування")
        modal.geometry("600x500")
        modal.configure(fg_color=self.theme_colors[self.theme_var.get()]["main_bg"])
        self.themed_widgets["frames"].append((modal, "fg_color", "main_bg"))


        card = ctk.CTkFrame(
            modal,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"],
            corner_radius=12
        )
        card.pack(fill="both", expand=True, padx=10, pady=10)
        self.themed_widgets["frames"].append((card, "fg_color", "card_bg"))


        label = ctk.CTkLabel(
            card,
            text=f"План: {details['type']}",
            font=("Roboto", 20, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        label.pack(pady=10)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))

        canvas_container = ctk.CTkFrame(
            card,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        canvas_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.themed_widgets["frames"].append((canvas_container, "fg_color", "card_bg"))


        canvas = ctk.CTkCanvas(
            canvas_container,
            bg=self.theme_colors[self.theme_var.get()]["canvas_bg"],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        self.themed_widgets["canvases"].append((canvas, "bg", "canvas_bg"))


        scrollbar = ctk.CTkScrollbar(
            canvas_container,
            orientation="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        exercises_frame = ctk.CTkFrame(
            canvas,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        self.themed_widgets["frames"].append((exercises_frame, "fg_color", "card_bg"))


        canvas_window_id = canvas.create_window(
            (0, 0),
            window=exercises_frame,
            anchor="nw"
        )

        if not details["exercises"]:
            no_ex_label = ctk.CTkLabel(
                exercises_frame,
                text="Немає вправ у цьому плані",
                font=("Roboto", 14, "italic"),
                text_color=self.theme_colors[self.theme_var.get()]["text_color"]
            )
            no_ex_label.pack(pady=10)
            self.themed_widgets["labels"].append((no_ex_label, "text_color", "text_color"))
        else:

            for ex in details["exercises"]:
                ex_card = ctk.CTkFrame(
                    exercises_frame,
                    fg_color=self.theme_colors[self.theme_var.get()]["exercise_card_bg"],
                    corner_radius=8
                )
                ex_card.pack(fill="x", padx=8, pady=4)
                self.themed_widgets["frames"].append((ex_card, "fg_color", "exercise_card_bg"))

                ex_label = ctk.CTkLabel(
                    ex_card,
                    text=ex,
                    font=("Roboto", 14),
                    wraplength=500,
                    text_color=self.theme_colors[self.theme_var.get()]["text_color"],
                    anchor="w",
                    justify="left"
                )
                ex_label.pack(anchor="w", padx=8, pady=6)
                self.themed_widgets["labels"].append((ex_label, "text_color", "text_color"))


        calories_card = ctk.CTkFrame(
            card,
            fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
            corner_radius=8
        )
        calories_card.pack(fill="x", padx=10, pady=5)
        self.themed_widgets["frames"].append((calories_card, "fg_color", "inner_card_bg"))

        calories_label = ctk.CTkLabel(
            calories_card,
            text=f"🔥 Калорії: {details['calories']} ккал",
            font=("Roboto", 16, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        calories_label.pack(pady=8)
        self.themed_widgets["labels"].append((calories_label, "text_color", "text_color"))


        button = ctk.CTkButton(
            card,
            text="Закрити",
            font=("Roboto", 14),
            command=modal.destroy,
            fg_color=self.theme_colors[self.theme_var.get()]["button_active"],
            hover_color=self.theme_colors[self.theme_var.get()]["button_hover"]
        )
        button.pack(pady=10)
        self.themed_widgets["buttons"].extend([
            (button, "fg_color", "button_active"),
            (button, "hover_color", "button_hover")
        ])


        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            canvas.itemconfigure(canvas_window_id, width=canvas_width - 4)

        exercises_frame.bind("<Configure>", update_scrollregion)

        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        modal.grab_set()
        if modal.winfo_exists():
            modal.focus_set()

    def show_plan_details(self, index):
        plan_details = self.archive_manager.get_plan_details(index)
        modal = ctk.CTkToplevel(self)
        modal.transient(self)
        modal.title("Деталі Плану")
        modal.geometry("400x300")
        label = ctk.CTkLabel(modal, text=f"Тип: {plan_details['type']}", font=("Roboto", 16), text_color=self.theme_colors[self.theme_var.get()]["text_color"])
        label.pack(pady=8)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))
        exercises = "\n".join(plan_details['exercises'])
        label_ex = ctk.CTkLabel(modal, text=f"Вправи:\n{exercises}", font=("Roboto", 14), wraplength=350, text_color=self.theme_colors[self.theme_var.get()]["text_color"])
        label_ex.pack(pady=8)
        self.themed_widgets["labels"].append((label_ex, "text_color", "text_color"))
        label_cal = ctk.CTkLabel(modal, text=f"Калорії: {plan_details['calories']}", font=("Roboto", 14), text_color=self.theme_colors[self.theme_var.get()]["text_color"])
        label_cal.pack(pady=8)
        self.themed_widgets["labels"].append((label_cal, "text_color", "text_color"))
        button = ctk.CTkButton(modal, text="OK", font=("Roboto", 14), command=modal.destroy, fg_color=self.theme_colors[self.theme_var.get()]["button_active"], hover_color=self.theme_colors[self.theme_var.get()]["button_hover"])
        button.pack(pady=8)
        self.themed_widgets["buttons"].extend([(button, "fg_color", "button_active"), (button, "hover_color", "button_hover")])

    def clear_archive(self):
        message = self.archive_manager.clear_archive()
        self._show_info("Архів", message)
        self.update_archive_display()

    def setup_statistics_page(self):

        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        title_label = ctk.CTkLabel(
            self.stats_frame,
            text="Статистика по тренуванням",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))

        subtitle_label = ctk.CTkLabel(
            self.stats_frame,
            text="Слідкуйте за прогресом своїх сесій!",
            font=("Roboto", 14),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        subtitle_label.pack(pady=(0, 20))
        self.themed_widgets["labels"].append((subtitle_label, "text_color", "text_color"))

        graph_frame = ctk.CTkFrame(
            self.stats_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"],
            corner_radius=12
        )
        graph_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.themed_widgets["frames"].append((graph_frame, "fg_color", "card_bg"))

        graph_title = ctk.CTkLabel(
            graph_frame,
            text="Кількість калорій (ккал)",
            font=("Roboto", 16, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_accent"]
        )
        graph_title.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((graph_title, "text_color", "text_accent"))

        self.histogram_frame = ctk.CTkFrame(
            graph_frame,
            fg_color="transparent"
        )
        self.histogram_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        bottom_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 10))

        left_card = ctk.CTkFrame(
            bottom_frame,
            height=180,
            corner_radius=12,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        left_card.pack(side="left", expand=True, fill="x", padx=(0, 5))
        left_card.pack_propagate(False)
        self.themed_widgets["frames"].append((left_card, "fg_color", "card_bg"))

        right_card = ctk.CTkFrame(
            bottom_frame,
            height=180,
            corner_radius=12,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        right_card.pack(side="right", expand=True, fill="x", padx=(5, 0))
        right_card.pack_propagate(False)
        self.themed_widgets["frames"].append((right_card, "fg_color", "card_bg"))

        calories_title = ctk.CTkLabel(
            left_card,
            text="🔥 Всього спалено калорій",
            font=("Roboto", 16, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_accent"]
        )
        calories_title.pack(pady=(15, 5))
        self.themed_widgets["labels"].append((calories_title, "text_color", "text_accent"))


        self.total_calories_label = ctk.CTkLabel(
            left_card,
            text="0 ккал",
            font=("Roboto", 20, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        self.total_calories_label.pack(expand=True, pady=(0, 5))
        self.themed_widgets["labels"].append((self.total_calories_label, "text_color", "text_color"))

        self.avg_calories_label = ctk.CTkLabel(
            left_card,
            text="📊 Середня кількість калорій: 0 ккал",
            font=("Roboto", 14),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        self.avg_calories_label.pack(pady=(5, 0))
        self.themed_widgets["labels"].append((self.avg_calories_label, "text_color", "text_color"))

        self.workouts_label = ctk.CTkLabel(
            left_card,
            text="🏃 Загальна кількість тренувань за останній тиждень: 0",
            font=("Roboto", 14),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        self.workouts_label.pack(pady=(5, 15))
        self.themed_widgets["labels"].append((self.workouts_label, "text_color", "text_color"))

        tip_title = ctk.CTkLabel(
            right_card,
            text="💡 Підказки",
            font=("Roboto", 16, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_accent"]
        )
        tip_title.pack(pady=(15, 5))
        self.themed_widgets["labels"].append((tip_title, "text_color", "text_accent"))

        self.tip_label = ctk.CTkLabel(
            right_card,
            text="💪 Чудовий прогрес, продовжуйте в тому ж дусі! Додавайте нові вправи, щоб урізноманітнити тренування та досягти кращих результатів. 😊",
            font=("Roboto", 14),
            wraplength=350,
            justify="center",
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        self.tip_label.pack(expand=True, pady=(0, 15), padx=10)
        self.themed_widgets["labels"].append((self.tip_label, "text_color", "text_color"))

        self.update_statistics_display()

    def update_statistics_display(self):

        for widget in self.histogram_frame.winfo_children():
            widget.destroy()

        archive_data = self.archive_manager.load_archive()
        if not archive_data:
            no_data_label = ctk.CTkLabel(
                self.histogram_frame,
                text="Немає доступних даних для відображення статистики.",
                font=("Roboto", 16),
                text_color=self.theme_colors[self.theme_var.get()]["text_color"]
            )
            no_data_label.pack(expand=True, pady=20)
            self.themed_widgets["labels"].append((no_data_label, "text_color", "text_color"))
            self.total_calories_label.configure(text="0 ккал")
            self.avg_calories_label.configure(text="📊 Середня кількість калорій: 0 ккал")
            self.workouts_label.configure(text="🏃 Загальна кількість тренувань за останній тиждень: 0")
            return

        archive_data = archive_data[-12:]
        max_calories = max(entry.total_calories_burned for entry in archive_data) or 1
        dates = [entry.date.strftime("%d.%m") for entry in archive_data]

        bars_container = ctk.CTkFrame(self.histogram_frame, fg_color="transparent")
        bars_container.pack(fill="both", expand=True, padx=20, pady=20)

        colors = [
            "#10b981", "#34d399", "#6ee7b7", "#a7f3d0",
            "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe",
            "#6b46c1", "#8e44ad", "#9b59b6", "#d1b3e0"
        ]


        for i, entry in enumerate(archive_data):
            percent = entry.total_calories_burned / max_calories
            bar_height = int(percent * 220)


            column = ctk.CTkFrame(bars_container, fg_color="transparent")
            column.pack(side="left", fill="y", expand=True)


            date_label = ctk.CTkLabel(
                column,
                text=dates[i],
                font=("Roboto", 12),
                text_color="#FFFFFF"
            )
            date_label.pack(side="bottom", pady=(0, 5))
            self.themed_widgets["labels"].append((date_label, "text_color", "text_color"))


            bar = ctk.CTkFrame(
                column,
                height=bar_height,
                width=36,
                corner_radius=6,
                fg_color=colors[i % len(colors)]
            )
            bar.pack(side="bottom", fill="x", padx=5)
            self.themed_widgets["frames"].append((bar, "fg_color", "text_accent"))


            cal_label = ctk.CTkLabel(
                column,
                text=str(entry.total_calories_burned),
                font=("Roboto", 12, "bold"),
                text_color=self.theme_colors[self.theme_var.get()]["text_color"]
            )
            cal_label.pack(side="bottom", pady=(5, 0))
            self.themed_widgets["labels"].append((cal_label, "text_color", "text_color"))


        total_calories = sum(entry.total_calories_burned for entry in archive_data)
        self.total_calories_label.configure(text=f"{total_calories} ккал")


        avg_calories = total_calories // len(archive_data) if archive_data else 0
        self.avg_calories_label.configure(text=f"📊 Середня кількість калорій: {avg_calories} ккал")


        from datetime import datetime, timedelta
        one_week_ago = datetime.now() - timedelta(days=7)
        weekly_workouts = len([entry for entry in archive_data
                               if datetime.combine(entry.date, datetime.min.time()) >= one_week_ago])
        self.workouts_label.configure(text=f"🏃 Загальна кількість тренувань за останній тиждень: {weekly_workouts}")

        tip = ""
        if len(archive_data) > 1:
            last = archive_data[-1].total_calories_burned
            prev = archive_data[-2].total_calories_burned

            dates = [entry.date for entry in archive_data]
            is_regular = all((dates[i] - dates[i - 1]).days <= 2 for i in range(1, len(dates)))
            # Перевірка типу тренувань
            last_five_types = [entry.plan_type for entry in archive_data[-5:]]
            mostly_cardio = last_five_types.count("Cardio") > last_five_types.count("Strength")
            mostly_strength = last_five_types.count("Strength") > last_five_types.count("Cardio")

            if last > prev:
                tip = "💪 Чудовий прогрес, продовжуйте в тому ж дусі! Додавайте нові вправи, щоб урізноманітнити тренування та досягти кращих результатів. 😊 Регулярність ключ до успіху!"
            elif last == prev:
                tip = "📈 Стабільні результати, можна трохи підвищити навантаження! Спробуйте додати інтенсивність або тривалість тренувань. 💪"
            else:
                tip = "🌱 Трохи менше результат, але не хвилюйтесь, головне регулярність! Зосередьтеся на відновленні та поступовому прогресі. 😊"


            if not is_regular:
                tip = "⏰ Регулярність — запорука успіху! Намагайтеся тренуватися хоча б раз на 2 дні, щоб підтримувати прогрес. 🏋️"

            elif total_calories > 2000:
                tip = "🔥 Ви спалили понад 2000 калорій, вражаючий результат! Продовжуйте в тому ж дусі та не забувайте про відпочинок! 😴"

            elif mostly_cardio:
                tip = "🏃 Ви віддаєте перевагу кардіо — чудово для витривалості! Спробуйте додати силові тренування, щоб зміцнити м’язи. 💪"
            elif mostly_strength:
                tip = "💪 Ви зосереджені на силових тренуваннях, круто! Додайте кардіо, щоб покращити витривалість і здоров’я серця. 🏃"
        else:
            tip = "🌟 Початок відмінний! Продовжуйте тренуватись регулярно, і результати не забаряться. 💪"

        self.tip_label.configure(text=tip)

    def create_bmi_gauge(self, parent_frame, bmi):

        gauge_frame = ctk.CTkFrame(
            parent_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        gauge_frame.pack(fill="x", padx=20, pady=(9, 0))
        self.themed_widgets["frames"].append((gauge_frame, "fg_color", "main_bg"))

        canvas_width = 500
        canvas_height = 250
        gauge_canvas = ctk.CTkCanvas(
            gauge_frame,
            width=canvas_width,
            height=canvas_height,
            bg=self.theme_colors[self.theme_var.get()]["main_bg"],
            highlightthickness=0
        )
        gauge_canvas.pack()
        self.themed_widgets["canvases"].append((gauge_canvas, "bg", "main_bg"))

        center_x, center_y = canvas_width / 2, canvas_height - 100
        radius = 140

        total_angle = 300

        colors = {
            "underweight": "#10b981",
            "normal": "#3b82f6",
            "overweight": "#6b46c1"
        }

        underweight_angle = total_angle * ((18.5 - 15) / (30 - 15))
        normal_angle = total_angle * ((25 - 18.5) / (30 - 15))
        overweight_angle = total_angle * ((30 - 25) / (30 - 15))

        start_angle = 240


        gauge_canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle, extent=-underweight_angle,
            style="arc", outline=colors["underweight"], width=20
        )

        gauge_canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle - underweight_angle, extent=-normal_angle,
            style="arc", outline=colors["normal"], width=20
        )

        gauge_canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle - underweight_angle - normal_angle, extent=-overweight_angle,
            style="arc", outline=colors["overweight"], width=20
        )

        bmi_label = gauge_canvas.create_text(
            center_x, center_y - 30,
            text=f"ІМТ: {bmi:.1f}",
            font=("Roboto", 28, "bold"),
            fill="#ffffff"
        )

        category = self.profile_manager.get_bmi_category(bmi)
        category_color = (
            colors["underweight"] if bmi < 18.5 else
            colors["normal"] if bmi < 25 else
            colors["overweight"]
        )

        category_label = gauge_canvas.create_text(
            center_x, center_y + 10,
            text=category,
            font=("Roboto", 16),
            fill=category_color
        )

        bmi_normalized = max(15, min(30, bmi))
        pointer_angle = start_angle - total_angle * ((bmi_normalized - 15) / (30 - 15))
        pointer_angle_rad = math.radians(pointer_angle)

        outer_radius = radius + 20
        triangle_base = 16
        triangle_height = 12
        p1_x = center_x + (outer_radius - triangle_height) * math.cos(pointer_angle_rad)
        p1_y = center_y - (outer_radius - triangle_height) * math.sin(pointer_angle_rad)
        p2_x = center_x + outer_radius * math.cos(pointer_angle_rad) - (triangle_base / 2) * math.sin(pointer_angle_rad)
        p2_y = center_y - outer_radius * math.sin(pointer_angle_rad) - (triangle_base / 2) * math.cos(pointer_angle_rad)
        p3_x = center_x + outer_radius * math.cos(pointer_angle_rad) + (triangle_base / 2) * math.sin(pointer_angle_rad)
        p3_y = center_y - outer_radius * math.sin(pointer_angle_rad) + (triangle_base / 2) * math.cos(pointer_angle_rad)

        gauge_canvas.create_polygon(
            p1_x, p1_y, p2_x, p2_y, p3_x, p3_y,
            fill="#ffffff"
        )

        legend_frame = ctk.CTkFrame(gauge_frame, fg_color=self.theme_colors[self.theme_var.get()]["main_bg"])
        legend_frame.pack(pady=(8, 0))
        self.themed_widgets["frames"].append((legend_frame, "fg_color", "main_bg"))

        legend_items = [
            (colors["underweight"], "Недостатня вага (<18.5)"),
            (colors["normal"], "Нормальна вага (18.5-25)"),
            (colors["overweight"], "Надмірна вага (>25)")
        ]

        for color, text in legend_items:
            item_frame = ctk.CTkFrame(legend_frame, fg_color="transparent")
            item_frame.pack(side="left", padx=10)

            color_box = ctk.CTkFrame(
                item_frame,
                width=14,
                height=14,
                corner_radius=3,
                fg_color=color
            )
            color_box.pack(side="left", padx=(0, 5))

            text_label = ctk.CTkLabel(
                item_frame,
                text = text,
                font=("Arial", 12, "bold"),
                text_color="#ffffff"
            )
            text_label.pack(side="left")

        return gauge_frame

    def setup_profile_page(self):

        for widget in self.profile_frame.winfo_children():
            widget.destroy()
        self.profile_inputs = {}

        title_label = ctk.CTkLabel(
            self.profile_frame,
            text="Загальна інформація",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))


        bmi = self.profile_manager.calculate_bmi(self.user_profile)
        self.create_bmi_gauge(self.profile_frame, bmi)


        profile_cards_frame = ctk.CTkFrame(
            self.profile_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        profile_cards_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.themed_widgets["frames"].append((profile_cards_frame, "fg_color", "main_bg"))


        profile_data = [
            ("🚻", "Стать", self.user_profile._gender),
            ("⚖️", "Вага", f"{self.user_profile._weight} кг"),
            ("📏", "Зріст", f"{self.user_profile._height} см"),
            ("🔢", "Рівень підготовки", str(self.user_profile._fitness_level)),
            ("💪", "Цільові м'язові групи", ", ".join(self.user_profile._goal_muscle_groups)),
            ("🎮", "Складність", self.user_profile._preferred_difficulty)
        ]

        for i, (emoji, key, value) in enumerate(profile_data):
            card = ctk.CTkFrame(
                profile_cards_frame,
                fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                corner_radius=8
            )
            card.pack(fill="x", padx=20, pady=3)
            card.grid_columnconfigure((0, 1), weight=1)
            self.themed_widgets["frames"].append((card, "fg_color", "inner_card_bg"))

            key_frame = ctk.CTkFrame(
                card,
                fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                corner_radius=0
            )
            key_frame.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")
            self.themed_widgets["frames"].append((key_frame, "fg_color", "inner_card_bg"))


            emoji_label = ctk.CTkLabel(
                key_frame,
                text=emoji,
                font=("Roboto", 18),
                text_color="#ffffff"
            )
            emoji_label.pack(side="left", padx=5)
            self.themed_widgets["labels"].append((emoji_label, "text_color", "text_color"))

            key_label = ctk.CTkLabel(
                key_frame,
                text=key,
                font=("Roboto", 14, "bold"),
                text_color="#ffffff",
                anchor="w"
            )
            key_label.pack(side="left", padx=(5, 0), pady=2)
            self.themed_widgets["labels"].append((key_label, "text_color", "text_color"))

            value_label = ctk.CTkLabel(
                card,
                text=str(value),
                font=("Roboto", 14, "bold"),
                text_color="#ffffff",
                padx=10,
                pady=4
            )
            value_label.grid(row=0, column=1, padx=(5, 10), pady=8, sticky="e")
            self.themed_widgets["labels"].append((value_label, "text_color", "text_color"))

        button_row = ctk.CTkFrame(
            self.profile_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        button_row.pack(pady=10)
        self.themed_widgets["frames"].append((button_row, "fg_color", "main_bg"))

        edit_button = ctk.CTkButton(
            button_row,
            text="Редагувати",
            font=("Roboto", 14, "bold"),
            command=self.edit_profile,
            fg_color="#10b981",
            hover_color="#059669",
            corner_radius=8
        )
        edit_button.pack(side="left", padx=10)
        self.themed_widgets["buttons"].extend([
            (edit_button, "fg_color", "button_active"),
            (edit_button, "hover_color", "button_hover")
        ])

    def update_profile_display(self):

        for widget in self.profile_frame.winfo_children():
            widget.destroy()
        self.profile_inputs = {}


        title_label = ctk.CTkLabel(
            self.profile_frame,
            text="Загальна інформація",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))


        bmi = self.profile_manager.calculate_bmi(self.user_profile)
        self.create_bmi_gauge(self.profile_frame, bmi)


        profile_cards_frame = ctk.CTkFrame(
            self.profile_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        profile_cards_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.themed_widgets["frames"].append((profile_cards_frame, "fg_color", "main_bg"))


        profile_data = [
            ("🚻", "Стать", self.user_profile._gender),
            ("⚖️", "Вага", f"{self.user_profile._weight} кг"),
            ("📏", "Зріст", f"{self.user_profile._height} см"),
            ("🔢", "Рівень підготовки", str(self.user_profile._fitness_level)),
            ("💪", "Цільові м'язові групи", ", ".join(self.user_profile._goal_muscle_groups)),
            ("🎮", "Складність", self.user_profile._preferred_difficulty)
        ]

        for i, (emoji, key, value) in enumerate(profile_data):
            card = ctk.CTkFrame(
                profile_cards_frame,
                fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                corner_radius=8
            )
            card.pack(fill="x", padx=20, pady=3)
            card.grid_columnconfigure((0, 1), weight=1)
            self.themed_widgets["frames"].append((card, "fg_color", "inner_card_bg"))


            key_frame = ctk.CTkFrame(
                card,
                fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                corner_radius=0
            )
            key_frame.grid(row=0, column=0, padx=(10, 5), pady=6, sticky="w")
            self.themed_widgets["frames"].append((key_frame, "fg_color", "inner_card_bg"))


            emoji_label = ctk.CTkLabel(
                key_frame,
                text=emoji,
                font=("Roboto", 18),
                text_color="#ffffff"
            )
            emoji_label.pack(side="left", padx=5)
            self.themed_widgets["labels"].append((emoji_label, "text_color", "text_color"))


            key_label = ctk.CTkLabel(
                key_frame,
                text=key,
                font=("Roboto", 14, "bold"),
                text_color="#ffffff",
                anchor="w"
            )
            key_label.pack(side="left", padx=(5, 0), pady=2)
            self.themed_widgets["labels"].append((key_label, "text_color", "text_color"))


            value_label = ctk.CTkLabel(
                card,
                text=str(value),
                font=("Roboto", 14, "bold"),
                text_color="#ffffff",
                padx=10,
                pady=4
            )
            value_label.grid(row=0, column=1, padx=(5, 10), pady=8, sticky="e")
            self.themed_widgets["labels"].append((value_label, "text_color", "text_color"))

        button_row = ctk.CTkFrame(
            self.profile_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        button_row.pack(pady=10)
        self.themed_widgets["frames"].append((button_row, "fg_color", "main_bg"))

        edit_button = ctk.CTkButton(
            button_row,
            text="Редагувати",
            font=("Roboto", 14, "bold"),
            command=self.edit_profile,
            fg_color="#10b981",
            hover_color="#059669",
            corner_radius=8
        )
        edit_button.pack(side="left", padx=10)
        self.themed_widgets["buttons"].extend([
            (edit_button, "fg_color", "button_active"),
            (edit_button, "hover_color", "button_hover")
        ])

    def edit_profile(self):
        modal = ctk.CTkToplevel(self)
        modal.transient(self)
        modal.title("Редагувати Профіль")
        modal.geometry("500x500")
        modal.configure(fg_color=self.theme_colors[self.theme_var.get()]["main_bg"])
        self.themed_widgets["frames"].append((modal, "fg_color", "main_bg"))

        inputs = {}
        selected_muscles = self.user_profile._goal_muscle_groups.copy() if self.user_profile._goal_muscle_groups else []

        title_label = ctk.CTkLabel(
            modal, text="Редагувати профіль", font=("Roboto", 20, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=10)
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))

        gender_frame = ctk.CTkFrame(modal, fg_color="transparent")
        gender_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(gender_frame, text="🚻 Стать", font=("Roboto", 14), text_color="#ffffff").pack(side="left", padx=5)
        inputs["gender"] = ctk.CTkOptionMenu(
            gender_frame, values=["Male", "Female"], font=("Roboto", 14),
            fg_color=self.theme_colors[self.theme_var.get()]["option_menu_fg"],
            button_color=self.theme_colors[self.theme_var.get()]["option_menu_button"],
            variable=ctk.StringVar(value=self.user_profile._gender)
        )
        inputs["gender"].pack(side="right", padx=5, fill="x", expand=True)
        self.themed_widgets["option_menus"].extend([
            (inputs["gender"], "fg_color", "option_menu_fg"),
            (inputs["gender"], "button_color", "option_menu_button")
        ])

        weight_frame = ctk.CTkFrame(modal, fg_color="transparent")
        weight_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(weight_frame, text="⚖️ Вага (кг)", font=("Roboto", 14), text_color="#ffffff").pack(side="left",
                                                                                                        padx=5)
        inputs["weight"] = ctk.CTkEntry(weight_frame, font=("Roboto", 14))
        inputs["weight"].insert(0, str(self.user_profile._weight))
        inputs["weight"].pack(side="right", padx=5, fill="x", expand=True)

        height_frame = ctk.CTkFrame(modal, fg_color="transparent")
        height_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(height_frame, text="📏 Зріст (см)", font=("Roboto", 14), text_color="#ffffff").pack(side="left",
                                                                                                        padx=5)
        inputs["height"] = ctk.CTkEntry(height_frame, font=("Roboto", 14))
        inputs["height"].insert(0, str(self.user_profile._height))
        inputs["height"].pack(side="right", padx=5, fill="x", expand=True)

        fitness_frame = ctk.CTkFrame(modal, fg_color="transparent")
        fitness_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(fitness_frame, text="🔢 Рівень підготовки", font=("Roboto", 14), text_color="#ffffff").pack(
            side="left", padx=5)
        inputs["fitness_level"] = ctk.CTkSegmentedButton(
            fitness_frame, values=["1", "2", "3", "4", "5"], font=("Roboto", 14),
            selected_color=self.theme_colors[self.theme_var.get()]["button_active"],
            selected_hover_color=self.theme_colors[self.theme_var.get()]["button_hover"],
            variable=ctk.StringVar(value=str(self.user_profile._fitness_level))
        )
        inputs["fitness_level"].pack(side="right", padx=5, fill="x", expand=True)
        self.themed_widgets["segmented_buttons"].extend([
            (inputs["fitness_level"], "selected_color", "button_active"),
            (inputs["fitness_level"], "selected_hover_color", "button_hover")
        ])

        muscles_frame = ctk.CTkFrame(modal, fg_color="transparent")
        muscles_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(muscles_frame, text="💪 М’язові групи", font=("Roboto", 14), text_color="#ffffff").pack(anchor="w",
                                                                                                            padx=5)

        muscles_grid = ctk.CTkFrame(modal, fg_color="transparent")
        muscles_grid.pack(fill="x", padx=20, pady=5)

        muscle_groups = ["Arms", "Chest", "Back", "Legs", "Shoulders", "Core"]
        inputs["muscle_groups"] = []

        for i, group in enumerate(muscle_groups):
            var = ctk.BooleanVar(value=group in selected_muscles)
            button = ctk.CTkButton(
                muscles_grid, text=group, font=("Roboto", 14),
                fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if var.get() else
                self.theme_colors[self.theme_var.get()]["button_fg"],
                hover_color=self.theme_colors[self.theme_var.get()]["button_hover"]
            )

            button.configure(
                command=lambda g=group, v=var, b=button: self.toggle_muscle_selection(g, v, inputs["muscle_groups"], b))
            button.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")
            inputs["muscle_groups"].append((group, var, button))
            self.themed_widgets["buttons"].append(
                (button, "fg_color", "button_active" if var.get() else "button_fg", "hover_color", "button_hover")
            )

        muscles_grid.grid_columnconfigure((0, 1, 2), weight=1)

        difficulty_frame = ctk.CTkFrame(modal, fg_color="transparent")
        difficulty_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(difficulty_frame, text="🎮 Складність", font=("Roboto", 14), text_color="#ffffff").pack(side="left",
                                                                                                            padx=5)
        inputs["difficulty"] = ctk.CTkOptionMenu(
            difficulty_frame, values=["Easy", "Medium", "Hard"], font=("Roboto", 14),
            fg_color=self.theme_colors[self.theme_var.get()]["option_menu_fg"],
            button_color=self.theme_colors[self.theme_var.get()]["option_menu_button"],
            variable=ctk.StringVar(value=self.user_profile._preferred_difficulty)
        )
        inputs["difficulty"].pack(side="right", padx=10, fill="x", expand=True)
        self.themed_widgets["option_menus"].extend([
            (inputs["difficulty"], "fg_color", "option_menu_fg"),
            (inputs["difficulty"], "button_color", "option_menu_button")
        ])

        buttons_frame = ctk.CTkFrame(modal, fg_color="transparent")
        buttons_frame.pack(pady=20)
        save_button = ctk.CTkButton(
            buttons_frame, text="Зберегти", font=("Roboto", 14, "bold"),
            command=lambda: self.save_profile(inputs, modal),
            fg_color="#10b981", hover_color="#059669", corner_radius=8
        )
        save_button.pack(side="left", padx=10)
        self.themed_widgets["buttons"].append((save_button, "fg_color", "button_active", "hover_color", "button_hover"))

        cancel_button = ctk.CTkButton(
            buttons_frame,
            text="Скасувати", font=("Roboto", 14, "bold"),
            command=modal.destroy,
            fg_color="#ef4444", hover_color="#dc2626", corner_radius=8
        )
        cancel_button.pack(side="left", padx=10)
        self.themed_widgets["buttons"].append(
            (cancel_button, "fg_color", "button_active", "hover_color", "button_hover"))

        modal.grab_set()
        modal.focus_set()

    def toggle_muscle_selection(self, group, var, muscle_inputs, button):
        var.set(not var.get())
        button.configure(
            fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if var.get() else
            self.theme_colors[self.theme_var.get()]["button_fg"]
        )
        for i, (w, attr, color_key, *extra) in enumerate(self.themed_widgets["buttons"]):
            if w == button and attr == "fg_color":
                self.themed_widgets["buttons"][i] = (
                    w, "fg_color", "button_active" if var.get() else "button_fg", *extra
                )
                break

    def save_profile(self, inputs, modal):
        profile_inputs = {
            "gender": inputs["gender"].get(),
            "weight": inputs["weight"].get(),
            "height": inputs["height"].get(),
            "fitness_level": inputs["fitness_level"].get(),
            "muscle_groups": [g for g, v, _ in inputs["muscle_groups"] if v.get()],
            "difficulty": inputs["difficulty"].get()
        }
        result = self.profile_manager.fill_user_profile(self.user_profile, profile_inputs)
        if result is True:
            self.update_profile_display()
            modal.destroy()
        else:
            self._show_error(result)

    def delete_profile(self):
        self.profile_manager.delete_user_profile()
        self.user_profile = UserProfile()
        self.update_profile_display()

    def _show_error(self, message):
        modal = ctk.CTkToplevel(self)
        modal.transient(self)
        modal.title("Помилка")
        modal.geometry("400x200")
        modal.configure(fg_color=self.theme_colors[self.theme_var.get()]["main_bg"])
        self.themed_widgets["frames"].append((modal, "fg_color", "main_bg"))

        label = ctk.CTkLabel(
            modal,
            text=message,
            font=("Roboto", 14),
            wraplength=350,
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        label.pack(pady=20)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))

        button = ctk.CTkButton(
            modal,
            text="OK",
            font=("Roboto", 14),
            command=modal.destroy,
            fg_color=self.theme_colors[self.theme_var.get()]["button_active"],
            hover_color=self.theme_colors[self.theme_var.get()]["button_hover"]
        )
        button.pack(pady=8)
        self.themed_widgets["buttons"].append(
            (button, "fg_color", "button_active", "hover_color", "button_hover")
        )

        modal.grab_set()
        if modal.winfo_exists():
            modal.focus_set()

    def _show_info(self, title, message):
        modal = ctk.CTkToplevel(self)
        modal.transient(self)
        modal.title(title)
        modal.geometry("400x200")
        modal.configure(fg_color=self.theme_colors[self.theme_var.get()]["main_bg"])
        self.themed_widgets["frames"].append((modal, "fg_color", "main_bg"))

        label = ctk.CTkLabel(
            modal,
            text=message,
            font=("Roboto", 14),
            wraplength=350,
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        label.pack(pady=20)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))

        button = ctk.CTkButton(
            modal,
            text="OK",
            font=("Roboto", 14),
            command=modal.destroy,
            fg_color=self.theme_colors[self.theme_var.get()]["button_active"],
            hover_color=self.theme_colors[self.theme_var.get()]["button_hover"]
        )
        button.pack(pady=8)
        self.themed_widgets["buttons"].append(
            (button, "fg_color", "button_active", "hover_color", "button_hover")
        )

        modal.grab_set()
        if modal.winfo_exists():
            modal.focus_set()

    def quit_application(self):
        self.destroy()


if __name__ == "__main__":
    app = TrainingApplication()
    app.mainloop()