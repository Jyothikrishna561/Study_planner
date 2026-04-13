
from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
app = Flask(__name__)
from openai import OpenAI
import os
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

mongo_client = MongoClient("mongodb://localhost:27017/")
db = mongo_client["study_planner"]
collection = db["tasks"]




from datetime import datetime

@app.route('/')
def home():
    tasks = list(collection.find())

    today = datetime.today().date()

    for task in tasks:
        task["status"] = "normal"

        if task.get("due_date"):
            try:
                due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
                today = datetime.today().date()

                if due < today and not task["completed"]:
                    task["status"] = "overdue"
                elif due == today:
                    task["status"] = "today"
                else:
                    task["status"] = "upcoming"

            except:
                task["status"] = "normal"

# 🔥 ADD THIS BLOCK HERE (IMPORTANT)
    tasks.sort(key=lambda task: (
        task["status"] != "overdue",
        task["priority"] != "high",
        task["priority"] != "medium",
        task["priority"] != "low"
    ))

# 👇 THIS LINE SHOULD COME AFTER SORTING
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task["completed"])

    if total_tasks == 0:
        progress = 0
    else:
        progress = int((completed_tasks / total_tasks) * 100)

    if progress == 0:
        emoji = "😴"
    elif progress < 40:
        emoji = "🙂"
    elif progress < 70:
        emoji = "🔥"
    elif progress < 100:
        emoji = "🎯"
    else:
        emoji = "🎉"

    if total_tasks == 0:
        message = "Start adding tasks ✍️"
    elif completed_tasks == 0:
        message = "Try to complete at least one task 💪"
    elif completed_tasks == total_tasks:
        message = "Awesome! All tasks completed 🎉"
    elif completed_tasks >= total_tasks / 2:
        message = "Great progress 🔥 Keep going!"
    else:
        message = "You can do better 😎"

    return render_template(
        'index.html',
        tasks=tasks,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        message=message,
        progress=progress,
        emoji=emoji
    )


"""@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    if task:
        tasks.append({"text": task, "completed": False})
    
    return redirect('/')"""



@app.route('/delete/<id>')
def delete(id):
    collection.delete_one({"_id": ObjectId(id)})
    return redirect('/')
"""@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    priority = request.form.get('priority')

    if task:
        collection.insert_one({
            "text": task,
            "completed": False,
            "priority": priority
        })

    return redirect('/')"""
@app.route('/toggle/<id>')
def toggle(id):
    task = collection.find_one({"_id": ObjectId(id)})

    collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"completed": not task["completed"]}}
    )

    return redirect('/')


@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    task = collection.find_one({"_id": ObjectId(id)})

    if request.method == 'POST':
        new_text = request.form['task']

        if new_text.strip() != "":
            collection.update_one(
                {"_id": ObjectId(id)},
                {"$set": {"text": new_text}}
            )

        return redirect('/')

    return render_template('edit.html', task=task, id=id)
@app.route('/ai_suggest')
def ai_suggest():
    tasks = list(collection.find())

    if not tasks:
        result = "Add some tasks first ✍️"
    else:
        high = [t["text"] for t in tasks if t["priority"] == "high"]
        medium = [t["text"] for t in tasks if t["priority"] == "medium"]
        low = [t["text"] for t in tasks if t["priority"] == "low"]

        result = "📊 AI Suggestions:\n\n"

        if high:
            result += f"👉 Start with HIGH priority: {high[0]}\n\n"
        elif medium:
            result += f"👉 Start with MEDIUM priority: {medium[0]}\n\n"
        else:
            result += f"👉 Start with LOW priority: {low[0]}\n\n"

        result += "💡 Tip: Focus on one task at a time\n"
        result += "🚀 You are doing great, keep going!"

    return render_template("ai.html", result=result)
@app.route('/add', methods=['POST'])
def add():
    task = request.form.get('task')
    priority = request.form.get('priority')
    due_date = request.form.get('due_date')

    if task:
        collection.insert_one({
            "text": task,
            "completed": False,
            "priority": priority,
            "due_date": due_date
        })

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)


