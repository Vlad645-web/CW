import json
import os
import datetime
from training_archive import TrainingArchiveEntry

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