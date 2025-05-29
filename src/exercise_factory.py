from abc import ABC, abstractmethod
from exercise import Exercise
from user_profile import UserProfile

class IExerciseFactory(ABC):
    @abstractmethod
    def create_exercises(self, user_profile, training_location):
        pass


class GymStrengthExercisesForMenFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Жим лежачи", "strength", "chest", "Barbell", 4.0),
            Exercise("Жим під нахилом", "strength", "chest", "Barbell", 4.0),
            Exercise("Жим під негативним нахилом", "strength", "chest", "Barbell", 4.0),
            Exercise("Розведення гантелей лежачи", "strength", "chest", "Dumbbells", 3.5),
            Exercise("Віджимання", "strength", "chest", met=3.0),

            Exercise("Присідання", "strength", "legs", "Barbell", 5.0),
            Exercise("Жим ногами", "strength", "legs", "Leg Press Machine", 4.5),
            Exercise("Станова тяга", "strength", "legs", "Barbell", 5.0),
            Exercise("Випади", "strength", "legs", "Bodyweight", 3.5),
            Exercise("Підйом на литки", "strength", "legs", "Smith Machine", 4.0),

            Exercise("Підтягування", "strength", "back", "Pull-Up Bar", 5.0),
            Exercise("Тяга верхнього блоку", "strength", "back", "Cable Machine", 4.0),
            Exercise("Тяга в горизонтальному блоці", "strength", "back", "Cable Machine", 4.0),
            Exercise("Тяга Т-штанги", "strength", "back", "T-Bar Row Machine", 4.0),
            Exercise("Гіперекстензії", "strength", "back", "Hyperextension Bench", 3.5),

            Exercise("Жим над головою", "strength", "shoulders", "Barbell", 4.0),
            Exercise("Жим гантелей над головою", "strength", "shoulders", "Dumbbells", 4.0),
            Exercise("Бічні підйоми в тросах", "strength", "shoulders", "Cable Machine", 3.0),
            Exercise("Жим Арнольда", "strength", "shoulders", "Dumbbells", 3.5),

            Exercise("Згинання рук з гантелями", "strength", "arms", "Dumbbells", 3.5),
            Exercise("Молоткові згинання", "strength", "arms", "Dumbbells", 3.5),
            Exercise("Віджимання на брусах", "strength", "arms", "Parallel Bars", 4.0),
            Exercise("Тяга троса на трицепс", "strength", "arms", "Cable Machine", 3.5),

            Exercise("Планка", "strength", "core", met=2.5),
            Exercise("Російські скручування", "strength", "core", met=3.0),
            Exercise("Підйом ніг", "strength", "core", met=3.5),
            Exercise("Бічна планка", "strength", "core", met=2.5),
            Exercise("Підйом колін у висі", "strength", "core", "Pull-Up Bar", 3.0)
        ]
        for ex in exercises:
            max_weights = {
                "Жим лежачи": 80,
                "Жим під нахилом": 70,
                "Жим під негативним нахилом": 75,
                "Розведення гантелей лежачи": 20,
                "Присідання": 100,
                "Жим ногами": 200,
                "Станова тяга": 120,
                "Підйом на литки": 60,
                "Тяга верхнього блоку": 60,
                "Тяга в горизонтальному блоці": 70,
                "Тяга Т-штанги": 80,
                "Жим над головою": 50,
                "Жим гантелей над головою": 25,
                "Бічні підйоми в тросах": 15,
                "Жим Арнольда": 20,
                "Згинання рук з гантелями": 15,
                "Молоткові згинання": 20,
                "Тяга троса на трицепс": 25
            }
            ex.max_weight = max_weights.get(ex.name, 0)
        return exercises


class GymStrengthExercisesForWomenFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Жим гантелями лежачи", "strength", "chest", "Dumbbells", 3.5),
            Exercise("Віджимання", "strength", "chest", met=3.0),

            Exercise("Присідання", "strength", "legs", met=4.0),
            Exercise("Тазові підйоми", "strength", "legs", "Barbell", 4.5),
            Exercise("Глютеальний міст", "strength", "legs", met=3.5),
            Exercise("Жим ногами", "strength", "legs", "Leg Press Machine", 4.0),
            Exercise("Бічні випади", "strength", "legs", met=3.5),

            Exercise("Тяга гантелі однією рукою", "strength", "back", "Dumbbell", 4.0),
            Exercise("Тяга верхнього блоку", "strength", "back", "Lat Pulldown Machine", 4.0),

            Exercise("Жим над головою", "strength", "shoulders", "Dumbbells", 4.0),

            Exercise("Відведення рук на трицепс", "strength", "arms", "Dumbbells", 3.5),
            Exercise("Молоткові згинання", "strength", "arms", "Dumbbells", 3.5),

            Exercise("Планка", "strength", "core", met=2.5),
            Exercise("Російські скручування", "strength", "core", met=3.0),
            Exercise("Бічна планка", "strength", "core", met=2.5)
        ]
        for ex in exercises:
            max_weights = {
                "Жим гантелями лежачи": 30,
                "Тазові підйоми": 60,
                "Жим ногами": 120,
                "Тяга гантелі однією рукою": 25,
                "Жим над головою": 20,
                "Відведення рук на трицепс": 15,
                "Молоткові згинання": 18
            }
            ex.max_weight = max_weights.get(ex.name, 0)
        return exercises


class HomeStrengthExercisesFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Віджимання", "strength", "chest", met=3.0),
            Exercise("Віджимання з нахилом", "strength", "chest", met=3.0),
            Exercise("Віджимання з негативним нахилом", "strength", "chest", met=3.0),
            Exercise("Широкі віджимання", "strength", "chest", met=3.0),

            Exercise("Присідання", "strength", "legs", met=4.0),
            Exercise("Глютеальний міст", "strength", "legs", met=3.5),
            Exercise("Підйом на сходинку", "strength", "legs", met=4.0),
            Exercise("Стілець біля стіни", "strength", "legs", met=3.0),
            Exercise("Випади", "strength", "legs", met=3.5),

            Exercise("Супермен", "strength", "back", met=3.0),
            Exercise("Зворотні снігові янголи", "strength", "back", met=2.5),
            Exercise("Пташка-собака", "strength", "back", met=2.5),
            Exercise("Вправа плавання", "strength", "back", met=3.0),

            Exercise("Віджимання пік", "strength", "shoulders", met=3.5),
            Exercise("Круги руками", "strength", "shoulders", met=2.0),
            Exercise("Стійка на руках біля стіни", "strength", "shoulders", met=2.5),
            Exercise("Бічна планка з підйомом руки", "strength", "shoulders", met=2.5),

            Exercise("Віджимання від стільця", "strength", "arms", "Chair", 4.0),
            Exercise("Діамантові віджимання", "strength", "arms", met=3.5),
            Exercise("Ізометричне утримання рук", "strength", "arms", met=2.5),
            Exercise("Удари в планці", "strength", "arms", met=3.0),

            Exercise("Планка", "strength", "core", met=2.5),
            Exercise("Бічна планка", "strength", "core", met=2.5),
            Exercise("Російські скручування", "strength", "core", met=3.0),
            Exercise("Підйом ніг", "strength", "core", met=3.5),
            Exercise("Альпіністи", "strength", "core", met=4.0)
        ]
        return exercises


class GymCardioExercisesFactory(IExerciseFactory):
    def create_exercises(self, user_profile, training_location):
        exercises = [
            Exercise("Біг на доріжці", "cardio", "dynamic", "Treadmill", 9.8),
            Exercise("Велотренажер", "cardio", "dynamic", "Stationary Bike", 8.0),
            Exercise("Гребний тренажер", "cardio", "dynamic", "Rowing Machine", 7.0),
            Exercise("Еліптичний тренажер", "cardio", "dynamic", "Elliptical Machine", 5.5),
            Exercise("Лыжний ергометр", "cardio", "dynamic", "Ski Ergometer", 6.0),
            Exercise("Сходовий тренажер", "cardio", "dynamic", "Stair Climber", 8.0),
            Exercise("Спринти", "cardio", "dynamic", met=10.0),

            Exercise("Стрибки зі скакалкою", "cardio", "static", "Jump Rope", 10.0),
            Exercise("Танцювальне кардіо", "cardio", "static", met=5.0),
            Exercise("Вправи на спритність", "cardio", "static", "Agility Ladder", 6.0),
            Exercise("Стрибки зірочкою", "cardio", "static", met=7.0),
            Exercise("Тіньовий бокс", "cardio", "static", met=6.0),
            Exercise("Канати", "cardio", "static", "Battle Ropes", 7.0),
            Exercise("Високі коліна", "cardio", "static", met=7.0),
            Exercise("Бурпі", "cardio", "static", met=7.0),
            Exercise("Альпіністи", "cardio", "static", met=7.0),
            Exercise("Торкання плечей у планці", "cardio", "static", met=5.0),
            Exercise("Плавання на місці", "cardio", "static", "Pool", 5.0)
        ]
        for ex in exercises:
            settings = {
                "Біг на доріжці": {"speed": 8.0, "freq": 140, "dist": 10.0},
                "Велотренажер": {"speed": 18.0, "freq": 130, "dist": 15.0},
                "Гребний тренажер": {"speed": 10.0, "freq": 130, "dist": 7.0},
                "Еліптичний тренажер": {"speed": 12.0, "freq": 135, "dist": 8.0},
                "Лыжний ергометр": {"speed": 9.0, "freq": 120, "dist": 5.0},
                "Сходовий тренажер": {"speed": 5.0, "freq": 125, "dist": 4.0},
                "Спринти": {"speed": 15.0, "freq": 160, "dist": 1.0},
                "Стрибки зі скакалкою": {"freq": 150},
                "Танцювальне кардіо": {"freq": 130},
                "Вправи на спритність": {"freq": 140},
                "Стрибки зірочкою": {"freq": 120},
                "Тіньовий бокс": {"freq": 115},
                "Канати": {"freq": 130},
                "Високі коліна": {"freq": 110},
                "Бурпі": {"freq": 115},
                "Альпіністи": {"freq": 115},
                "Торкання плечей у планці": {"freq": 120},
                "Плавання на місці": {"freq": 100}
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
            Exercise("Велосипед", "cardio", "dynamic", "Bicycle", 7.0),
            Exercise("Похід", "cardio", "dynamic", "Hiking Boots", 5.0),
            Exercise("Ходьба", "cardio", "dynamic", met=3.8),
            Exercise("Плавання", "cardio", "dynamic", "Pool", 6.0),
            Exercise("Спринти", "cardio", "dynamic", met=10.0),

            Exercise("Стрибки зі скакалкою", "cardio", "static", "Jump Rope", 10.0),
            Exercise("Альпіністи", "cardio", "static", met=6.0),
            Exercise("Високі коліна", "cardio", "static", met=6.0),
            Exercise("Стрибки зірочкою", "cardio", "static", met=6.0),
            Exercise("Бурпі", "cardio", "static", met=6.0),
            Exercise("Тіньовий бокс", "cardio", "static", met=6.0)
        ]
        for ex in exercises:
            settings = {
                "Біг по стежці": {"speed": 8.0, "freq": 130, "dist": 10.0},
                "Велосипед": {"speed": 15.0, "freq": 135, "dist": 15.0},
                "Похід": {"speed": 6.0, "freq": 120, "dist": 20.0},
                "Ходьба": {"speed": 5.0, "freq": 100, "dist": 5.0},
                "Плавання": {"speed": 7.0, "freq": 110, "dist": 2.0},
                "Спринти": {"speed": 15.0, "freq": 160, "dist": 0.5},
                "Стрибки зі скакалкою": {"freq": 150},
                "Альпіністи": {"freq": 115},
                "Високі коліна": {"freq": 110},
                "Стрибки зірочкою": {"freq": 120},
                "Бурпі": {"freq": 115},
                "Тіньовий бокс": {"freq": 120}
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
            Exercise("Високі коліна", "cardio", "static", met=8.0),
            Exercise("Альпіністи", "cardio", "static", met=8.0),
            Exercise("Підйом на сходинку", "cardio", "static", "Chair", 4.0),
            Exercise("Тіньовий бокс", "cardio", "static", met=7.0),
            Exercise("Стрибки в планці", "cardio", "static", met=5.0),
            Exercise("Стрибки з боку в бік", "cardio", "static", met=6.0),
            Exercise("Танцювальне кардіо", "cardio", "static", met=6.0),
            Exercise("Підйом по сходах", "cardio", "static", "Stairs", 5.0),
            Exercise("Велотренажер у приміщенні", "cardio", "static", "Stationary Bike", 8.0),
            Exercise("Ходьба на доріжці", "cardio", "static", "Treadmill", 4.0)
        ]
        for ex in exercises:
            settings = {
                "Стрибки зірочкою": {"freq": 120},
                "Бурпі": {"freq": 115},
                "Високі коліна": {"freq": 110},
                "Альпіністи": {"freq": 115},
                "Підйом на сходинку": {"freq": 120},
                "Тіньовий бокс": {"freq": 120},
                "Стрибки в планці": {"freq": 110},
                "Стрибки з боку в бік": {"freq": 115},
                "Танцювальне кардіо": {"freq": 130},
                "Підйом по сходах": {"freq": 130},
                "Велотренажер у приміщенні": {"freq": 135},
                "Ходьба на доріжці": {"freq": 120}
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