from training_plan import CardioPlan, StrengthPlan, SplitPlan, FullBodyPlan
from user_profile import UserProfile


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