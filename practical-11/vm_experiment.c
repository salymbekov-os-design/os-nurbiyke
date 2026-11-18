
#define _DEFAULT_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/resource.h>
#include <time.h>
#include <stdint.h>

#define MAX_DIMENSION 4096

typedef struct {
    long minor;
    long major;
} FaultStats;


double get_time()
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);

    return ts.tv_sec + ts.tv_nsec / 1000000000.0;
}


FaultStats get_faults()
{
    struct rusage usage;
    FaultStats result = {0, 0};

    if (getrusage(RUSAGE_SELF, &usage) == 0) {
        result.minor = usage.ru_minflt;
        result.major = usage.ru_majflt;
    }

    return result;
}


void print_proc_stat()
{
    FILE *file = fopen("/proc/self/stat", "r");

    if (!file) {
        perror("/proc/self/stat");
        return;
    }

    char buffer[4096];

    if (!fgets(buffer, sizeof(buffer), file)) {
        fclose(file);
        return;
    }

    fclose(file);

    char *right = strrchr(buffer, ')');

    if (!right) {
        printf("Cannot parse /proc/self/stat\n");
        return;
    }

    char *saveptr;
    char *token = strtok_r(right + 2, " ", &saveptr);

    int field = 3;
    long minflt = 0;
    long majflt = 0;

    while (token != NULL) {
        if (field == 10)
            minflt = atol(token);

        if (field == 12) {
            majflt = atol(token);
            break;
        }

        field++;
        token = strtok_r(NULL, " ", &saveptr);
    }

    printf("\n/proc/self/stat:\n");
    printf("Minor faults: %ld\n", minflt);
    printf("Major faults: %ld\n", majflt);
}


void print_results(
    const char *name,
    FaultStats before,
    FaultStats after,
    double elapsed
)
{
    printf("\n%s\n", name);

    printf("Minor faults: %ld\n",
        after.minor - before.minor);

    printf("Major faults: %ld\n",
        after.major - before.major);

    printf("Time: %.6f seconds\n", elapsed);
}


int run_matrix(const char *mode, size_t rows, size_t cols)
{
    if (rows == 0 || cols == 0 ||
        rows > MAX_DIMENSION ||
        cols > MAX_DIMENSION ||
        rows > SIZE_MAX / cols ||
        rows * cols > SIZE_MAX / sizeof(int)) {

        printf("Invalid matrix dimensions.\n");
        return 1;
    }

    size_t elements = rows * cols;
    size_t bytes = elements * sizeof(int);

    printf("MATRIX EXPERIMENT\n");
    printf("Mode: %s\n", mode);
    printf("Rows: %zu\n", rows);
    printf("Columns: %zu\n", cols);
    printf("Memory: %.2f MB\n",
        bytes / (1024.0 * 1024.0));

    int *matrix = calloc(elements, sizeof(int));

    if (!matrix) {
        perror("Memory allocation failed");
        return 1;
    }

    FaultStats before = get_faults();
    double start = get_time();

    volatile long long sum = 0;

    if (strcmp(mode, "rows") == 0) {

        for (size_t i = 0; i < rows; i++) {
            for (size_t j = 0; j < cols; j++) {
                size_t index = i * cols + j;

                matrix[index] = (int)(i + j);
                sum += matrix[index];
            }
        }

    } else if (strcmp(mode, "cols") == 0) {

        for (size_t j = 0; j < cols; j++) {
            for (size_t i = 0; i < rows; i++) {
                size_t index = i * cols + j;

                matrix[index] = (int)(i + j);
                sum += matrix[index];
            }
        }

    } else {
        printf("Unknown mode. Use rows or cols.\n");
        free(matrix);
        return 1;
    }

    double end = get_time();
    FaultStats after = get_faults();

    print_results(
        strcmp(mode, "rows") == 0
            ? "ROW-WISE ACCESS"
            : "COLUMN-WISE ACCESS",
        before,
        after,
        end - start
    );

    printf("Checksum: %lld\n", sum);

    free(matrix);

    return 0;
}


int main(int argc, char *argv[])
{
    if (argc != 4) {
        printf("Usage:\n");
        printf("./vm_experiment rows ROWS COLS\n");
        printf("./vm_experiment cols ROWS COLS\n");
        return 1;
    }

    size_t rows = strtoul(argv[2], NULL, 10);
    size_t cols = strtoul(argv[3], NULL, 10);

    if (strcmp(argv[1], "rows") != 0 &&
        strcmp(argv[1], "cols") != 0) {

        printf("Mode must be rows or cols.\n");
        return 1;
    }

    int result = run_matrix(argv[1], rows, cols);

    printf("\nPROCESS STATISTICS\n");
    print_proc_stat();

    printf("\nExperiment finished.\n");

    return result;
}
