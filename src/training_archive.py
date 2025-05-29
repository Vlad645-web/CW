from datetime import datetime
from exercise import Exercise

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
