import json
import os
from user_profile import UserProfile
from user_profile import ExerciseFeedback

class UserProfileManager:
    def __init__(self):
        self._user_profile_file_path = "user_profile.json"

    def calculate_bmi(self, profile):
        height_in_meters = profile.height / 100
        return round(profile.weight / (height_in_meters * height_in_meters), 2)

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
            profile.gender = inputs.get("gender", "Male")
            profile.weight = float(inputs.get("weight", 70.0))
            profile.height = float(inputs.get("height", 170.0))
            profile.fitness_level = int(inputs.get("fitness_level", 1))
            profile.goal_muscle_groups = inputs.get("muscle_groups", [])
            profile.preferred_difficulty = inputs.get("difficulty", "Medium")

            if profile.weight <= 0 or profile.height <= 0:
                raise ValueError("Вага та зріст повинні бути більше 0.")
            if profile.fitness_level < 1 or profile.fitness_level > 5:
                raise ValueError("Рівень підготовки повинен бути від 1 до 5.")
            if not profile.goal_muscle_groups:
                raise ValueError("Виберіть хоча б одну м’язову групу.")

            self.save_user_profile(profile)
            return True
        except ValueError as e:
            return str(e)

    def display_user_profile(self, profile):
        bmi = self.calculate_bmi(profile)
        bmi_category = self.get_bmi_category(bmi)
        return {
            "Стать": profile.gender,
            "Рівень підготовки": profile.fitness_level,
            "М’язові групи": ", ".join(profile.goal_muscle_groups),
            "Складність": profile.preferred_difficulty,
            "Вага": f"{profile.weight} кг",
            "Зріст": f"{profile.height} см",
            "ІМТ": f"{bmi} ({bmi_category})"
        }

    def update_exercise_feedback(self, profile, exercise_name, feedback):
        try:
            if isinstance(feedback, ExerciseFeedback):
                profile.exercise_feedback[exercise_name] = feedback
            else:
                return "Невірний тип відгуку. Очікується ExerciseFeedback."
            self.save_user_profile(profile)
            return True
        except Exception as e:
            return f"Помилка під час збереження відгуку: {str(e)}"

    def delete_user_profile(self):
        if os.path.exists(self._user_profile_file_path):
            os.remove(self._user_profile_file_path)