import sqlite3
import tkinter as tk
import turtle
from datetime import datetime, timedelta

# Connect to SQLite database
conn = sqlite3.connect("workout_progress.db")
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''CREATE TABLE IF NOT EXISTS progress 
                  (user_id TEXT, exercise TEXT, sets INTEGER, reps INTEGER, weight INTEGER, date TEXT)''')
conn.commit()

# Sample workout data with progressive exercises
workout_data = {
    "muscle_gain": {
        "bodyweight": [
            {"exercise": "Push-ups", "sets": 4, "reps": 12},
            {"exercise": "Squats", "sets": 4, "reps": 15},
            {"exercise": "Pull-ups", "sets": 3, "reps": 10}
        ],
        "gym": [
            {"exercise": "Bench Press", "sets": 4, "reps": 8, "weight": 40},
            {"exercise": "Squats", "sets": 4, "reps": 10, "weight": 60},
            {"exercise": "Deadlifts", "sets": 3, "reps": 6, "weight": 80}
        ]
    }
}

# Advanced exercises (added if progress is detected)
advanced_exercises = {
    "Push-ups": "Archer Push-ups",
    "Squats": "Bulgarian Split Squats",
    "Pull-ups": "Weighted Pull-ups",
    "Bench Press": "Incline Bench Press",
    "Deadlifts": "Romanian Deadlifts"
}

# Tkinter GUI setup
root = tk.Tk()
root.title("AI Workout Assistant")

# Labels & Input Fields
tk.Label(root, text="User ID").grid(row=0, column=0)
user_entry = tk.Entry(root)
user_entry.grid(row=0, column=1)

tk.Label(root, text="Workout Goal (muscle_gain)").grid(row=1, column=0)
goal_entry = tk.Entry(root)
goal_entry.grid(row=1, column=1)

tk.Label(root, text="Workout Type (bodyweight/gym)").grid(row=2, column=0)
type_entry = tk.Entry(root)
type_entry.grid(row=2, column=1)

tk.Label(root, text="Sets Completed").grid(row=3, column=0)
sets_entry = tk.Entry(root)
sets_entry.grid(row=3, column=1)

tk.Label(root, text="Reps Completed").grid(row=4, column=0)
reps_entry = tk.Entry(root)
reps_entry.grid(row=4, column=1)

tk.Label(root, text="Weight Used (if gym)").grid(row=5, column=0)
weight_entry = tk.Entry(root)
weight_entry.grid(row=5, column=1)

# Turtle Setup
turtle_screen = turtle.Screen()
turtle_screen.title("Workout Progress")
t = turtle.Turtle()
t.speed(0)

# AI Adjustment Logic
def adjust_workout():
    user_id = user_entry.get()
    goal = goal_entry.get()
    workout_type = type_entry.get()
    sets_completed = int(sets_entry.get())
    reps_completed = int(reps_entry.get())
    weight_used = int(weight_entry.get()) if weight_entry.get() else 0

    if goal not in workout_data or workout_type not in workout_data[goal]:
        result_label.config(text="Invalid goal or type")
        return

    exercise = workout_data[goal][workout_type][0]  # First exercise for demo
    exercise_name = exercise["exercise"]

    # Analyze past progress
    cursor.execute("SELECT reps, weight FROM progress WHERE user_id = ? AND exercise = ? ORDER BY date DESC LIMIT 1",
                   (user_id, exercise_name))
    past_record = cursor.fetchone()

    new_reps, new_weight = reps_completed, weight_used
    add_advanced_exercise = False

    if past_record:
        past_reps, past_weight = past_record

        if reps_completed > past_reps + 2:  # Significant improvement detected
            new_reps += 2
            new_weight += 5 if weight_used else 0
            msg = f"Increase: {new_reps} reps, {new_weight} kg."
            add_advanced_exercise = True
        elif reps_completed < past_reps - 2:  # Performance drop detected
            new_reps = max(5, reps_completed - 2)
            new_weight = max(5, weight_used - 5) if weight_used else 0
            msg = f"Decrease: {new_reps} reps, {new_weight} kg."
        else:
            msg = "Maintain current level."
    else:
        msg = "First time logging this exercise."

    # Save progress in database
    cursor.execute("INSERT INTO progress VALUES (?, ?, ?, ?, ?, datetime('now'))",
                   (user_id, exercise_name, sets_completed, reps_completed, weight_used))
    conn.commit()

    # Add new advanced exercise if progress is detected
    if add_advanced_exercise and exercise_name in advanced_exercises:
        new_exercise = advanced_exercises[exercise_name]
        msg += f" 🚀 New Challenge: Try {new_exercise}!"

    result_label.config(text=msg)
    
    # Draw progress graph
    draw_progress_chart(user_id, exercise_name)

# Function to draw Turtle progress chart
def draw_progress_chart(user_id, exercise_name):
    t.clear()
    t.penup()
    t.goto(-200, 100)
    t.pendown()
    
    cursor.execute("SELECT date, reps FROM progress WHERE user_id = ? AND exercise = ? ORDER BY date ASC", 
                   (user_id, exercise_name))
    data = cursor.fetchall()
    
    if not data:
        t.write("No progress found", font=("Arial", 14, "bold"))
        return

    # Convert date strings to datetime objects
    dates = [datetime.strptime(d[0], "%Y-%m-%d %H:%M:%S") for d in data]
    reps = [d[1] for d in data]

    # Normalize data for plotting
    min_date = min(dates)
    x_positions = [(d - min_date).days * 10 for d in dates]  # Scale for spacing
    max_reps = max(reps)
    
    t.penup()
    for i in range(len(dates)):
        t.goto(-200 + x_positions[i], 100 - reps[i])
        t.pendown()
        t.dot(5, "blue")
        t.write(f" {reps[i]} reps", font=("Arial", 10, "normal"))

# Button to trigger AI
submit_button = tk.Button(root, text="Submit", command=adjust_workout)
submit_button.grid(row=6, column=0, columnspan=2)

# Output Label
result_label = tk.Label(root, text="")
result_label.grid(row=7, column=0, columnspan=2)

# Start GUI
root.mainloop()
