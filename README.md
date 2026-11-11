# Smart Surplus Food Management System
 
A desktop application that tracks **surplus food** and distributes it to the people who need it in a fair and organised way, serving urgent cases first.
 
> Data Structures through C: PBL (Project Based Learning) project
 
---
 
## Table of Contents
 
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Project Evolution](#project-evolution)
- [Data Structures Used](#data-structures-used)
- [How Serving Works](#how-serving-works)
- [Project Structure](#project-structure)
- [How to Run](#how-to-run)
- [Other Versions](#other-versions)
- [Known Limitations](#known-limitations)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [Team](#team)
- [License](#license)
---
 
## Problem Statement
 
Extra food from hostels, canteens, weddings and events is often thrown away, while many people nearby go hungry. In a typical canteen, leftover food is noted in a notebook or passed on by word of mouth, so nobody has a clear picture of what is available or who should receive it.
 
This project keeps a record of the available food and of the people requesting it, and hands food out in a proper order. **Urgent cases (for example, a hospital) are served before normal ones.**
 
---
 
## Features
 
- **Dashboard** with live numbers: food types, total plates, normal requests, urgent requests
- **Food Inventory:** add, search and delete food
- **Requests:** normal requests and urgent requests (Critical / High / Medium)
- **Serve Food:** serve one request or all pending requests with one click
- **Activity log** with colour coding (green = served, orange = partly served, red = food not available)
- **Auto-save:** data is stored in `data.json` and restored when the app is reopened
- **Load Sample Data** button for a quick demo
- **Input validation** (empty fields, invalid numbers) with clear messages
---
 
## Project Evolution
 
This project was built in two stages, and both versions are kept in the repository on purpose.
 
**Stage 1: Console version (C).** I started with a text-menu program in pure C to learn and implement the core data structures from scratch: a linked list for the food inventory, a queue for normal requests, and structures and pointers to build the nodes. Working in the terminal let me focus only on getting the logic right, without any interface code getting in the way.
 
**Stage 2: GUI version (Python).** Once the core ideas worked, I rebuilt the project as a desktop app so that real users, such as canteen staff or volunteers, could use it without typing menu numbers. The GUI added the dashboard, a priority queue for urgent requests, one-click serving, an activity log and auto-save.
 
The console version shows the foundation and the GUI version shows the finished product, so together they show how the project grew from a concept into a usable tool.
 
---
 
## Data Structures Used
 
| Data structure | Where it is used | Why |
|---|---|---|
| **Linked List** | Food inventory | Food can be added and removed easily, with no fixed size |
| **Queue** (FIFO) | Normal requests | First come, first served |
| **Priority Queue** | Urgent requests | The most urgent request is served first |
 
All three are implemented **by hand**, without built-in list shortcuts, in the first part of `app.py`, with explanatory comments. The C versions use structures and pointers to build the nodes.
 
---
 
## How Serving Works
 
1. If any **urgent** request exists, the most urgent one is served first. Requests with the same urgency are served in order of arrival.
2. If there are no urgent requests, the first **normal** request is served.
3. If enough plates are available, the person receives the full quantity requested.
4. If fewer plates are available, the person receives whatever is left.
5. If the requested food is not available at all, the request is closed.
6. A food item is removed from the inventory when its plates reach 0.
---
 
## Project Structure
 
```
Smart-Surplus-Food-Management-System/
├── app.py                  <- Main app (GUI). Run this file.
├── console_version/
│   └── surplus_food.c      <- Text-menu version in pure C
├── advanced_c_backend/
│   ├── backend.c           <- Data structures in C
│   ├── gui.py              <- GUI that calls the C code
│   └── build.bat           <- Compiles and runs (Windows)
├── .gitignore
└── README.md
```
 
---
 
## How to Run
 
### Main app (Windows)
 
Only **Python** is required. Tkinter comes with Python, so nothing else needs to be installed.
 
1. Install Python from [python.org](https://www.python.org/downloads/) and tick **"Add Python to PATH"** during installation.
2. Download or clone this repository.
3. Open the project folder in VS Code or Command Prompt.
4. Run:
```
python app.py
```
 
If `python` does not work, try `py app.py`.
 
### Using the app
 
1. Click **Load Sample Data** in the left menu to see the app with example data.
2. **Food Inventory:** enter a food name and number of plates, then click **Add Food**.
3. **Requests:** enter a name, food and plates, choose *Normal* or *Urgent*, then click **Submit Request**.
4. **Serve Food:** click **Serve Next Request** or **Serve All Requests**.
5. Watch the **Dashboard** numbers change and read the activity log.
---
 
## Other Versions
 
### Console version (pure C)
 
Requires a C compiler such as `gcc`.
 
```
cd console_version
gcc surplus_food.c -o surplus_food
./surplus_food
```
 
On Windows, run `surplus_food.exe` instead of `./surplus_food`.
 
**Current status of the console version:**
 
- Working: add food to the inventory (if the food already exists, the plates are added to it), show the inventory, add a normal request, show pending requests
- Urgent requests (priority queue) and serving a request are available in the main GUI app
### GUI with C backend
 
The data structures are written in C (`backend.c`) and the window is built in Python. On Windows with `gcc` installed, double-click `advanced_c_backend/build.bat`, or run:
 
```
cd advanced_c_backend
gcc -shared -o backend.dll backend.c
python gui.py
```
 
---
 
## Known Limitations
 
- **Console version:** food names must be a single word (for example, `Rice` or `Dal`) because input is read with `scanf`
- **Console version:** no data is saved, so everything is lost when the program closes (the main GUI app saves to `data.json`)
- Quantity is measured in **plates**
- Food expiry is not handled yet
---
 
## Screenshots

 <img width="1312" height="881" alt="image" src="https://github.com/user-attachments/assets/a63ac9ce-3415-427c-9fa8-b0eadafbe3e8" />
 <img width="1301" height="885" alt="image" src="https://github.com/user-attachments/assets/068fc598-5860-4bd2-be27-b466503a1849" />
 <img width="1312" height="885" alt="image" src="https://github.com/user-attachments/assets/ad9426e9-6b67-4011-a041-a6a5489cd337" />
 <img width="1306" height="882" alt="image" src="https://github.com/user-attachments/assets/89da37af-a5ca-4514-96c4-a039d5159a02" />

---
 
## Future Improvements
 
- Cancel or edit a request
- Expiry date for food, so food that expires first is served first
- Export a report to PDF or Excel
- Search and history of served requests
- Online version where NGOs and donors can log in
---
 
## Team
 
- Ayush Tiwari (Team Lead)
- Anshul Bisht
- Shivam Rana
- Akshat Seth
---
 
## License
 
Made for educational purposes.
