from abc import ABC, abstractmethod
from user_profile import UserProfile
from exercise import Exercise
from user_profile import ExerciseFeedback
import random

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
            return None, "Немає доступних кардіо вправ."
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