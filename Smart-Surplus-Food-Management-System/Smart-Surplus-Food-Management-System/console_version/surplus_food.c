// Smart Surplus Food Management System (Console Version)
// DS through C - PBL project
//
// Data structures used:
//   Linked List    -> food inventory
//   Queue          -> normal requests (first come first served)
//   Priority Queue -> urgent requests (most urgent first)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// node for food linked list
struct Food {
    char name[30];
    int qty;
    struct Food *next;
};

// node for request queue and priority queue
struct Request {
    char person[30];
    char food[30];
    int qty;
    int priority;            // 0 = normal, 1 = critical, 2 = high, 3 = medium
    struct Request *next;
};

struct Food *head = NULL;          // first food in list
struct Request *front = NULL;      // first request in normal queue
struct Request *rear = NULL;       // last request in normal queue
struct Request *urgentHead = NULL; // first request in priority queue


// ---------- small helper functions ----------

// compare two names ignoring upper/lower case (Rice == rice)
int sameName(char a[], char b[]) {
    int i = 0;
    while (a[i] != '\0' && b[i] != '\0') {
        if (tolower((unsigned char)a[i]) != tolower((unsigned char)b[i]))
            return 0;
        i++;
    }
    return a[i] == b[i];
}

// remove wrong input that is still waiting in the keyboard buffer
void clearInput() {
    int c;
    while ((c = getchar()) != '\n' && c != EOF) {
    }
}

// give the urgency number a name
char *priorityName(int p) {
    if (p == 1) return "Critical";
    if (p == 2) return "High";
    return "Medium";
}


// ---------- food inventory (linked list) ----------

// add food to the inventory
void addFood() {
    char name[30];
    int qty;
    struct Food *temp, *newnode;

    printf("Food name: ");
    scanf("%29s", name);
    printf("Quantity (plates): ");
    if (scanf("%d", &qty) != 1) {
        clearInput();
        printf("Please enter a number\n");
        return;
    }

    if (qty <= 0) {
        printf("Quantity should be more than 0\n");
        return;
    }

    // if food is already there then only increase the qty
    temp = head;
    while (temp != NULL) {
        if (sameName(temp->name, name)) {
            temp->qty = temp->qty + qty;
            printf("%s updated, now %d plates\n", temp->name, temp->qty);
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


// ---------- normal requests (queue) ----------

// add a request at the end of the queue (enqueue)
void addRequest() {
    char person[30], food[30];
    int qty;
    struct Request *newnode;

    printf("Your name: ");
    scanf("%29s", person);
    printf("Food you want: ");
    scanf("%29s", food);
    printf("How many plates: ");
    if (scanf("%d", &qty) != 1) {
        clearInput();
        printf("Please enter a number\n");
        return;
    }
    if (qty <= 0) {
        printf("Plates should be more than 0\n");
        return;
    }

    newnode = (struct Request *)malloc(sizeof(struct Request));
    strcpy(newnode->person, person);
    strcpy(newnode->food, food);
    newnode->qty = qty;
    newnode->priority = 0;
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

// show all pending normal requests
void showRequests() {
    struct Request *temp = front;
    int i = 1;

    if (temp == NULL) {
        printf("No pending normal requests\n");
        return;
    }

    printf("\nPending normal requests (first come first served):\n");
    while (temp != NULL) {
        printf("%d. %s wants %d plates of %s\n", i, temp->person, temp->qty, temp->food);
        temp = temp->next;
        i++;
    }
}


// ---------- urgent requests (priority queue) ----------

// add an urgent request. 1 = critical, 2 = high, 3 = medium
// smaller number is served first, same number -> first come first served
void addUrgentRequest() {
    char person[30], food[30];
    int qty, priority;
    struct Request *newnode, *temp;

    printf("Your name: ");
    scanf("%29s", person);
    printf("Food you want: ");
    scanf("%29s", food);
    printf("How many plates: ");
    if (scanf("%d", &qty) != 1) {
        clearInput();
        printf("Please enter a number\n");
        return;
    }
    if (qty <= 0) {
        printf("Plates should be more than 0\n");
        return;
    }
    printf("Urgency (1 = Critical, 2 = High, 3 = Medium): ");
    if (scanf("%d", &priority) != 1) {
        clearInput();
        printf("Please enter a number\n");
        return;
    }
    if (priority < 1 || priority > 3) {
        printf("Urgency should be 1, 2 or 3\n");
        return;
    }

    newnode = (struct Request *)malloc(sizeof(struct Request));
    strcpy(newnode->person, person);
    strcpy(newnode->food, food);
    newnode->qty = qty;
    newnode->priority = priority;
    newnode->next = NULL;

    // goes at the front if list is empty or it is more urgent than the first one
    if (urgentHead == NULL || priority < urgentHead->priority) {
        newnode->next = urgentHead;
        urgentHead = newnode;
    } else {
        // find the place: after all nodes with same or higher urgency
        temp = urgentHead;
        while (temp->next != NULL && temp->next->priority <= priority) {
            temp = temp->next;
        }
        newnode->next = temp->next;
        temp->next = newnode;
    }
    printf("Urgent request added (%s)\n", priorityName(priority));
}

// show all pending urgent requests
void showUrgentRequests() {
    struct Request *temp = urgentHead;
    int i = 1;

    if (temp == NULL) {
        printf("No pending urgent requests\n");
        return;
    }

    printf("\nPending urgent requests (most urgent first):\n");
    while (temp != NULL) {
        printf("%d. [%s] %s wants %d plates of %s\n", i, priorityName(temp->priority),
               temp->person, temp->qty, temp->food);
        temp = temp->next;
        i++;
    }
}


// ---------- distribute food ----------

// serve ONE request. urgent requests are always served before normal ones
void processRequest() {
    struct Request *r;
    struct Food *t, *prev;
    int give;
    char tag[10];

    // pick the request: urgent first, then normal
    if (urgentHead != NULL) {
        r = urgentHead;
        urgentHead = urgentHead->next;
        strcpy(tag, "URGENT");
    } else if (front != NULL) {
        r = front;
        front = front->next;
        if (front == NULL) {
            rear = NULL;       // queue became empty
        }
        strcpy(tag, "NORMAL");
    } else {
        printf("No pending requests\n");
        return;
    }

    // search the food in inventory
    prev = NULL;
    t = head;
    while (t != NULL && !sameName(t->name, r->food)) {
        prev = t;
        t = t->next;
    }

    if (t == NULL) {
        printf("[%s] %s asked for %s - not available, request closed\n", tag, r->person, r->food);
    } else {
        // give the full amount, or whatever is left
        if (t->qty >= r->qty) {
            give = r->qty;
        } else {
            give = t->qty;
        }
        t->qty = t->qty - give;

        if (give == r->qty) {
            printf("[%s] %s got %d plates of %s\n", tag, r->person, give, t->name);
        } else {
            printf("[%s] %s wanted %d plates of %s but only %d were left\n",
                   tag, r->person, r->qty, t->name, give);
        }

        // remove the food node if the stock finished
        if (t->qty == 0) {
            if (prev == NULL) {
                head = t->next;
            } else {
                prev->next = t->next;
            }
            free(t);
        }
    }

    free(r);
}


// ---------- free all memory before exit ----------

void freeAll() {
    struct Food *f;
    struct Request *r;

    while (head != NULL) {
        f = head;
        head = head->next;
        free(f);
    }
    while (front != NULL) {
        r = front;
        front = front->next;
        free(r);
    }
    rear = NULL;
    while (urgentHead != NULL) {
        r = urgentHead;
        urgentHead = urgentHead->next;
        free(r);
    }
}


int main() {
    int choice;

    do {
        printf("\n--- Smart Surplus Food Management ---\n");
        printf("1. Add food\n");
        printf("2. Show inventory\n");
        printf("3. Add normal request\n");
        printf("4. Show pending normal requests\n");
        printf("5. Add urgent request\n");
        printf("6. Show pending urgent requests\n");
        printf("7. Serve next request\n");
        printf("0. Exit\n");
        printf("Enter choice: ");
        if (scanf("%d", &choice) != 1) {
            clearInput();
            choice = -1;
        }

        switch (choice) {
            case 1: addFood(); break;
            case 2: showInventory(); break;
            case 3: addRequest(); break;
            case 4: showRequests(); break;
            case 5: addUrgentRequest(); break;
            case 6: showUrgentRequests(); break;
            case 7: processRequest(); break;
            case 0: freeAll(); printf("Bye\n"); break;
            default: printf("Wrong choice, try again\n");
        }
    } while (choice != 0);

    return 0;
}
