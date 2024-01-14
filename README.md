# Coup Game Setup

This README provides instructions on how to set up and run the `coup` game simulation on your local machine using a virtual environment.


## Getting Started

1. **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Coup.git
    ```

2. **Navigate to the parent project directory:**

    ```bash
    cd Coup
    ```

3. **Create a virtual environment named `venv`:**

    ```bash
    python -m venv venv
    ```

4. **Activate the virtual environment:**

    - On Windows:

        ```bash
        . venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

5. **Install project dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

This is a console-based approach to the Coup game simulation. Run the game with the following command:

```bash
python -m coup.console
```

- Please make sure you are in the Coup project directory before running the command.

- To add more AI players, go into console.py and add more AI players in the setup_game() function.

- For playing the game, simply type an action from the given action options when prompted in the command line.

Link to Coup rules:
https://www.ultraboardgames.com/coup/game-rules.php


