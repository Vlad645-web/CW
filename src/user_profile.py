import json
import os
from enum import Enum

class ExerciseFeedback(Enum):
    EASY = "Easy"
    NORMAL = "Normal"
    HARD = "Hard"


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

    @property
    def fitness_level(self):
        return self._fitness_level

    @fitness_level.setter
    def fitness_level(self, value):
        if 1 <= value <= 10:
            self._fitness_level = value

    @property
    def preferred_difficulty(self):
        return self._preferred_difficulty

    @preferred_difficulty.setter
    def preferred_difficulty(self, value):
        if value in ["Easy", "Medium", "Hard"]:
            self._preferred_difficulty = value

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, value):
        if value > 0:
            self._weight = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        if value > 0:
            self._height = value

    @property
    def gender(self):
        return self._gender

    @gender.setter
    def gender(self, value):
        if value in ["Male", "Female"]:
            self._gender = value

    @property
    def goal_muscle_groups(self):
        return self._goal_muscle_groups

    @goal_muscle_groups.setter
    def goal_muscle_groups(self, value):
        self._goal_muscle_groups = value

    @property
    def last_strength_values(self):
        return self._last_strength_values

    @last_strength_values.setter
    def last_strength_values(self, value):
        self._last_strength_values = value

    @property
    def exercise_feedback(self):
        return self._exercise_feedback

    @exercise_feedback.setter
    def exercise_feedback(self, value):
        self._exercise_feedback = value

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