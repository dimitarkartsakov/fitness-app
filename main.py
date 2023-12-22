from kivy.app import App
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.datatables import MDDataTable
from kivy.uix.floatlayout import FloatLayout
from kivy.metrics import dp
from kivy.properties import ListProperty
from kivymd.toast.kivytoast.kivytoast import toast
from kivy.uix.popup import Popup
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton


import sqlite3
import database
from database import *


currently_logged_id = ""
selected_trainer_id = ""
selected_trainee_id = ""
selected_workout_id = ""

class WindowManager(ScreenManager):
    pass


class TraineeNavWindow(Screen):
    def __init__(self, **kwargs):
        super(TraineeNavWindow, self).__init__(**kwargs)
        self.popup = None
    def populate_workouts(self):
        list_workouts_trainee = self.ids.list_workouts_trainee
        list_workouts_trainee.clear_widgets()

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Workout""")

        workouts_seed = cur.fetchall()

        for workout in workouts_seed:
            list_workouts_trainee.add_widget(
                TwoLineListItem(
                    text=f"{workout[1]}",
                    secondary_text=
                    f"Category: {workout[4]}, "
                    f"Duration: {workout[2]}, "
                    f"Difficulty: {workout[3]}, "
                    f"Created By: {workout[5]}"
                )
            )

        conn.close()

    def filter_workouts(self, chosen_category=None):
        list_workouts_trainee = self.ids.list_workouts_trainee
        list_workouts_trainee.clear_widgets()

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Workout WHERE
            category=? 
        """, (chosen_category,))

        workouts_seed = cur.fetchall()

        if chosen_category == "All Categories":
            self.populate_workouts()
        else:

            for workout in workouts_seed:
                list_workouts_trainee.add_widget(
                    TwoLineListItem(
                        text=f"{workout[1]}",
                        secondary_text=
                        f"Category: {workout[4]}, "
                        f"Duration: {workout[2]}, "
                        f"Difficulty: {workout[3]}, "
                        f"Created By: {workout[5]}"
                    )
                )

    def fetch_profile_info(self):
        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Trainee WHERE
            id=?
        """, (currently_logged_id,))

        trainee = cur.fetchone()
        trainee_first_name = f"First name:  {trainee[1]}"
        self.ids.my_profile_first_name.text = trainee_first_name
        trainee_last_name = f"Last name:  {trainee[2]}"
        self.ids.my_profile_last_name.text = trainee_last_name
        trainer_account_creation_date = f"Member since:  {(trainee[4])[0:-8]}"
        self.ids.my_profile_creation_date.text = trainer_account_creation_date

        trainer_to_find_id = trainee[3]
        if trainer_to_find_id is not None:
            cur.execute("""SELECT * FROM Trainer WHERE id=?
            """, (trainer_to_find_id,))
            trainer_found = cur.fetchone()
            trainer_found_names = f"Current trainer: {trainer_found[1]} {trainer_found[2]}"
            self.ids.my_current_trainer.text = trainer_found_names
        else:
            self.ids.my_current_trainer.text = "Current trainer: Not selected"

        conn.close()

    def populate_trainers(self):
        list_trainers = self.ids.list_trainers
        list_trainers.clear_widgets()

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Trainer""")

        trainers_seed = cur.fetchall()

        for trainer in trainers_seed:
            item=ThreeLineListItem(
                text=
                f"{trainer[1]} {trainer[2]} ",
                secondary_text=
                f"Trainer since: {(trainer[4])[0:-8]} "
                f"Rating: /5",
                tertiary_text= f"Trainer work ID: {trainer[0]}")
            item.bind(on_release=self.choose_trainer)
            self.ids.list_trainers.add_widget(item)

        conn.close()

    def choose_trainer(self, instance):
        global selected_trainer_id
        selected_trainer_id = instance.tertiary_text.split(":")[-1].strip()
        self.create_confirmation_dialog(selected_trainer_id)

    def create_confirmation_dialog(self, trainer_id):
        self.dialog = MDDialog(
            title="Confirm Assignment",
            text=f"Would you like to confirm you choose this trainer?",
            buttons=[
                MDFlatButton(
                    text="Yes",
                    on_release=lambda x: self.confirm_assignment(trainer_id),
                ),
                MDFlatButton(
                    text="No",
                    on_release=self.close_confirmation_dialog,
                ),
            ],
        )
        self.dialog.open()

    def close_confirmation_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def confirm_assignment(self, trainer_id):
        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""UPDATE trainee
            SET trainerID=?
            WHERE ID=?        
        """, (selected_trainer_id, currently_logged_id))
        conn.commit()
        conn.close()
        self.close_confirmation_dialog()





class TrainerNavWindow(Screen):
    def __init__(self, **kwargs):
        super(TrainerNavWindow, self).__init__(**kwargs)

    def create_workout(self):
        global currently_logged_id
        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        workout_name = self.ids.workout_name.text
        workout_duration = self.ids.workout_duration.text
        workout_difficulty = self.ids.workout_difficulty.text
        workout_category = self.ids.workout_category.text
        currently_logged_id = currently_logged_id

        cur.execute("""
            SELECT * FROM Trainer 
            WHERE ID=?
        """, (currently_logged_id,))

        trainer = cur.fetchone()

        if (workout_name.strip() and
                workout_duration.strip() and
                workout_difficulty.strip() and
                workout_category.strip()):
            cur.execute("""
            INSERT INTO Workout(Name, Duration, Difficulty, Category, CreatedByID)
            VALUES(?, ?, ?, ?, ?)
        """, (workout_name, workout_duration, workout_difficulty, workout_category, f"{trainer[1]} {trainer[2]}"))

        conn.commit()
        conn.close()

    def clear_text_fields(self):
        self.ids.workout_name.text = ""
        self.ids.workout_duration.text = ""
        self.ids.workout_difficulty.text = ""
        self.ids.workout_category.text = ""

    def populate_workouts(self):
        list_workouts = self.ids.list_workouts
        list_workouts.clear_widgets()

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Workout""")

        workouts_seed = cur.fetchall()

        for workout in workouts_seed:
            item = ThreeLineListItem(
                text=
                f"{workout[1]}",
                secondary_text=
                f"Category: {workout[4]}, "
                f"Duration: {workout[2]}, "
                f"Difficulty: {workout[3]}, "
                f"Created By: {workout[5]}",
                tertiary_text=
                f"Workout ID: {workout[0]}")
            item.bind(on_release=self.select_workout)
            self.ids.list_workouts.add_widget(item)

        conn.close()

    def filter_workouts(self, chosen_category=None):
        list_workouts = self.ids.list_workouts
        list_workouts.clear_widgets()

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Workout WHERE
            category=? 
        """, (chosen_category,))

        workouts_seed = cur.fetchall()

        if chosen_category == "All Categories":
            self.populate_workouts()
        else:
            for workout in workouts_seed:
                item=ThreeLineListItem(
                    text=
                    f"{workout[1]}",
                    secondary_text=
                    f"Category: {workout[4]}, "
                    f"Duration: {workout[2]}, "
                    f"Difficulty: {workout[3]}, "
                    f"Created By: {workout[5]}",
                    tertiary_text =
                    f"Workout ID: {workout[0]}")
                item.bind(on_release=self.select_workout)
                self.ids.list_workouts.add_widget(item)

        conn.close()

    def fetch_profile_info(self):
        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Trainer WHERE
            id=?
        """, (currently_logged_id,))

        trainer = cur.fetchone()
        trainer_first_name = f"First name:  {trainer[1]}"
        self.ids.my_profile_first_name.text = trainer_first_name
        trainer_last_name = f"Last name:  {trainer[2]}"
        self.ids.my_profile_last_name.text = trainer_last_name
        trainer_account_creation_date = f"Member since:  {trainer[4]}"
        self.ids.my_profile_creation_date.text = trainer_account_creation_date
        conn.close()

    def populate_my_trainees(self):
        global currently_logged_id
        list_trainees = self.ids.list_trainees
        list_trainees.clear_widgets()

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""SELECT * FROM Trainee
            WHERE trainerID=?
        """, (currently_logged_id, ))

        trainees_seed = cur.fetchall()

        for trainee in trainees_seed:
            item=ThreeLineListItem(
                text=
                f"{trainee[1]} {trainee[2]} ",
                secondary_text=
                f"Trainee since: {(trainee[4])[0:-8]} ",
                tertiary_text=
                f"Trainee user ID: {trainee[0]}")
            item.bind(on_release=self.select_trainee)
            self.ids.list_trainees.add_widget(item)

        conn.close()

    def select_workout(self, instance):
        global selected_workout_id
        selected_workout_id = instance.tertiary_text.split(":")[-1].strip()
        print("Workout Selected")
        self.assign_workout_to_trainee()
        print("Workout assigned")


    def toast_workout_added(self):
        toast("Workout Added Successfully")

    def select_trainee(self, instance):
        global selected_trainee_id
        selected_trainee_id = instance.tertiary_text.split(":")[-1].strip()
        print("Trainee selected")
        print(selected_trainee_id)

    def assign_workout_to_trainee(self):
        global selected_trainee_id
        global selected_workout_id
        self.toast_workout_added()

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        if selected_workout_id and selected_trainee_id:
            cur.execute("""UPDATE trainee
            SET CurrentWorkoutID=?
            WHERE ID=?        
        """, (selected_workout_id, selected_trainee_id))

        conn.commit()
        conn.close()

class LoginWindow(Screen):
    def __init__(self, **kwargs):
        super(LoginWindow, self).__init__(**kwargs)

    def login_user(self):
        global currently_logged_id
        currently_logged_id = ""
        username = self.ids.username.text
        password = self.ids.password.text

        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        cur.execute("""
            SELECT * FROM Login WHERE
            username=? AND password=?
        """, (username, password))

        user = cur.fetchone()

        if user:
            if user[3] == "trainee":
                cur.execute("""
                    SELECT * FROM Trainee WHERE
                    id=?
                """, (user[0],))
                self.manager.current = "trainee_nav_window"
                self.manager.transition.direction = "right"
                currently_logged_id = user[0]
            elif user[3] == "trainer":
                cur.execute("""
                    SELECT * FROM Trainer WHERE
                    id=?
                """, (user[0],))
                self.manager.current = "trainer_nav_window"
                self.manager.transition.direction = "right"
                currently_logged_id = user[0]
        else:
            self.toast_error()

    def clear_text_fields(self):
        self.ids.username.text = ""
        self.ids.password.text = ""

    def toast_error(self):
        toast("Invalid username or password. Please try again!")





class RegisterWindow(Screen):
    def __init__(self, **kwargs):
        super(RegisterWindow, self).__init__(**kwargs)

    def register_user(self):
        global currently_logged_id
        currently_logged_id = ""
        conn = database.sqlite3.connect('fitness_app2.db')
        cur = conn.cursor()

        firstname = self.ids.firstname.text
        lastname = self.ids.lastname.text
        username = self.ids.username.text
        password = self.ids.password.text
        role = self.ids.role.text

        try:
            cur.execute("""
                INSERT INTO Login(Username, Password, Role)
                VALUES(?, ?, ?)
            """, (username, password, role))

            id = cur.lastrowid

            new_user = User(id, firstname, lastname, username, password, role)

            if role == "trainer":
                cur.execute("""
                    INSERT INTO Trainer(ID, FirstName, LastName)
                    VALUES (?, ?, ?)
                """, (new_user.id, new_user.firstname, new_user.lastname))
                self.manager.current = "trainer_nav_window"
                self.manager.transition.direction = "right"
                print("TRAINER CREATED FINALLY")
                currently_logged_id = new_user.id
                self.clear_text_fields()
            elif role == "trainee":
                cur.execute("""
                    INSERT INTO Trainee(ID, FirstName, LastName)
                    VALUES (?, ?, ?)
                """, (new_user.id, new_user.firstname, new_user.lastname))
                self.manager.current = "trainee_nav_window"
                self.manager.transition.direction = "right"
                print("TRAINEE CREATED FINALLY")
                currently_logged_id = new_user.id
                self.clear_text_fields()
            conn.commit()
            conn.close()

        except sqlite3.IntegrityError:
            self.clear_text_fields()
            raise NonUniqueUsernameError(
                "Username already exists. Please choose a different one.")

    def clear_text_fields(self):
        self.ids.firstname.text = ""
        self.ids.lastname.text = ""
        self.ids.username.text = ""
        self.ids.password.text = ""
        self.ids.role.text = ""
class NonUniqueUsernameError(Exception):
    pass

class MyFitnessApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "DeepOrange"
        return WindowManager()


if __name__ == '__main__':
    MyFitnessApp().run()
