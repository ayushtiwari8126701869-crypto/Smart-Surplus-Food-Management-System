// Smart Surplus Food Management System - BACKEND (C)
// DS through C - PBL project
//
// This file has NO printf/scanf menus. The GUI (gui.py) is the frontend.
// It calls these functions, and the data structures live here in C:
//   Linked List    -> food inventory
//   Queue          -> normal requests (first come first served)
//   Priority Queue -> urgent requests (lower priority number = served first)

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#ifdef _WIN32
#define EXPORT __declspec(dllexport)
#else
#define EXPORT
#endif

// ---------- structures ----------

struct Food {
    char name[30];
    int qty;
    struct Food *next;
};

struct Request {
    char person[30];
    char food[30];
    int qty;
    int priority;            // 0 = normal request, 1 = critical, 2 = high, 3 = medium
    struct Request *next;
};

struct Food *head = NULL;            // food linked list
struct Request *front = NULL;        // normal queue front
struct Request *rear = NULL;         // normal queue rear
struct Request *urgentHead = NULL;   // priority queue (sorted linked list)


// ---------- small helper functions ----------

// compare two names ignoring upper/lower case (Rice == rice)
int sameName(const char *a, const char *b) {
    while (*a && *b) {
        if (tolower((unsigned char)*a) != tolower((unsigned char)*b))
            return 0;
        a++;
        b++;
    }
    return *a == *b;
}

// add one line of text at the end of the output buffer (safe, no overflow)
void appendLine(char *out, int size, const char *line) {
    if (strlen(out) + strlen(line) + 1 < (size_t)size)
        strcat(out, line);
}

// make a new request node
struct Request *makeRequest(const char *person, const char *food, int qty, int priority) {
    struct Request *n = (struct Request *)malloc(sizeof(struct Request));
    snprintf(n->person, sizeof(n->person), "%s", person);
    snprintf(n->food, sizeof(n->food), "%s", food);
    n->qty = qty;
    n->priority = priority;
    n->next = NULL;
    return n;
}


// ---------- food inventory (linked list) ----------

// returns: -1 = invalid input, 1 = new food added, 2 = existing food updated
EXPORT int add_food(const char *name, int qty) {
    struct Food *temp, *newnode;

    if (name == NULL || name[0] == '\0' || qty <= 0)
        return -1;

    // food already there -> only increase qty
    temp = head;
    while (temp != NULL) {
        if (sameName(temp->name, name)) {
            temp->qty = temp->qty + qty;
            return 2;
        }
        temp = temp->next;
    }

    // otherwise make a new node at the end
    newnode = (struct Food *)malloc(sizeof(struct Food));
    snprintf(newnode->name, sizeof(newnode->name), "%s", name);
    newnode->qty = qty;
    newnode->next = NULL;

    if (head == NULL) {
        head = newnode;
    } else {
        temp = head;
        while (temp->next != NULL)
            temp = temp->next;
        temp->next = newnode;
    }
    return 1;
}

// writes lines like "Rice|20" into out
EXPORT void get_inventory(char *out, int size) {
    struct Food *temp = head;
    char line[80];

    out[0] = '\0';
    while (temp != NULL) {
        snprintf(line, sizeof(line), "%s|%d\n", temp->name, temp->qty);
        appendLine(out, size, line);
        temp = temp->next;
    }
}


// ---------- normal requests (queue) ----------

// enqueue at rear. returns 1 = ok, -1 = invalid input
EXPORT int add_request(const char *person, const char *food, int qty) {
    struct Request *newnode;

    if (person == NULL || food == NULL || person[0] == '\0' || food[0] == '\0' || qty <= 0)
        return -1;

    newnode = makeRequest(person, food, qty, 0);

    if (rear == NULL) {
        front = newnode;
        rear = newnode;
    } else {
        rear->next = newnode;
        rear = newnode;
    }
    return 1;
}

// writes lines like "Ravi|Rice|5"
EXPORT void get_requests(char *out, int size) {
    struct Request *temp = front;
    char line[120];

    out[0] = '\0';
    while (temp != NULL) {
        snprintf(line, sizeof(line), "%s|%s|%d\n", temp->person, temp->food, temp->qty);
        appendLine(out, size, line);
        temp = temp->next;
    }
}


// ---------- urgent requests (priority queue) ----------

// priority: 1 = critical, 2 = high, 3 = medium (smaller number is served first)
// same priority -> first come first served
// returns 1 = ok, -1 = invalid input
EXPORT int add_urgent_request(const char *person, const char *food, int qty, int priority) {
    struct Request *newnode, *temp;

    if (person == NULL || food == NULL || person[0] == '\0' || food[0] == '\0' || qty <= 0)
        return -1;
    if (priority < 1 || priority > 3)
        return -1;

    newnode = makeRequest(person, food, qty, priority);

    // goes at the front if list is empty or it is more urgent than the first one
    if (urgentHead == NULL || priority < urgentHead->priority) {
        newnode->next = urgentHead;
        urgentHead = newnode;
        return 1;
    }

    // otherwise find the place: after all nodes with same or higher urgency
    temp = urgentHead;
    while (temp->next != NULL && temp->next->priority <= priority)
        temp = temp->next;

    newnode->next = temp->next;
    temp->next = newnode;
    return 1;
}

// writes lines like "Asha|Rice|10|1"
EXPORT void get_urgent_requests(char *out, int size) {
    struct Request *temp = urgentHead;
    char line[120];

    out[0] = '\0';
    while (temp != NULL) {
        snprintf(line, sizeof(line), "%s|%s|%d|%d\n", temp->person, temp->food, temp->qty, temp->priority);
        appendLine(out, size, line);
        temp = temp->next;
    }
}


// ---------- distribute food ----------

// Serves ONE request. Urgent requests are always served before normal ones.
// returns 1 = a request was processed, 0 = no pending requests
// the result text is written into msg
EXPORT int process_next(char *msg, int size) {
    struct Request *r;
    struct Food *t, *prev;
    int give;
    char tag[10];

    msg[0] = '\0';

    // pick the request: urgent first, then normal
    if (urgentHead != NULL) {
        r = urgentHead;
        urgentHead = urgentHead->next;
        strcpy(tag, "URGENT");
    } else if (front != NULL) {
        r = front;
        front = front->next;
        if (front == NULL)
            rear = NULL;       // queue became empty
        strcpy(tag, "NORMAL");
    } else {
        snprintf(msg, size, "No pending requests");
        return 0;
    }

    // search the food in inventory
    prev = NULL;
    t = head;
    while (t != NULL && !sameName(t->name, r->food)) {
        prev = t;
        t = t->next;
    }

    if (t == NULL) {
        snprintf(msg, size, "[%s] %s asked for %s - not available, request closed",
                 tag, r->person, r->food);
    } else {
        give = (t->qty >= r->qty) ? r->qty : t->qty;
        t->qty = t->qty - give;

        if (give == r->qty)
            snprintf(msg, size, "[%s] %s got %d plates of %s",
                     tag, r->person, give, t->name);
        else
            snprintf(msg, size, "[%s] %s wanted %d plates of %s but only %d were left",
                     tag, r->person, r->qty, t->name, give);

        // remove the food node if the stock finished
        if (t->qty == 0) {
            if (prev == NULL)
                head = t->next;
            else
                prev->next = t->next;
            free(t);
        }
    }

    free(r);
    return 1;
}


// ---------- cleanup ----------

// free all memory (optional, can be called when the GUI closes)
EXPORT void clear_all(void) {
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
