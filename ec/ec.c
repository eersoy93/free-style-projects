#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_LINE 1024

// Simple variable table
typedef struct
{
    char name[32];
    int value;
} Variable;

Variable vars[100];
int var_count = 0;

// Find variable index, or -1 if not found
int find_var(const char * name)
{
    for (int i = 0; i < var_count; ++i)
    {
        if (strcmp(vars[i].name, name) == 0)
        {
            return i;
        }
    }

    return -1;
}

// Set variable value
void set_var(const char * name, int value)
{
    int idx = find_var(name);
    if (idx == -1)
    {
        strcpy_s(vars[var_count].name, sizeof(vars[var_count].name), name);
        vars[var_count].value = value;
        var_count++;
    }
    else
    {
        vars[idx].value = value;
    }
}

// Get variable value
int get_var(const char * name)
{
    int idx = find_var(name);
    if (idx == -1)
    {
        printf("Undefined variable: %s\n", name);
        exit(EXIT_FAILURE);
    }

    return vars[idx].value;
}

// Evaluate simple expressions: number or variable
int eval_expr(const char * expr)
{
    char var[32];
    int val;

    if (sscanf_s(expr, "%d", &val) == 1)
    {
        return val;
    }
    else if (sscanf_s(expr, "%31s", var, (unsigned)sizeof(var)) == 1)
    {
        return get_var(var);
    }
    else
    {
        printf("Invalid expression: %s\n", expr);
        exit(EXIT_FAILURE);
    }
}

// Parse and execute a line
void exec_line(char * line)
{
    char cmd[16] = { 0 };
    char arg1[32] = { 0 };
    char arg2[32] = { 0 };
    if (sscanf_s(line, "%15s %31s = %31s", cmd, (unsigned)sizeof(cmd), arg1, (unsigned)sizeof(arg1), arg2, (unsigned)sizeof(arg2)) == 3 && strcmp(cmd, "let") == 0)
    {
        int val = eval_expr(arg2);
        set_var(arg1, val);
    }
    else if (sscanf_s(line, "%15s %31s", cmd, (unsigned)sizeof(cmd), arg1, (unsigned)sizeof(arg1)) == 2 && strcmp(cmd, "print") == 0)
    {
        int val = eval_expr(arg1);
        printf("%d\n", val);
    }
    else if (sscanf_s(line, "%15s", cmd, (unsigned)sizeof(cmd)) == 1 && strcmp(cmd, "exit") == 0)
    {
        printf("Exiting EC...\n");
        exit(EXIT_SUCCESS);
    }
    else if (sscanf_s(line, "%15s", cmd, (unsigned)sizeof(cmd)) == 1 && strcmp(cmd, "help") == 0)
    {
        printf("Available commands:\n");
        printf("let <var> = <expr>   Set variable\n");
        printf("print <var>          Print variable\n");
        printf("exit                 Exit the interpreter\n");
        printf("help                 Show this help message\n");
        printf("vars                 List all variables\n");
        printf("clearvars            Clear all variables\n");
        printf("clear                Clear the screen\n");
        printf("NOTE: Variables are case-sensitive!\n");
    }
    else if (sscanf_s(line, "%15s", cmd, (unsigned)sizeof(cmd)) == 1 && strcmp(cmd, "vars") == 0)
    {
        printf("Variables:\n");
        for (int i = 0; i < var_count; ++i)
        {
            printf("%s = %d\n", vars[i].name, vars[i].value);
        }
    }
    else if (sscanf_s(line, "%15s", cmd, (unsigned)sizeof(cmd)) == 1 && strcmp(cmd, "clearvars") == 0)
    {
        var_count = 0;
        printf("All variables cleared!\n");
    }
    else if (sscanf_s(line, "%15s", cmd, (unsigned)sizeof(cmd)) == 1 && strcmp(cmd, "clear") == 0)
    {
        system("cls");
    }
    else if (strlen(line) == 0 || line[0] == '#')
    {
        // Ignore empty lines and comments
        return;
    }
    else
    {
        printf("Unknown command: %s\n", line);
    }
}

int main()
{
    char line[MAX_LINE];
    printf("Welcome to EC!\n");
    printf("Simple C dialect interpreter. Type 'exit' to quit.\n");
    while (1)
    {
        printf("EC> ");
        if (!fgets(line, sizeof(line), stdin))
        {
            break;
        }

        // Remove trailing newline
        line[strcspn(line, "\n")] = 0;

        exec_line(line);
    }

    return EXIT_SUCCESS;
}
