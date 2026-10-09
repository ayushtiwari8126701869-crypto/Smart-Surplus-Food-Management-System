# Smart Surplus Food Management System

This is our project for Data Structures through C (PBL).

## What is the problem?
In our college canteen a lot of food is cooked and some of it is left over and thrown away. The leftover food is mostly noted in a notebook or just told by mouth, so nobody really knows what is left or who should get it. We are making a small C program to keep track of this food and give it out in a proper order.

## Data structures we used
- Linked list: to store the food items and how many plates are left
- Queue: to store normal requests, first come first served
- Priority queue: for urgent requests (we have not made this yet)
- Structures and pointers: to make the nodes

## What is working right now
- Add food to the inventory (if the food is already there, the plates get added to it)
- Show the inventory
- Add a normal request
- Show pending requests

## What is left
- Priority queue for urgent requests
- Process a request and give the food (reduce the stock)
- Testing
- Flowchart and documentation

## How to run
You need gcc installed.

    gcc surplus_food.c -o surplus_food
    ./surplus_food

(on Windows run surplus_food.exe)

## Things to know
- Food name should be one word, like Rice or Dal, because we used scanf
- Quantity is in plates
- No database, everything is lost when the program closes
- Expiry of food is not handled

## Team
- Ayush Tiwari (team lead)
- Anshul Bisht
- Shivam Rana
- Akshat Seth
