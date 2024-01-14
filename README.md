# Coup Game Setup

This README provides instructions on how to set up and run the `coup` game simulation on your local machine using a virtual environment.

## Getting Started

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/coup.git
    ```

2. Navigate to the project directory:

    ```bash
    cd coup
    ```

3. Create a virtual environment named `venv`:

    ```bash
    python -m venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```bash
        . venv\Scripts\activate
        ```

    - On macOS and Linux:

        ```bash
        source venv/bin/activate
        ```

5. Install project dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the Coup game simulation with the following command:

```bash
python -m coup.console
