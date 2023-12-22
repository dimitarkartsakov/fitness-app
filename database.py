import sqlite3


conn = sqlite3.connect('fitness_app2.db')
cursor = conn.cursor()



class Workout:
    def __init__(self, name, duration, difficulty, category, created_by):
        self.name = name
        self.duration = duration
        self.difficulty = difficulty
        self.category = category
        self.created_by = created_by



class Exercise:
    def __init__(self, name, sets, reps):
        self.name = name
        self.sets = sets
        self.reps = reps


# Define the WorkoutExercises class (many-to-many relationship)
class WorkoutExercises:
    def __init__(self, workout, exercise):
        self.workout = workout
        self.exercise = exercise



class Login:
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

class User:
    def __init__(self, id, firstname, lastname, username, password, role):
        self.id = id
        self.firstname = firstname
        self.lastname = lastname
        self.username = username
        self.password = password
        self.role = role


class Trainee(User):
    def __init__(self, firstname, lastname, my_trainer=None, current_workout=None):
        super().__init__(None, firstname, lastname, None, None, 'trainee')
        self.my_trainer = my_trainer
        self.current_workout = current_workout
        self.workout_history = []


class Trainer(User):
    def __init__(self, firstname, lastname):
        super().__init__(None, firstname, lastname, None, None, 'trainer')
        self.trainees = []
        self.myworkouts = []


cursor.execute('''
    CREATE TABLE IF NOT EXISTS Workout (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Duration INTEGER,
        Difficulty TEXT,
        Category TEXT,
        CreatedByID INTEGER,
        FOREIGN KEY (CreatedByID) REFERENCES Trainer (ID)
        
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Exercise (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Sets INTEGER,
        Reps INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS WorkoutExercises (
        WorkoutID INTEGER,
        ExerciseID INTEGER,
        FOREIGN KEY (WorkoutID) REFERENCES Workout (ID),
        FOREIGN KEY (ExerciseID) REFERENCES Exercise (ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Login (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Username TEXT,
        Password TEXT,
        Role TEXT,
        TrainerID INTEGER,
        TraineeID INTEGER,
        FOREIGN KEY (TrainerID) REFERENCES Trainer (ID),
        FOREIGN KEY (TraineeID) REFERENCES Trainee (ID)   
    )
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Role TEXT NOT NULL,
    FirstName TEXT NOT NULL,
    LastName TEXT NOT NULL,
    Username TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL
)
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Trainer (
        ID INTEGER PRIMARY KEY,
        FirstName TEXT,
        LastName TEXT,
        TraineeID INTEGER,
        RegistrationDate TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (TraineeID) REFERENCES Trainee (ID)
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Trainee (
        ID INTEGER PRIMARY KEY,
        FirstName TEXT,
        LastName TEXT,
        TrainerID INTEGER,
        RegistrationDate TEXT DEFAULT CURRENT_TIMESTAMP,
        CurrentWorkoutID INTEGER,
        FOREIGN KEY (TrainerID) REFERENCES Trainer (ID),
        FOREIGN KEY (CurrentWorkoutID) REFERENCES Workout (ID)
    )
''')


conn.commit()
conn.close()
