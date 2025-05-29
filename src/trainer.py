import threading
import time

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