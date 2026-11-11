# Smart Surplus Food Management System

A desktop app that helps manage **surplus (extra) food** and give it to the people who need it, in a fair and organised way.

> Data Structures through C - PBL (Project Based Learning) project

Extra food from hostels, canteens, weddings and events often gets thrown away, while many people nearby are hungry. This app keeps track of the food that is available and the people who are asking for it. **Urgent cases (like a hospital) are served before normal ones.**

---

## Features

- **Dashboard** with live numbers: food types, total plates, normal requests, urgent requests
- **Food Inventory**: add food, search food, delete food
- **Requests**: normal requests and urgent requests (Critical / High / Medium)
- **Serve Food**: serve one request or all requests with one click
- **Activity log** with colours (green = served, orange = partly served, red = food not available)
- **Auto-save**: your data is saved in `data.json` and comes back when you open the app again
- **Load Sample Data** button for a quick demo
- Input checks (empty fields, wrong numbers) with friendly messages

---

## Data structures used

| Data structure | Where it is used | Why |
|---|---|---|
| **Linked List** | Food inventory | Food can be added and removed easily, no fixed size |
| **Queue** (FIFO) | Normal requests | First come, first served |
| **Priority Queue** | Urgent requests | The most urgent request is served first |

All three are written **by hand** (no built-in list tricks) in the first part of `app.py`, with simple comments.

### How serving works

1. If there is any **urgent** request, the most urgent one is served first (same urgency: first come, first served).
2. If there are no urgent requests, the first **normal** request is served.
3. If enough plates are available, the person gets all of them.
4. If fewer plates are left, the person gets what is left.
5. If the food is not available at all, the request is closed.
6. A food is removed from the inventory when its plates become 0.

---

## Project structure

```
Smart-Surplus-Food-Management-System/
├── app.py                  <- MAIN APP (GUI). Run this file.
├── console_version/
│   └── surplus_food.c      <- same project in pure C (text menu)
├── advanced_c_backend/
│   ├── backend.c           <- data structures in C
│   ├── gui.py              <- GUI that calls the C code
│   └── build.bat           <- compiles and runs (Windows)
├── .gitignore
└── README.md
```

---

## How to run the main app (Windows)

You only need **Python**. Nothing else to install (Tkinter comes with Python).

1. Install Python from [python.org](https://www.python.org/downloads/) and tick **"Add Python to PATH"** during installation.
2. Download or clone this repository.
3. Open the project folder in VS Code (or Command Prompt).
4. Run:

```
python app.py
```

(If `python` does not work, try `py app.py`.)

### How to use the app

1. Click **Load Sample Data** (left menu) to see the app with example data.
2. **Food Inventory**: type a food name and plates, then click **Add Food**.
3. **Requests**: enter a name, food and plates. Choose *Normal* or *Urgent* and click **Submit Request**.
4. **Serve Food**: click **Serve Next Request** or **Serve All Requests**.
5. Watch the **Dashboard** numbers change and read the activity log.

---

## Other versions

### Console version (pure C)

Needs a C compiler like `gcc`.

```
cd console_version
gcc surplus_food.c -o surplus_food
surplus_food
```

(On Linux or Mac run `./surplus_food` instead.)

### GUI with C backend

The data structures are in C (`backend.c`) and the window is in Python. On Windows, with `gcc` installed, double-click `advanced_c_backend/build.bat` or run:

```
cd advanced_c_backend
gcc -shared -o backend.dll backend.c
python gui.py
```

---

## Screenshots

<!-- Take screenshots of your app, put them in a folder called "screenshots", then remove these comment marks and fix the file names:

![Dashboard](screenshots/dashboard.png)
![Inventory](screenshots/inventory.png)
![Requests](screenshots/requests.png)
![Serve Food](screenshots/serve.png)
-->

---

## Future improvements

- Cancel or edit a request
- Expiry date for food, so food that expires first is served first
- Export a report to PDF or Excel
- Search and history of served requests
- Online version where NGOs and donors can log in

---

## Team

Add the names of your team members here.

---

## License

Made for educational purposes.
