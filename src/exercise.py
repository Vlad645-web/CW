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