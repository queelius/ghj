---
date: '2023-12-07T20:57:14Z'
description: Scalable lock based on 2-thread Peterson lock.
forks: 0
languages:
- Java
layout: project
links:
- name: GitHub
  url: https://github.com/queelius/tournamentpetersonlock
open_issues: 0
stars: 0
tags:
- GitHub
- project
title: tournamentpetersonlock
---

Scalable lock based on 2-thread Peterson lock.

**Stars**: 0 | **Forks**: 0 | **Open Issues**: 0

**Languages**: Java

## Contributors
- queelius (2 commits)

## README
# Java Package: `tournamentpetersonlock`

## Overview

`tournamentpetersonlock` is an elegant Java implementation of a scalable locking mechanism based on the classic Peterson lock algorithm. This project addresses the challenge of generalizing the two-thread Peterson lock to accommodate `n` threads, with `n` being a power of two, using a binary tree of Peterson locks.

Developed as a response to Exercise 13 in "The Art of Multiprocessor Programming" by Maurice Herlihy and Nir Shavit (2008), it was part of the coursework for CS-590 Multiprocessor Synchronization at SIUE under Dr. Greg Stephen.

## Features
- **Binary Tree Structure**: Utilizes a binary tree of 2-thread Peterson locks.
- **Scalable Synchronization**: Designed to handle a power of two number of threads for efficient multi-thread synchronization.
- **Thread Safety**: Ensures mutual exclusion, deadlock freedom, and starvation freedom in concurrent environments.

## Getting Started

To use `tournamentpetersonlock` in your project, clone this repository and include the Java files in your project's classpath.

### Installation
```bash
git clone https://github.com/queelius/tournamentpetersonlock.git
```

## Building and Testing with Maven

### Prerequisites
- Java Development Kit (JDK) - Version 1.8 or above.
- Maven - If not already installed, you can download it from [Maven's official website](https://maven.apache.org/download.cgi).

### Building the Project
Navigate to the project's root directory and run the following command to compile the project:
```bash
mvn compile
```

### Running Tests
To run the tests, execute:

```bash
mvn test
```

This command will automatically handle downloading the necessary dependencies, compiling the source code, and running the tests.


## Usage

After building the project with Maven, you can use `tournamentpetersonlock` in your Java applications. Here's a minimal working example demonstrating how to use `tournamentpetersonlock`:

```java
import tournamentpetersonlock.TournamentLock;

public class TournamentExample {
    public static void main(String[] args) {
        // Number of threads (must be a power of two)
        int numThreads = 4;

        // Create an instance of the lock
        TournamentLock lock = new TournamentLock(numThreads);

        // Example usage of the lock in a thread
        Runnable task = () -> {
            lock.lock();
            try {
                // Critical section
                System.out.println("Thread " + Thread.currentThread().getId() + " is in the critical section");
            } finally {
                lock.unlock();
            }
        };

        // Starting threads
        for (int i = 0; i < numThreads; i++) {
            new Thread(task).start();
        }
    }
}
```

This example creates an `TournamentLock` lock for a specified number of threads and demonstrates its usage in a multi-threaded context. Each thread acquires the lock before entering the critical section and releases it afterward.

Note: Ensure that the number of threads is a power of two, as required by the `TournamentLock` implementation.

### Running the Example With Maven
- Place the above code in a file named `TournamentExample.java` in the `src/main/java` directory of your project.

- Compile and run the example using Maven:

```bash
  mvn compile
  mvn exec:java -Dexec.mainClass="tournamentpetersonlock.PetersonLockExample"
```

### Running the Example Without Maven

- Place example code into `TournamentExample.java` somewhere.

- This step requires Maven: Make sure you packaged `tournamentpetersonlock` into a JAR:

```bash
mvn package
```

- Place the JAR package into same directory as `TournamentExample.java` and rename it to `tournamentpetersonlock-1.0.jar`.

- Compile and run the example:

```bash
javac -cp .:tournamentpetersonlock-1.0.jar TournamentExample.java
java -cp .:tournamentpetersonlock-1.0.jar TournamentExample
```

## Theoretical Background

The `tournamentpetersonlock` is underpinned by key theoretical principles ensuring robust and reliable synchronization in multi-threaded environments:

- **Mutual Exclusion**: Each node in the binary tree represents a 2-thread Peterson lock. Threads are only promoted to the next layer if they acquire the lock at their current layer, ensuring that at any level, only half of the threads can progress. This process leads to mutual exclusion at the root, extending to the entire tree.

- **Freedom from Deadlock**: Upon release, a thread sets its flag variable to false for each node along its path. This action allows other threads, which were previously unable to progress due to the lock, to move forward, thus preventing deadlock in the system.

- **Freedom from Starvation**: Since each Peterson lock is starvation-free and the earlier arriving thread (which is not the victim) at a node gets promoted, this property is recursively maintained at each tree layer. Consequently, the entire tree structure is free from starvation.

## Contributing
Contributions to `tournamentpetersonlock` are welcome. Please review any contribution guidelines in this repository and ensure to follow standard practices for contributing to open source projects.

## License
This project is licensed under the [MIT License](LICENSE).
