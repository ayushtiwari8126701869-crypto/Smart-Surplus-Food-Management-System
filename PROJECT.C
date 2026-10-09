// Smart Surplus Food Management System
// DS through C - PBL project
// done: linked list for food, queue for normal requests
// todo: priority queue, distribute food

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// node for food linked list
struct Food {
    char name[30];
    int qty;
    struct Food *next;
};

// node for request queue
struct Request {
    char person[30];
    char food[30];
    int qty;
    struct Request *next;
};

struct Food *head = NULL;      // first food in list
struct Request *front = NULL;  // first request in queue
struct Request *rear = NULL;   // last request in queue


// add food to the inventory
void addFood() {
    char name[30];
    int qty;
    struct Food *temp, *newnode;

    printf("Food name: ");
    scanf("%s", name);
    printf("Quantity (plates): ");
    scanf("%d", &qty);

    if (qty <= 0) {
        printf("Quantity should be more than 0\n");
        return;
    }

    // if food is already there then only increase the qty
    temp = head;
    while (temp != NULL) {
        if (strcmp(temp->name, name) == 0) {
            temp->qty = temp->qty + qty;
            printf("%s updated, now %d plates\n", name, temp->qty);
            return;
        }
        temp = temp->next;
    }

    // otherwise make a new node
    newnode = (struct Food *)malloc(sizeof(struct Food));
    strcpy(newnode->name, name);
    newnode->qty = qty;
    newnode->next = NULL;

    if (head == NULL) {
        head = newnode;        // list was empty
    } else {
        temp = head;
        while (temp->next != NULL) {
            temp = temp->next; // go to last node
        }
        temp->next = newnode;
    }
    printf("%s added\n", name);
}

// show all food in the inventory
void showInventory() {
    struct Food *temp = head;

    if (temp == NULL) {
        printf("Inventory is empty\n");
        return;
    }

    printf("\nInventory:\n");
    while (temp != NULL) {
        printf("%s - %d plates\n", temp->name, temp->qty);
        temp = temp->next;
    }
}

// add a request at the end of the queue (enqueue)
void addRequest() {
    struct Request *newnode;
    newnode = (struct Request *)malloc(sizeof(struct Request));

    printf("Your name: ");
    scanf("%s", newnode->person);
    printf("Food you want: ");
    scanf("%s", newnode->food);
    printf("How many plates: ");
    scanf("%d", &newnode->qty);
    newnode->next = NULL;

    if (rear == NULL) {
        front = newnode;       // queue was empty
        rear = newnode;
    } else {
        rear->next = newnode;
        rear = newnode;
    }
    printf("Request added to queue\n");
}

// show all pending requests
void showRequests() {
    struct Request *temp = front;
    int i = 1;

    if (temp == NULL) {
        printf("No pending requests\n");
        return;
    }

    printf("\nPending requests (first come first served):\n");
    while (temp != NULL) {
        printf("%d. %s wants %d plates of %s\n", i, temp->person, temp->qty, temp->food);
        temp = temp->next;
        i++;
    }
}

int main() {
    int choice;

    do {
        printf("\n--- Smart Surplus Food Management ---\n");
        printf("1. Add food\n");
        printf("2. Show inventory\n");
        printf("3. Add normal request\n");
        printf("4. Show pending requests\n");
        printf("5. Add urgent request (not done yet)\n");
        printf("6. Process requests (not done yet)\n");
        printf("0. Exit\n");
        printf("Enter choice: ");
        scanf("%d", &choice);

        switch (choice) {
            case 1: addFood(); break;
            case 2: showInventory(); break;
            case 3: addRequest(); break;
            case 4: showRequests(); break;
            case 5: printf("Coming soon\n"); break;
            case 6: printf("Coming soon\n"); break;
            case 0: printf("Bye\n"); break;
            default: printf("Wrong choice, try again\n");
        }
    } while (choice != 0);

    return 0;
}
