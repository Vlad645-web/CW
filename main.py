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


# Налаштування теми customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Enums для зворотного зв’язку
class ExerciseFeedback(Enum):
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"


# Enums для зворотного зв’язку
class ExerciseFeedback(Enum):
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"


# Модель даних для профілю користувача
class UserProfile:
    def __init__(self):
        self._fitness_level = 1
        self._preferred_difficulty = "Medium"
        self._weight = 70.0
        self._height = 170.0
        self._gender = "Male"
        self._goal_muscle_groups = []
        self._last_strength_values = {}
        self._exercise_feedback = {}
        self._tk_root = None

    @property
    def fitness_level(self):
        return self._fitness_level

    @fitness_level.setter
    def fitness_level(self, value):
        if 1 <= value <= 10:
            self._fitness_level = value

    def to_dict(self):
        return {
            "FitnessLevel": self._fitness_level,
            "PreferredDifficulty": self._preferred_difficulty,
            "Weight": self._weight,
            "Height": self._height,
            "Gender": self._gender,
            "GoalMuscleGroups": self._goal_muscle_groups,
            "LastStrengthValues": self._last_strength_values,
            "ExerciseFeedback": {k: v.value for k, v in self._exercise_feedback.items()}
        }

    @classmethod
    def from_dict(cls, data):
        profile = cls()
        profile._fitness_level = data.get("FitnessLevel", 1)
        profile._preferred_difficulty = data.get("PreferredDifficulty", "Medium")
        profile._weight = data.get("Weight", 70.0)
        profile._height = data.get("Height", 170.0)
        profile._gender = data.get("Gender", "Male")
        profile._goal_muscle_groups = data.get("GoalMuscleGroups", [])
        profile._last_strength_values = data.get("LastStrengthValues", {})
        profile._exercise_feedback = {
            k: ExerciseFeedback(v) for k, v in data.get("ExerciseFeedback", {}).items()
        }
        return profile


class Exercise:
    def __init__(self, name, exercise_type, properties, equipment="Bodyweight", met=0):
        self.name = name
        self.type = exercise_type
        self.properties = properties
        self.equipment = equipment
        self.met = met
        self.distance = 0
        self.duration = 0
        self.intensity = ""
        self.sets = 0
        self.repeats = 0
        self.working_weight = 0
        self.rest = 0
        self.recommended_speed = None
        self.recommended_frequency = None
        self.max_weight = 0
        self.max_distance = 0

    def __str__(self):
        equipment_display = f", Обладнання: {self.equipment}" if self.equipment != "Bodyweight" else ""
        if self.type == "cardio":
            if self.properties == "dynamic":
                return (f"{self.name} (Відстань: {self.distance} км, Тривалість: {self.duration} хв, "
                        f"Інтенсивність: {self.intensity}{equipment_display}, "
                        f"Швидкість: {self.recommended_speed} км/год, Частота: {self.recommended_frequency} уд/хв)")
            return (f"{self.name} (Тривалість: {self.duration} хв, Інтенсивність: {self.intensity}{equipment_display}, "
                    f"Частота: {self.recommended_frequency} уд/хв)")
        if self.equipment != "Bodyweight" and self.working_weight != 0:
            return (f"{self.name} (Підходи: {self.sets}, Повторення: {self.repeats}, Відпочинок: {self.rest} хв, "
                    f"Вага: {self.working_weight} кг{equipment_display})")
        return f"{self.name} (Підходи: {self.sets}, Повторення: {self.repeats}, Відпочинок: {self.rest} хв{equipment_display})"


class TrainingArchiveEntry:
    def __init__(self, plan_type, generated_plan, total_calories_burned, date):
        self.plan_type = plan_type
        self.generated_plan = generated_plan
        self.total_calories_burned = total_calories_burned
        self.date = date

    def to_dict(self):
        return {
            "PlanType": self.plan_type,
            "GeneratedPlan": [self._exercise_to_dict(ex) for ex in self.generated_plan],
            "TotalCaloriesBurned": self.total_calories_burned,
            "Date": self.date.strftime("%Y-%m-%d %H:%M:%S")
        }

    @classmethod
    def from_dict(cls, data):
        exercises = [cls._dict_to_exercise(ex) for ex in data["GeneratedPlan"]]
        return cls(
            data["PlanType"],
            exercises,
            data["TotalCaloriesBurned"],
            datetime.strptime(data["Date"], "%Y-%m-%d %H:%M:%S")
        )

    @staticmethod
    def _exercise_to_dict(exercise):
        return {
            "Name": exercise.name,
            "Type": exercise.type,
            "Properties": exercise.properties,
            "Equipment": exercise.equipment,
            "MET": exercise.met,
            "Distance": exercise.distance,
            "Duration": exercise.duration,
            "Intensity": exercise.intensity,
            "Sets": exercise.sets,
            "Repeats": exercise.repeats,
            "WorkingWeight": exercise.working_weight,
            "Rest": exercise.rest,
            "RecommendedSpeed": exercise.recommended_speed,
            "RecommendedFrequency": exercise.recommended_frequency,
            "MaxWeight": exercise.max_weight,
            "MaxDistance": exercise.max_distance
        }

    @staticmethod
    def _dict_to_exercise(data):
        ex = Exercise(
            data["Name"],
            data["Type"],
            data["Properties"],
            data["Equipment"],
            data["MET"]
        )
        ex.distance = data["Distance"]
        ex.duration = data["Duration"]
        ex.intensity = data["Intensity"]
        ex.sets = data["Sets"]
        ex.repeats = data["Repeats"]
        ex.working_weight = data["WorkingWeight"]
        ex.rest = data["Rest"]
        ex.recommended_speed = data["RecommendedSpeed"]
        ex.recommended_frequency = data["RecommendedFrequency"]
        ex.max_weight = data["MaxWeight"]
        ex.max_distance = data["MaxDistance"]
        return ex


class TrainingPlan(ABC):
    def __init__(self, user_profile):
        self.user_profile = user_profile
        self.generated_plan = []
        self.total_calories_burned = 0

    def get_generated_plan(self):
        return self.generated_plan

    @abstractmethod
    def generate_plan(self, difficulty, exercises):
        pass

    @abstractmethod
    def calculate_total_calories(self, selected_exercises, difficulty):
        pass

    @abstractmethod
    def set_exercise_parameters(self, exercises, difficulty):
        pass

    @abstractmethod
    def calculate_calories_per_exercise(self, exercise):
        pass


class StrengthPlan(TrainingPlan):
    def __init__(self, muscle_groups, user_profile):
        super().__init__(user_profile)
        self.muscle_groups = muscle_groups

    def generate_plan(self, difficulty, exercises):
        selected_exercises = self.select_exercises(difficulty, exercises)
        self.set_exercise_parameters(selected_exercises, difficulty)
        self.generated_plan = selected_exercises
        self.calculate_total_calories(selected_exercises, difficulty)

    @abstractmethod
    def select_exercises(self, difficulty, exercises):
        pass

    def set_exercise_parameters(self, exercises, difficulty):
        rand = random.Random()
        for exercise in exercises:
            exercise.sets = self._get_sets(difficulty, rand)
            exercise.repeats = self._get_repeats(difficulty, rand)
            exercise.rest = self._get_rest_time(difficulty)
            if exercise.equipment != "Bodyweight":
                if exercise.name not in self.user_profile._last_strength_values:
                    exercise.working_weight = self._get_initial_weight(difficulty, exercise.max_weight)
                else:
                    exercise.working_weight = self._adjust_weight_based_on_feedback(exercise)
                self.user_profile._last_strength_values[exercise.name] = exercise.working_weight

    def _adjust_weight_based_on_feedback(self, exercise):
        if exercise.name in self.user_profile._last_strength_values:
            current_weight = self.user_profile._last_strength_values[exercise.name]
            if exercise.name in self.user_profile._exercise_feedback:
                feedback = self.user_profile._exercise_feedback[exercise.name]
                return {
                    ExerciseFeedback.EASY: int(current_weight * 1.3),
                    ExerciseFeedback.NORMAL: int(current_weight),
                    ExerciseFeedback.HARD: int(current_weight * 0.8)
                }.get(feedback, 0)
        return 0

    def _get_sets(self, difficulty, rand):
        return {
            "Easy": rand.randint(1, 2),
            "Medium": rand.randint(1, 2),
            "Hard": rand.randint(1, 2)
        }.get(difficulty, 4)

    def _get_repeats(self, difficulty, rand):
        return {
            "Easy": rand.randint(10, 13),
            "Medium": rand.randint(8, 11),
            "Hard": rand.randint(6, 9)
        }.get(difficulty, 10)

    def _get_rest_time(self, difficulty):
        return {
            "Easy": 1,
            "Medium": 1,
            "Hard": 1
        }.get(difficulty, 2)

    def _get_initial_weight(self, difficulty, max_weight):
        weight = {
            "Easy": max_weight * 0.4,
            "Medium": max_weight * 0.6,
            "Hard": max_weight * 0.9
        }.get(difficulty, max_weight * 0.5)
        return int(weight)

    def calculate_calories_per_exercise(self, exercise):
        weight_in_kg = self.user_profile._weight
        total_reps = exercise.sets * exercise.repeats
        calories = exercise.met * weight_in_kg * total_reps / 1000.0
        return int(round(calories))

    def calculate_total_calories(self, selected_exercises, difficulty):
        total_calories = 0
        for exercise in selected_exercises:
            total_calories += self.calculate_calories_per_exercise(exercise) * exercise.sets
        self.total_calories_burned = total_calories
        return total_calories

    @abstractmethod
    def get_exercises_per_group(self, difficulty):
        pass


class CardioPlan(TrainingPlan):
    def generate_plan(self, difficulty, exercises):
        number_of_exercises = self._get_number_of_exercises(difficulty)
        selected_exercises = random.sample(exercises, min(number_of_exercises, len(exercises)))
        if not selected_exercises:
            self._show_error("Немає доступних кардіо вправ.")
            return
        self.set_exercise_parameters(selected_exercises, difficulty)
        self.generated_plan = selected_exercises
        self.calculate_total_calories(selected_exercises, difficulty)

    def _get_number_of_exercises(self, difficulty):
        return {
            "Easy": 2,
            "Medium": 3,
            "Hard": 4
        }.get(difficulty, 3)

    def set_exercise_parameters(self, exercises, difficulty):
        for exercise in exercises:
            exercise.intensity = self._get_intensity(difficulty)
            if exercise.properties == "dynamic":
                exercise.distance = self._get_distance(difficulty, exercise.max_distance)
                exercise.duration = self._calculate_dynamic_duration(exercise.distance, exercise.recommended_speed,
                                                                     difficulty)
                exercise.recommended_speed = self._adjust_speed_based_on_difficulty(exercise.recommended_speed,
                                                                                    difficulty)
                exercise.recommended_frequency = self._adjust_frequency_based_on_difficulty(
                    exercise.recommended_frequency, difficulty)
            elif exercise.properties == "static":
                exercise.duration = self._get_static_duration(difficulty)
                exercise.recommended_frequency = self._adjust_frequency_based_on_difficulty(
                    exercise.recommended_frequency, difficulty)

    def _get_intensity(self, difficulty):
        return {
            "Easy": "Низька",
            "Medium": "Середня",
            "Hard": "Висока"
        }.get(difficulty, "Середня")

    def _get_distance(self, difficulty, max_distance):
        if not max_distance:
            return 0
        return {
            "Easy": max_distance * 0.5,
            "Medium": max_distance * 0.75,
            "Hard": max_distance
        }.get(difficulty, max_distance)

    def _calculate_dynamic_duration(self, distance, speed, difficulty):
        if not speed or speed <= 0:
            return 0
        adjusted_speed = speed * 1.2 if difficulty == "Hard" else speed
        return int(round(distance / adjusted_speed * 60))

    def _adjust_speed_based_on_difficulty(self, recommended_speed, difficulty):
        if recommended_speed is None:
            return None
        adjusted_speed = recommended_speed * 1.2 if difficulty == "Hard" else recommended_speed
        return round(adjusted_speed)

    def _adjust_frequency_based_on_difficulty(self, recommended_frequency, difficulty):
        if recommended_frequency is None:
            return None
        return int(recommended_frequency * 1.2) if difficulty == "Hard" else recommended_frequency

    def _get_static_duration(self, difficulty):
        return {
            "Easy": 10,
            "Medium": 15,
            "Hard": 20
        }.get(difficulty, 15)

    def calculate_calories_per_exercise(self, exercise):
        weight_in_kg = self.user_profile._weight
        hours = exercise.duration / 60.0
        if hours <= 0:
            return 0
        calories = exercise.met * weight_in_kg * hours
        return int(round(calories))

    def calculate_total_calories(self, selected_exercises, difficulty):
        total_calories = 0
        for exercise in selected_exercises:
            total_calories += self.calculate_calories_per_exercise(exercise)
        self.total_calories_burned = total_calories
        return total_calories

    def _show_error(self, message):
        ctk.CTkToplevel(self.user_profile._tk_root).title("Помилка")
        ctk.CTkLabel(master=self.user_profile._tk_root, text=message).pack(pady=10)
        ctk.CTkButton(master=self.user_profile._tk_root, text="OK", command=self.user_profile._tk_root.destroy).pack(
            pady=10)


class FullBodyPlan(StrengthPlan):
    def select_exercises(self, difficulty, exercises):
        selected_exercises = []
        muscle_groups = list(set(ex.properties for ex in exercises))
        rand = random.Random()
        for group in muscle_groups:
            group_exercises = [ex for ex in exercises if ex.properties == group]
            selected = rand.sample(group_exercises, min(self.get_exercises_per_group(difficulty), len(group_exercises)))
            selected_exercises.extend(selected)
        return selected_exercises

    def get_exercises_per_group(self, difficulty):
        return 2 if difficulty == "Easy" else 3


class SplitPlan(StrengthPlan):
    def select_exercises(self, difficulty, exercises):
        selected_exercises = []
        rand = random.Random()
        for group in self.muscle_groups:
            group_exercises = [ex for ex in exercises if ex.properties.lower() == group.lower()]
            selected = rand.sample(group_exercises, min(self.get_exercises_per_group(difficulty), len(group_exercises)))
            selected_exercises.extend(selected)
        return selected_exercises

    def get_exercises_per_group(self, difficulty):
        return 3 if difficulty == "Easy" else 4


class IExerciseFactory(ABC):
    @abstractmethod
    def create_exercises(self, user_profile, training_location):
        pass


class GymStrengthExercisesForMenFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Жим лежачи", "strength", "chest", "Barbell", 4.0),
            Exercise("Жим під нахилом", "strength", "chest", "Barbell", 4.0),
            Exercise("Присідання", "strength", "legs", "Barbell", 5.0),
            Exercise("Тяга штанги", "strength", "back", "Barbell", 5.0),
        ]
        for ex in exercises:
            max_weights = {
                "Жим лежачи": 80,
                "Жим під нахилом": 70,
                "Присідання": 100,
                "Тяга штанги": 120,
            }
            ex.max_weight = max_weights.get(ex.name, 0)
        return exercises


class GymStrengthExercisesForWomenFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Жим гантелями", "strength", "chest", "Dumbbells", 3.5),
            Exercise("Глютеальний міст", "strength", "legs", met=3.5),
        ]
        for ex in exercises:
            max_weights = {"Жим гантелями": 30, "Глютеальний міст": 60}
            ex.max_weight = max_weights.get(ex.name, 0)
        return exercises


class HomeStrengthExercisesFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        return [
            Exercise("Віджимання", "strength", "chest", met=3.0),
            Exercise("Присідання", "strength", "legs", met=4.0),
        ]


class GymCardioExercisesFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Біг на доріжці", "cardio", "dynamic", "Treadmill", 9.8),
            Exercise("Стрибки зі скакалкою", "cardio", "static", "Jump Rope", 10.0),
        ]
        for ex in exercises:
            settings = {
                "Біг на доріжці": {"speed": 8.0, "freq": 140, "dist": 10.0},
                "Стрибки зі скакалкою": {"freq": 150},
            }
            setting = settings.get(ex.name, {})
            ex.recommended_speed = setting.get("speed")
            ex.recommended_frequency = setting.get("freq")
            ex.max_distance = setting.get("dist", 0)
        return exercises


class ParkCardioExercisesFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Біг по стежці", "cardio", "dynamic", met=8.0),
            Exercise("Стрибки зірочкою", "cardio", "static", met=6.0),
        ]
        for ex in exercises:
            settings = {
                "Біг по стежці": {"speed": 8.0, "freq": 130, "dist": 10.0},
                "Стрибки зірочкою": {"freq": 120},
            }
            setting = settings.get(ex.name, {})
            ex.recommended_speed = setting.get("speed")
            ex.recommended_frequency = setting.get("freq")
            ex.max_distance = setting.get("dist", 0)
        return exercises


class HomeCardioExercisesFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Стрибки зірочкою", "cardio", "static", met=8.0),
            Exercise("Бурпі", "cardio", "static", met=8.0),
        ]
        for ex in exercises:
            settings = {
                "Стрибки зірочкою": {"freq": 120},
                "Бурпі": {"freq": 115},
            }
            ex.recommended_frequency = settings.get(ex.name, {}).get("freq")
        return exercises


class ExerciseFactoryProvider:
    @staticmethod
    def get_factory(user_profile, plan_type, training_location):
        if user_profile._gender == "Male" and plan_type == "Strength" and training_location == "Gym":
            return GymStrengthExercisesForMenFactory()
        elif user_profile._gender == "Female" and plan_type == "Strength" and training_location == "Gym":
            return GymStrengthExercisesForWomenFactory()
        elif plan_type == "Strength" and training_location == "Home":
            return HomeStrengthExercisesFactory()
        elif plan_type == "Cardio" and training_location == "Gym":
            return GymCardioExercisesFactory()
        elif plan_type == "Cardio" and training_location == "Park":
            return ParkCardioExercisesFactory()
        elif plan_type == "Cardio" and training_location == "Home":
            return HomeCardioExercisesFactory()
        raise ValueError("Непідтримуваний тип тренування або локація.")


class UserProfileManager:
    def __init__(self):
        self._user_profile_file_path = "user_profile.json"

    def calculate_bmi(self, profile):
        height_in_meters = profile._height / 100
        return round(profile._weight / (height_in_meters * height_in_meters), 2)

    def get_bmi_category(self, bmi):
        if bmi < 18.5:
            return "Недостатня вага"
        elif bmi < 24.9:
            return "Нормальна вага"
        elif bmi < 29.9:
            return "Надмірна вага"
        return "Ожиріння"

    def save_user_profile(self, profile):
        with open(self._user_profile_file_path, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2)

    def load_user_profile(self):
        if not os.path.exists(self._user_profile_file_path):
            return UserProfile()
        try:
            with open(self._user_profile_file_path, 'r') as f:
                data = json.load(f)
                return UserProfile.from_dict(data)
        except json.JSONDecodeError:
            return UserProfile()

    def is_user_profile_file_empty(self):
        if not os.path.exists(self._user_profile_file_path):
            return True
        return os.path.getsize(self._user_profile_file_path) == 0

    def fill_user_profile(self, profile, inputs):
        try:
            profile._gender = inputs['gender']
            profile._weight = float(inputs['weight'])
            profile._height = float(inputs['height'])
            profile._fitness_level = int(inputs['fitness_level'])
            profile._goal_muscle_groups = inputs['muscle_groups']
            profile._preferred_difficulty = inputs['difficulty']
            if profile._weight <= 0 or profile._height <= 0:
                raise ValueError("Вага та зріст повинні бути більше 0.")
            if profile._fitness_level < 1 or profile._fitness_level > 5:
                raise ValueError("Рівень підготовки повинен бути від 1 до 5.")
            if not profile._goal_muscle_groups:
                raise ValueError("Виберіть хоча б одну м’язову групу.")
            self.save_user_profile(profile)
            return True
        except ValueError as e:
            self._show_error(profile._tk_root, str(e))
            return False

    def display_user_profile(self, profile):
        bmi = self.calculate_bmi(profile)
        bmi_category = self.get_bmi_category(bmi)
        return {
            "Рівень підготовки": profile._fitness_level,
            "М’язові групи": ", ".join(profile._goal_muscle_groups),
            "Складність": profile._preferred_difficulty,
            "Вага": f"{profile._weight} кг",
            "Зріст": f"{profile._height} см",
            "ІМТ": f"{bmi} ({bmi_category})"
        }

    def update_exercise_feedback(self, profile, exercise_name, feedback):
        profile._exercise_feedback[exercise_name] = feedback
        self.save_user_profile(profile)

    def delete_user_profile(self):
        if os.path.exists(self._user_profile_file_path):
            os.remove(self._user_profile_file_path)

    def _show_error(self, root, message):
        modal = ctk.CTkToplevel(root)
        modal.title("Помилка")
        modal.geometry("400x200")
        ctk.CTkLabel(modal, text=message, font=("Roboto", 14), wraplength=350).pack(pady=20)
        ctk.CTkButton(modal, text="OK", font=("Roboto", 14), command=modal.destroy, fg_color="#10b981",
                      hover_color="#12d1a1").pack(pady=10)


class TrainingArchiveManager:
    def __init__(self):
        self._archive_file_path = "training_archive.json"

    def save_plan_to_archive(self, plan, plan_type):
        archive_entry = TrainingArchiveEntry(
            plan_type,
            plan.get_generated_plan(),
            plan.total_calories_burned,
            datetime.now()
        )
        archive = self.load_archive()
        archive.append(archive_entry)
        with open(self._archive_file_path, 'w') as f:
            json.dump([entry.to_dict() for entry in archive], f, indent=2)

    def load_archive(self):
        if not os.path.exists(self._archive_file_path):
            return []
        try:
            with open(self._archive_file_path, 'r') as f:
                data = json.load(f)
                return [TrainingArchiveEntry.from_dict(entry) for entry in data]
        except json.JSONDecodeError:
            return []

    def clear_archive(self):
        if os.path.exists(self._archive_file_path):
            with open(self._archive_file_path, 'w') as f:
                f.write("")
            return "Архів успішно очищено."
        return "Файл архіву не існує."

    def get_archived_plans_summary(self):
        archive = self.load_archive()
        if not archive:
            return []
        return [
            {
                "id": i + 1,
                "type": entry.plan_type,
                "calories": entry.total_calories_burned,
                "date": entry.date.strftime("%Y-%m-%d %H:%M:%S")
            }
            for i, entry in enumerate(archive)
        ]

    def get_plan_details(self, index):
        archive = self.load_archive()
        if index < 0 or index >= len(archive):
            return {"error": "Невірний індекс. Оберіть коректний план."}
        entry = archive[index]
        details = {
            "type": entry.plan_type,
            "calories": entry.total_calories_burned,
            "exercises": []
        }
        for exercise in entry.generated_plan:
            equipment_display = f", Обладнання: {exercise.equipment}" if exercise.equipment != "Bodyweight" else ""
            if exercise.type == "cardio":
                details["exercises"].append(
                    f"{exercise.name} (Відстань: {exercise.distance} км, Тривалість: {exercise.duration} хв, "
                    f"Інтенсивність: {exercise.intensity}{equipment_display}, "
                    f"Швидкість: {exercise.recommended_speed} км/год, Частота: {exercise.recommended_frequency} уд/хв)"
                )
            else:
                if exercise.equipment != "Bodyweight" and exercise.working_weight != 0:
                    details["exercises"].append(
                        f"{exercise.name} (Підходи: {exercise.sets}, Повторення: {exercise.repeats}, "
                        f"Відпочинок: {exercise.rest} хв, Вага: {exercise.working_weight} кг{equipment_display})"
                    )
                else:
                    details["exercises"].append(
                        f"{exercise.name} (Підходи: {exercise.sets}, Повторення: {exercise.repeats}, "
                        f"Відпочинок: {exercise.rest} хв{equipment_display})"
                    )
        return details


class TrainingPlanManager:
    def create_cardio_plan(self, difficulty, exercises, profile):
        cardio_plan = CardioPlan(profile)
        cardio_plan.generate_plan(difficulty, exercises)
        return cardio_plan, self._format_plan(cardio_plan, "Cardio")

    def create_strength_plan(self, is_full_body, properties, difficulty, exercises, profile):
        strength_plan = FullBodyPlan(properties, profile) if is_full_body else SplitPlan(properties, profile)
        strength_plan.generate_plan(difficulty, exercises)
        return strength_plan, self._format_plan(strength_plan, "Strength")

    def _format_plan(self, plan, plan_type):
        plan_data = {
            "type": plan_type,
            "calories": plan.total_calories_burned,
            "exercises": []
        }
        properties_displayed = set()
        for exercise in plan.get_generated_plan():
            equipment_display = f", Обладнання: {exercise.equipment}" if exercise.equipment != "Bodyweight" else ""
            if plan_type == "Cardio":
                if exercise.properties == "dynamic":
                    plan_data["exercises"].append({
                        "name": exercise.name,
                        "details": f"Відстань: {exercise.distance} км, Інтенсивність: {exercise.intensity}{equipment_display}, "
                                   f"Швидкість: {exercise.recommended_speed} км/год, Частота: {exercise.recommended_frequency} уд/хв"
                    })
                else:
                    plan_data["exercises"].append({
                        "name": exercise.name,
                        "details": f"Тривалість: {exercise.duration} хв, Інтенсивність: {exercise.intensity}{equipment_display}, "
                                   f"Частота: {exercise.recommended_frequency} уд/хв"
                    })
            else:
                if exercise.properties not in properties_displayed:
                    plan_data["exercises"].append({"name": f"Ціль: {exercise.properties}", "details": ""})
                    properties_displayed.add(exercise.properties)
                if exercise.equipment != "Bodyweight" and exercise.working_weight != 0:
                    plan_data["exercises"].append({
                        "name": exercise.name,
                        "details": f"Підходи: {exercise.sets}, Повторення: {exercise.repeats}, "
                                   f"Відпочинок: {exercise.rest} хв, Вага: {exercise.working_weight} кг{equipment_display}"
                    })
                else:
                    plan_data["exercises"].append({
                        "name": exercise.name,
                        "details": f"Підходи: {exercise.sets}, Повторення: {exercise.repeats}, "
                                   f"Відпочинок: {exercise.rest} хв{equipment_display}"
                    })
        return plan_data


class Trainer:
    def __init__(self, plan, user_profile, update_callback):
        self.plan = plan
        self.user_profile = user_profile
        self.update_callback = update_callback
        self.running = False
        self.current_exercise_name = None
        self.current_set = 1

    def start_training(self):
        self.running = True
        threading.Thread(target=self._run_training, daemon=True).start()

    def _run_training(self):
        # Стартовий таймер
        self.update_callback("До початку тренування", show_timer=True, timer_duration=5)
        self._wait_until_confirmed()
        if not self.running:
            return

        exercises = self.plan.get_generated_plan()
        if not exercises:
            self.update_callback("В плані немає вправ.")
            return

        for idx, exercise in enumerate(exercises):
            self.current_exercise_name = exercise.name
            for set_num in range(1, exercise.sets + 1):
                self.current_set = set_num
                if not self.running:
                    return

                self.update_callback(
                    message=f"{exercise.name}",
                    set_info={"current": set_num, "total": exercise.sets},
                    prompt=True,
                    exercise_name=exercise.name
                )
                self._wait_until_confirmed()
                if not self.running:
                    return

                if set_num < exercise.sets:
                    rest_seconds = int(exercise.rest * 60)
                    self.update_callback(
                        message="Відпочинок",
                        show_timer=True,
                        timer_duration=rest_seconds
                    )
                    self._wait_until_confirmed()
                    if not self.running:
                        return

            # Перерва між вправами (якщо не остання вправа)
            if idx < len(exercises) - 1:
                rest_seconds = 30
                self.update_callback(
                    message="Перерва між вправами",
                    show_timer=True,
                    timer_duration=rest_seconds
                )
                self._wait_until_confirmed()
                if not self.running:
                    return

        self.update_callback("Тренування завершено! Залиште відгук", feedback=True)

    def _wait_until_confirmed(self):
        self.user_profile._tk_root.confirm_response.set(False)
        while not self.user_profile._tk_root.confirm_response.get() and self.running:
            time.sleep(0.1)

    def stop_training(self):
        self.running = False


class TrainingApplication(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Фітнес Додаток")
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
        self.exercise_status = {}  # Словник для відстеження статусу вправ
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
        nav_buttons = [("🏠 Головна", self.show_home_page, self.home_frame), (" 💪 Тренування", self.show_training_page, self.training_frame),
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
        # Заголовок угорі
        welcome_label = ctk.CTkLabel(
            self.home_frame,
            text="Ласкаво просимо до Фітнес Додатку!",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors["dark"]["text_color"]
        )
        welcome_label.pack(pady=(10, 20))
        self.themed_widgets["labels"].append((welcome_label, "text_color", "text_color"))

        # Зображення під заголовком
        image_path = r"C:\Users\Asus\PycharmProjects\PythonProject\Images\Image1.png"
        try:
            img = Image.open(image_path).convert("RGBA")
            img = img.resize((600, 400), Image.LANCZOS)  # Збільшене зображення
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(500, 350))
            image_frame = ctk.CTkFrame(self.home_frame, fg_color="transparent")
            image_frame.pack(pady=10)
            image_label = ctk.CTkLabel(image_frame, image=ctk_img, text="", fg_color="transparent")
            image_label.pack()
        except Exception as e:
            error_label = ctk.CTkLabel(
                self.home_frame,
                text="Не вдалося завантажити зображення",
                font=("Roboto", 14),
                text_color=self.theme_colors["dark"]["text_color"]
            )
            error_label.pack(pady=10)
            self.themed_widgets["labels"].append((error_label, "text_color", "text_color"))

        # Секція порад
        tips_frame = ctk.CTkFrame(self.home_frame, fg_color=self.theme_colors["dark"]["card_bg"])
        tips_frame.pack(pady=20, fill="x")
        self.themed_widgets["frames"].append((tips_frame, "fg_color", "card_bg"))
        tips_label = ctk.CTkLabel(
            tips_frame,
            text="Цікавий факт: Регулярні тренування можуть збільшити тривалість життя на 3-7 років!\nПорада: Пийте воду перед, під час та після тренувань для оптимального відновлення.",
            font=("Roboto", 14),
            wraplength=600,
            justify="center",
            text_color=self.theme_colors["dark"]["text_color"]
        )
        tips_label.pack()
        self.themed_widgets["labels"].append((tips_label, "text_color", "text_color"))

        # Контейнер для карток-кнопок
        cards_frame = ctk.CTkFrame(self.home_frame, fg_color=self.theme_colors["dark"]["card_bg"])
        cards_frame.pack(pady=20, fill="x")
        self.themed_widgets["frames"].append((cards_frame, "fg_color", "card_bg"))

        # Дані для карток (лише емодзі)
        card_data = [
            ("📋", self.show_training_page),
            ("📚", self.show_archive_page),
            ("📊", self.show_statistics_page)
        ]

        for i, (emoji, command) in enumerate(card_data):
            card_button = ctk.CTkButton(
                cards_frame,
                text=emoji,
                font=("Roboto", 40),  # Великий розмір емодзі
                fg_color=self.theme_colors["dark"]["inner_card_bg"],
                hover_color=self.theme_colors["dark"]["button_hover"],
                command=command,
                corner_radius=12,
                width=100,  # Менший розмір картки
                height=100
            )
            card_button.grid(row=0, column=i, padx=10, pady=10)
            self.themed_widgets["buttons"].extend([
                (card_button, "fg_color", "inner_card_bg"),
                (card_button, "hover_color", "button_hover")
            ])

    def animate_fade_in(self, widget, duration=500, steps=20):
        for i in range(steps):
            alpha = i / steps
            text_color = f"{self.theme_colors[self.theme_var.get()]['text_color']}{int(alpha*255):02x}"
            widget.configure(text_color=text_color)
            self.update()
            time.sleep(duration / steps / 1000)

    def animate_button_hover(self, button, enter=True):
        # Перевіряємо, чи кнопка належить до feedback_buttons або training_confirmation_buttons
        is_feedback_button = any(button == info["button"] for info in self.feedback_buttons.values())
        is_confirmation_button = any(button == info["button"] for info in self.training_confirmation_buttons.values())

        if is_feedback_button or is_confirmation_button:
            # Знаходимо ключ кнопки в словнику
            button_key = None
            buttons_dict = self.feedback_buttons if is_feedback_button else self.training_confirmation_buttons
            for key, info in buttons_dict.items():
                if button == info["button"]:
                    button_key = key
                    break

            if button_key:
                selected = buttons_dict[button_key]["selected"]
                if enter and not selected:
                    # Підсвітка при наведенні, якщо кнопка не вибрана
                    button.configure(
                        border_width=2,
                        border_color=self.theme_colors[self.theme_var.get()]["shadow_color"],
                        fg_color=self.theme_colors[self.theme_var.get()]["button_hover"]
                    )
                elif not selected:
                    # Скидаємо підсвітку при виході, якщо кнопка не вибрана
                    button.configure(
                        border_width=0,
                        border_color="",
                        fg_color=self.theme_colors[self.theme_var.get()]["button_fg"]
                    )
                # Для вибраних кнопок стан не змінюється при наведенні/виході
        else:
            # Для інших кнопок (start_training_button, trainer_button, feedback_submit_button)
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
            text="🏋️Розпочати",  # Без пробілу між текстом і емодзі
            font=("Roboto", 16),
            command=self.start_trainer_mode,
            fg_color=self.theme_colors["dark"]["button_active"],
            hover_color=self.theme_colors["dark"]["button_hover"],
            corner_radius=10,
            width=150,  # Збільшено ширину для кращого розміщення тексту  # Додано внутрішні відступи для центрування
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
                break  # Віджет знищено — припиняємо таймер

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

        # Словник із повідомленнями для кожного типу відгуку
        feedback_messages = {
            "Easy": "Чудово, ви великий молодець! Тренування було легким, можливо, наступного разу спробуйте складніше?",
            "Normal": "Відмінна робота! Тренування пройшло як треба, продовжуйте в тому ж дусі!",
            "Hard": "Шкода, що було важко. Не хвилюйтеся, ми підлаштуємо наступний план, щоб було комфортніше!"
        }

        # Вибираємо повідомлення або стандартне, якщо відгук нестандартний
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

        # Головний заголовок
        label = ctk.CTkLabel(
            self.archive_frame,
            text="Архів Тренувань",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        label.pack(pady=10)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))

        # Контейнер для canvas і scrollbar
        canvas_container = ctk.CTkFrame(
            self.archive_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        canvas_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.themed_widgets["frames"].append((canvas_container, "fg_color", "main_bg"))

        # Створення Canvas для прокрутки
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

        # Внутрішній фрейм для карток
        self.archive_frame_inner = ctk.CTkFrame(
            self.archive_canvas,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        self.themed_widgets["frames"].append((self.archive_frame_inner, "fg_color", "main_bg"))

        # Створення вікна в Canvas
        self.archive_window_id = self.archive_canvas.create_window(
            (0, 0),
            window=self.archive_frame_inner,
            anchor="nw"
        )

        # Налаштування прокрутки при зміні розміру фрейму
        def update_scrollregion(event):
            self.archive_canvas.configure(scrollregion=self.archive_canvas.bbox("all"))
            # Оновлення ширини вікна, щоб відповідати ширині canvas
            canvas_width = self.archive_canvas.winfo_width()
            self.archive_canvas.itemconfigure(self.archive_window_id, width=canvas_width)

        self.archive_frame_inner.bind("<Configure>", update_scrollregion)

        # Кнопка очищення архіву
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
        # Очищення попередніх карток
        for widget in self.archive_frame_inner.winfo_children():
            widget.destroy()

        # Завантаження архіву
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
                # Форматування дати та часу
                date_time_parts = entry['date'].split()
                if len(date_time_parts) > 1:
                    date_part = date_time_parts[0].split('-')
                    time_part = date_time_parts[1].split(':')
                    formatted_date = f"{date_part[2]}.{date_part[1]} | {time_part[0]}:{time_part[1]}"
                else:
                    date_part = entry['date'].split('-')
                    formatted_date = f"{date_part[2]}.{date_part[1]}"

                # Основна картка тренування
                card = ctk.CTkFrame(
                    self.archive_frame_inner,
                    fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                    corner_radius=12
                )
                card.pack(fill="x", padx=20, pady=6)
                card.grid_columnconfigure(0, weight=1)

                # Внутрішній фрейм для підкарток і кнопки
                inner_frame = ctk.CTkFrame(
                    card,
                    fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                    corner_radius=0
                )
                inner_frame.grid(row=0, column=0, sticky="w", padx=12, pady=12)
                inner_frame.grid_columnconfigure(0, weight=1)

                # Підкартка для дати
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

                # Підкартка для типу
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

                # Підкартка для калорій
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

                # Кнопка "Деталі"
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

                # Додавання до темованих віджетів
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

        # Оновлення області прокрутки після створення всіх карток
        self.archive_frame_inner.update_idletasks()
        canvas_width = self.archive_canvas.winfo_width()
        self.archive_canvas.configure(scrollregion=self.archive_canvas.bbox("all"))
        self.archive_canvas.itemconfigure(self.archive_window_id, width=canvas_width)

    def view_archive_details(self, index):
        # Отримання деталей плану
        details = self.archive_manager.get_plan_details(index)
        if "error" in details:
            self._show_error(details["error"])
            return

        # Створення модального вікна
        modal = ctk.CTkToplevel(self)
        modal.transient(self)
        modal.title("Деталі Тренування")
        modal.geometry("600x500")
        modal.configure(fg_color=self.theme_colors[self.theme_var.get()]["main_bg"])
        self.themed_widgets["frames"].append((modal, "fg_color", "main_bg"))

        # Основна картка
        card = ctk.CTkFrame(
            modal,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"],
            corner_radius=12
        )
        card.pack(fill="both", expand=True, padx=10, pady=10)
        self.themed_widgets["frames"].append((card, "fg_color", "card_bg"))

        # Заголовок
        label = ctk.CTkLabel(
            card,
            text=f"План: {details['type']}",
            font=("Roboto", 20, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        label.pack(pady=10)
        self.themed_widgets["labels"].append((label, "text_color", "text_color"))

        # Контейнер для прокрутки вправ
        canvas_container = ctk.CTkFrame(
            card,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        canvas_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.themed_widgets["frames"].append((canvas_container, "fg_color", "card_bg"))

        # Canvas для прокрутки
        canvas = ctk.CTkCanvas(
            canvas_container,
            bg=self.theme_colors[self.theme_var.get()]["canvas_bg"],
            highlightthickness=0
        )
        canvas.pack(side="left", fill="both", expand=True)
        self.themed_widgets["canvases"].append((canvas, "bg", "canvas_bg"))

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(
            canvas_container,
            orientation="vertical",
            command=canvas.yview
        )
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Внутрішній фрейм для вправ
        exercises_frame = ctk.CTkFrame(
            canvas,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        self.themed_widgets["frames"].append((exercises_frame, "fg_color", "card_bg"))

        # Створення вікна в Canvas
        canvas_window_id = canvas.create_window(
            (0, 0),
            window=exercises_frame,
            anchor="nw"
        )

        # Перевірка наявності вправ
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
            # Додавання вправ
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

        # Картка для калорій
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

        # Кнопка закриття
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

        # Налаштування прокрутки
        def update_scrollregion(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas_width = canvas.winfo_width()
            canvas.itemconfigure(canvas_window_id, width=canvas_width - 4)  # Невеликий відступ

        exercises_frame.bind("<Configure>", update_scrollregion)

        # Примусове оновлення canvas після створення всіх елементів
        canvas.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        # Безпечне захоплення фокусу
        modal.grab_set()
        if modal.winfo_exists():
            modal.focus_set()

    def show_plan_details(self, index):
        plan_details = self.archive_manager.get_plan_details(index)
        modal = ctk.CTkToplevel(self)
        modal.transient(self)  # Встановлюємо модальне вікно поверх головного
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
        """Ініціалізація сторінки статистики з верхньою карткою для гістограм та двома нижніми картками."""
        # Очищення попередніх віджетів
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Головний заголовок
        title_label = ctk.CTkLabel(
            self.stats_frame,
            text="Статистика по тренуванням",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))

        # Підзаголовок
        subtitle_label = ctk.CTkLabel(
            self.stats_frame,
            text="Слідкуйте за прогресом своїх сесій!",
            font=("Roboto", 14),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        subtitle_label.pack(pady=(0, 20))
        self.themed_widgets["labels"].append((subtitle_label, "text_color", "text_color"))

        # Верхня картка для гістограм
        graph_frame = ctk.CTkFrame(
            self.stats_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"],
            corner_radius=12
        )
        graph_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.themed_widgets["frames"].append((graph_frame, "fg_color", "card_bg"))

        # Заголовок графіка
        graph_title = ctk.CTkLabel(
            graph_frame,
            text="Кількість калорій (ккал)",
            font=("Roboto", 16, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_accent"]
        )
        graph_title.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((graph_title, "text_color", "text_accent"))

        # Область для гістограми
        self.histogram_frame = ctk.CTkFrame(
            graph_frame,
            fg_color="transparent"
        )
        self.histogram_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Нижня секція з двома картками
        bottom_frame = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=20, pady=(0, 10))

        # Ліва нижня картка (загальна кількість калорій)
        left_card = ctk.CTkFrame(
            bottom_frame,
            height=180,
            corner_radius=12,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        left_card.pack(side="left", expand=True, fill="x", padx=(0, 5))
        left_card.pack_propagate(False)
        self.themed_widgets["frames"].append((left_card, "fg_color", "card_bg"))

        # Права нижня картка (підказка)
        right_card = ctk.CTkFrame(
            bottom_frame,
            height=180,
            corner_radius=12,
            fg_color=self.theme_colors[self.theme_var.get()]["card_bg"]
        )
        right_card.pack(side="right", expand=True, fill="x", padx=(5, 0))
        right_card.pack_propagate(False)
        self.themed_widgets["frames"].append((right_card, "fg_color", "card_bg"))

        # Заголовок для лівої картки
        calories_title = ctk.CTkLabel(
            left_card,
            text="🔥 Всього спалено калорій",
            font=("Roboto", 16, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_accent"]
        )
        calories_title.pack(pady=(15, 5))
        self.themed_widgets["labels"].append((calories_title, "text_color", "text_accent"))

        # Значення калорій
        self.total_calories_label = ctk.CTkLabel(
            left_card,
            text="0 ккал",
            font=("Roboto", 20, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        self.total_calories_label.pack(expand=True, pady=(0, 5))
        self.themed_widgets["labels"].append((self.total_calories_label, "text_color", "text_color"))

        # Середня кількість калорій
        self.avg_calories_label = ctk.CTkLabel(
            left_card,
            text="📊 Середня кількість калорій: 0 ккал",
            font=("Roboto", 14),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        self.avg_calories_label.pack(pady=(5, 0))
        self.themed_widgets["labels"].append((self.avg_calories_label, "text_color", "text_color"))

        # Загальна кількість тренувань
        self.workouts_label = ctk.CTkLabel(
            left_card,
            text="🏃 Загальна кількість тренувань за останній тиждень: 0",
            font=("Roboto", 14),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        self.workouts_label.pack(pady=(5, 15))
        self.themed_widgets["labels"].append((self.workouts_label, "text_color", "text_color"))

        # Заголовок для правої картки
        tip_title = ctk.CTkLabel(
            right_card,
            text="💡 Підказки",
            font=("Roboto", 16, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_accent"]
        )
        tip_title.pack(pady=(15, 5))
        self.themed_widgets["labels"].append((tip_title, "text_color", "text_accent"))

        # Підказка
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

        # Оновлення даних
        self.update_statistics_display()

    def update_statistics_display(self):
        """Оновлення відображення статистики з гістограмами та даними."""
        # Очищення попередніх віджетів у фреймі гістограм
        for widget in self.histogram_frame.winfo_children():
            widget.destroy()

        # Завантаження даних з архіву
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

        # Обмеження до 12 останніх сесій
        archive_data = archive_data[-12:]
        max_calories = max(entry.total_calories_burned for entry in archive_data) or 1
        dates = [entry.date.strftime("%d.%m") for entry in archive_data]

        # Контейнер для гістограм
        bars_container = ctk.CTkFrame(self.histogram_frame, fg_color="transparent")
        bars_container.pack(fill="both", expand=True, padx=20, pady=20)

        # Визначення кольорів для стовпців
        colors = [
            "#10b981", "#34d399", "#6ee7b7", "#a7f3d0",  # Відтінки зеленого
            "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe",  # Відтінки синього
            "#6b46c1", "#8e44ad", "#9b59b6", "#d1b3e0"  # Відтінки фіолетового
        ]

        # Створення гістограм
        for i, entry in enumerate(archive_data):
            percent = entry.total_calories_burned / max_calories
            bar_height = int(percent * 220)

            # Колонка для одного стовпця
            column = ctk.CTkFrame(bars_container, fg_color="transparent")
            column.pack(side="left", fill="y", expand=True)

            # Лейбл з датою
            date_label = ctk.CTkLabel(
                column,
                text=dates[i],
                font=("Roboto", 12),
                text_color="#FFFFFF"
            )
            date_label.pack(side="bottom", pady=(0, 5))
            self.themed_widgets["labels"].append((date_label, "text_color", "text_color"))

            # Стовпець гістограми
            bar = ctk.CTkFrame(
                column,
                height=bar_height,
                width=36,
                corner_radius=6,
                fg_color=colors[i % len(colors)]
            )
            bar.pack(side="bottom", fill="x", padx=5)
            self.themed_widgets["frames"].append((bar, "fg_color", "text_accent"))

            # Лейбл з калоріями над стовпцем
            cal_label = ctk.CTkLabel(
                column,
                text=str(entry.total_calories_burned),
                font=("Roboto", 12, "bold"),
                text_color=self.theme_colors[self.theme_var.get()]["text_color"]
            )
            cal_label.pack(side="bottom", pady=(5, 0))
            self.themed_widgets["labels"].append((cal_label, "text_color", "text_color"))

        # Оновлення загальної кількості калорій
        total_calories = sum(entry.total_calories_burned for entry in archive_data)
        self.total_calories_label.configure(text=f"{total_calories} ккал")

        # Оновлення середньої кількості калорій
        avg_calories = total_calories // len(archive_data) if archive_data else 0
        self.avg_calories_label.configure(text=f"📊 Середня кількість калорій: {avg_calories} ккал")

        # Оновлення загальної кількості тренувань за останній тиждень
        from datetime import datetime, timedelta
        one_week_ago = datetime.now() - timedelta(days=7)
        weekly_workouts = len([entry for entry in archive_data
                               if datetime.combine(entry.date, datetime.min.time()) >= one_week_ago])
        self.workouts_label.configure(text=f"🏃 Загальна кількість тренувань за останній тиждень: {weekly_workouts}")

        # Логіка для вибору підказки
        tip = ""
        if len(archive_data) > 1:
            last = archive_data[-1].total_calories_burned
            prev = archive_data[-2].total_calories_burned
            # Перевірка регулярності: чи є тренування хоча б кожні 2 дні
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

            # Додаткові підказки залежно від регулярності
            if not is_regular:
                tip = "⏰ Регулярність — запорука успіху! Намагайтеся тренуватися хоча б раз на 2 дні, щоб підтримувати прогрес. 🏋️"
            # Підказки залежно від загальної кількості калорій
            elif total_calories > 2000:
                tip = "🔥 Ви спалили понад 2000 калорій, вражаючий результат! Продовжуйте в тому ж дусі та не забувайте про відпочинок! 😴"
            # Підказки залежно від типу тренувань
            elif mostly_cardio:
                tip = "🏃 Ви віддаєте перевагу кардіо — чудово для витривалості! Спробуйте додати силові тренування, щоб зміцнити м’язи. 💪"
            elif mostly_strength:
                tip = "💪 Ви зосереджені на силових тренуваннях, круто! Додайте кардіо, щоб покращити витривалість і здоров’я серця. 🏃"
        else:
            tip = "🌟 Початок відмінний! Продовжуйте тренуватись регулярно, і результати не забаряться. 💪"

        self.tip_label.configure(text=tip)

    def create_bmi_gauge(self, parent_frame, bmi):
        # Контейнер для гістограми
        gauge_frame = ctk.CTkFrame(
            parent_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        gauge_frame.pack(fill="x", padx=20, pady=(9, 0))
        self.themed_widgets["frames"].append((gauge_frame, "fg_color", "main_bg"))

        # Canvas для дуги
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

        # Центр і радіус дуги
        center_x, center_y = canvas_width / 2, canvas_height - 100
        radius = 140

        # Визначення секторів (діапазон 15-30)
        total_angle = 300

        # Кольори для секторів
        colors = {
            "underweight": "#10b981",  # Зелений
            "normal": "#3b82f6",  # Синій
            "overweight": "#6b46c1"  # Фіолетовий
        }

        # Визначення кутів для діапазону ІМТ 15-30
        underweight_angle = total_angle * ((18.5 - 15) / (30 - 15))
        normal_angle = total_angle * ((25 - 18.5) / (30 - 15))
        overweight_angle = total_angle * ((30 - 25) / (30 - 15))

        # Початковий кут (240 градусів)
        start_angle = 240

        # Малювання секторів проти годинникової стрілки
        # 1. Недостатня вага (зелений, зліва)
        gauge_canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle, extent=-underweight_angle,
            style="arc", outline=colors["underweight"], width=20
        )

        # 2. Нормальна вага (синій)
        gauge_canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle - underweight_angle, extent=-normal_angle,
            style="arc", outline=colors["normal"], width=20
        )

        # 3. Надмірна вага (фіолетовий)
        gauge_canvas.create_arc(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            start=start_angle - underweight_angle - normal_angle, extent=-overweight_angle,
            style="arc", outline=colors["overweight"], width=20
        )

        # Відображення значення ІМТ (білий колір)
        bmi_label = gauge_canvas.create_text(
            center_x, center_y - 30,
            text=f"ІМТ: {bmi:.1f}",
            font=("Roboto", 28, "bold"),
            fill="#ffffff"
        )

        # Визначення кольору категорії залежно від ІМТ
        category = self.profile_manager.get_bmi_category(bmi)
        category_color = (
            colors["underweight"] if bmi < 18.5 else
            colors["normal"] if bmi < 25 else
            colors["overweight"]
        )

        # Відображення категорії ІМТ (колір сектора)
        category_label = gauge_canvas.create_text(
            center_x, center_y + 10,
            text=category,
            font=("Roboto", 16),
            fill=category_color
        )

        # Трикутник-покажчик зовні
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

        # Легенда
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
            # Не додаємо text_label до themed_widgets["labels"], щоб зберегти білий колір

        return gauge_frame

    def setup_profile_page(self):
        # Очищення попередніх віджетів
        for widget in self.profile_frame.winfo_children():
            widget.destroy()
        self.profile_inputs = {}

        # Заголовок "Загальна інформація"
        title_label = ctk.CTkLabel(
            self.profile_frame,
            text="Загальна інформація",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))

        # Створення гістограми ІМТ
        bmi = self.profile_manager.calculate_bmi(self.user_profile)
        self.create_bmi_gauge(self.profile_frame, bmi)

        # Контейнер для карток профілю
        profile_cards_frame = ctk.CTkFrame(
            self.profile_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        profile_cards_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.themed_widgets["frames"].append((profile_cards_frame, "fg_color", "main_bg"))

        # Дані профілю з емодзі
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

            # Фрейм для емодзі та ключа
            key_frame = ctk.CTkFrame(
                card,
                fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                corner_radius=0
            )
            key_frame.grid(row=0, column=0, padx=(10, 5), pady=8, sticky="w")
            self.themed_widgets["frames"].append((key_frame, "fg_color", "inner_card_bg"))

            # Емодзі
            emoji_label = ctk.CTkLabel(
                key_frame,
                text=emoji,
                font=("Roboto", 18),
                text_color="#ffffff"
            )
            emoji_label.pack(side="left", padx=5)
            self.themed_widgets["labels"].append((emoji_label, "text_color", "text_color"))

            # Ключ
            key_label = ctk.CTkLabel(
                key_frame,
                text=key,
                font=("Roboto", 14, "bold"),
                text_color="#ffffff",
                anchor="w"
            )
            key_label.pack(side="left", padx=(5, 0), pady=2)
            self.themed_widgets["labels"].append((key_label, "text_color", "text_color"))

            # Значення
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

        # Кнопка "Редагувати"
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
        # Очищення попередніх віджетів
        for widget in self.profile_frame.winfo_children():
            widget.destroy()
        self.profile_inputs = {}

        # Заголовок "Загальна інформація"
        title_label = ctk.CTkLabel(
            self.profile_frame,
            text="Загальна інформація",
            font=("Roboto", 24, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=(10, 5))
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))

        # Оновлення гістограми ІМТ
        bmi = self.profile_manager.calculate_bmi(self.user_profile)
        self.create_bmi_gauge(self.profile_frame, bmi)

        # Контейнер для карток профілю
        profile_cards_frame = ctk.CTkFrame(
            self.profile_frame,
            fg_color=self.theme_colors[self.theme_var.get()]["main_bg"]
        )
        profile_cards_frame.pack(fill="both", expand=True, padx=20, pady=5)
        self.themed_widgets["frames"].append((profile_cards_frame, "fg_color", "main_bg"))

        # Оновлення даних профілю
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

            # Фрейм для емодзі та ключа
            key_frame = ctk.CTkFrame(
                card,
                fg_color=self.theme_colors[self.theme_var.get()]["inner_card_bg"],
                corner_radius=0
            )
            key_frame.grid(row=0, column=0, padx=(10, 5), pady=6, sticky="w")
            self.themed_widgets["frames"].append((key_frame, "fg_color", "inner_card_bg"))

            # Емодзі
            emoji_label = ctk.CTkLabel(
                key_frame,
                text=emoji,
                font=("Roboto", 18),
                text_color="#ffffff"
            )
            emoji_label.pack(side="left", padx=5)
            self.themed_widgets["labels"].append((emoji_label, "text_color", "text_color"))

            # Ключ
            key_label = ctk.CTkLabel(
                key_frame,
                text=key,
                font=("Roboto", 14, "bold"),
                text_color="#ffffff",
                anchor="w"
            )
            key_label.pack(side="left", padx=(5, 0), pady=2)
            self.themed_widgets["labels"].append((key_label, "text_color", "text_color"))

            # Значення
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

        # Кнопка "Редагувати"
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

        # Заголовок
        title_label = ctk.CTkLabel(
            modal, text="Редагувати профіль", font=("Roboto", 20, "bold"),
            text_color=self.theme_colors[self.theme_var.get()]["text_color"]
        )
        title_label.pack(pady=10)
        self.themed_widgets["labels"].append((title_label, "text_color", "text_color"))

        # Стать
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

        # Вага
        weight_frame = ctk.CTkFrame(modal, fg_color="transparent")
        weight_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(weight_frame, text="⚖️ Вага (кг)", font=("Roboto", 14), text_color="#ffffff").pack(side="left",
                                                                                                        padx=5)
        inputs["weight"] = ctk.CTkEntry(weight_frame, font=("Roboto", 14))
        inputs["weight"].insert(0, str(self.user_profile._weight))
        inputs["weight"].pack(side="right", padx=5, fill="x", expand=True)

        # Зріст
        height_frame = ctk.CTkFrame(modal, fg_color="transparent")
        height_frame.pack(fill="x", padx=20, pady=5)
        ctk.CTkLabel(height_frame, text="📏 Зріст (см)", font=("Roboto", 14), text_color="#ffffff").pack(side="left",
                                                                                                        padx=5)
        inputs["height"] = ctk.CTkEntry(height_frame, font=("Roboto", 14))
        inputs["height"].insert(0, str(self.user_profile._height))
        inputs["height"].pack(side="right", padx=5, fill="x", expand=True)

        # Рівень підготовки
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

        # М’язові групи
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
            # Прив’язуємо команду після створення кнопки
            button.configure(
                command=lambda g=group, v=var, b=button: self.toggle_muscle_selection(g, v, inputs["muscle_groups"], b))
            button.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="ew")
            inputs["muscle_groups"].append((group, var, button))
            self.themed_widgets["buttons"].append(
                (button, "fg_color", "button_active" if var.get() else "button_fg", "hover_color", "button_hover")
            )

        muscles_grid.grid_columnconfigure((0, 1, 2), weight=1)

        # Складність
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

        # Кнопки Зберегти/Скасувати
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

        # Захоплення фокусу
        modal.grab_set()
        modal.focus_set()

    def toggle_muscle_selection(self, group, var, muscle_inputs, button):
        var.set(not var.get())  # Перемикання стану вибору
        # Оновлення кольору кнопки
        button.configure(
            fg_color=self.theme_colors[self.theme_var.get()]["button_active"] if var.get() else
            self.theme_colors[self.theme_var.get()]["button_fg"]
        )
        # Оновлення themed_widgets для fg_color
        for i, (w, attr, color_key, *extra) in enumerate(self.themed_widgets["buttons"]):
            if w == button and attr == "fg_color":
                self.themed_widgets["buttons"][i] = (
                    w, "fg_color", "button_active" if var.get() else "button_fg", *extra
                )
                break

    def save_profile(self, inputs, modal):
        try:
            profile_inputs = {
                "gender": inputs["gender"].get(),
                "weight": inputs["weight"].get() or str(self.user_profile._weight),
                "height": inputs["height"].get() or str(self.user_profile._height),
                "fitness_level": inputs["fitness_level"].get(),
                "muscle_groups": [g for g, v, _ in inputs["muscle_groups"] if v.get()],
                "difficulty": inputs["difficulty"].get()
            }
            if self.profile_manager.fill_user_profile(self.user_profile, profile_inputs):
                self.update_profile_display()  # Оновлюємо відображення профілю
                modal.destroy()  # Закриваємо модальне вікно
            else:
                self._show_error("Помилка при оновленні профілю.")
        except ValueError as e:
            self._show_error(str(e))

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

        # Безпечне захоплення фокусу
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

        # Безпечне захоплення фокусу
        modal.grab_set()
        if modal.winfo_exists():
            modal.focus_set()

    def quit_application(self):
        self.destroy()



if __name__ == "__main__":
    app = TrainingApplication()
    app.mainloop()