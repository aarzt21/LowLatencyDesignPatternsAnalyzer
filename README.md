# Low Latency Design Patterns Analyzer

## Prerequisite
For learning about the low-latency design patterns and
seeing a detailed demonstration of the application, please
read my thesis beforehand: https://github.com/aarzt21/ImperialThesis

## Installation

Follow these steps to install and use the Low Latency Design Patterns Analyzer (LLDPA):

1. Download or clone this repository to your local machine.

2. Build a Docker image named "lldpa" by navigating to the downloaded repository folder and using the provided Dockerfile. If you have Docker installed, execute the following command: `docker build -t lldpa .`


3. For UNIX-like operating systems, you can run the application in a Docker container based on the "lldpa" image. Simply execute the provided `run.sh` script in your terminal using: `bash run.sh`


*(Note: If you're using Windows, you'll need to adjust the `run.sh` script to account for the lack of an X server to forward the application's GUI.)*

## Running the Application

### Code Analysis

To perform code analysis using LLDPA for your C++ implementation files, ensure your project follows these assumptions:

- The mock program (a realistic simulation of your application's main program - written by you) and other source code files must reside in the same directory.

- Class definitions are divided into header and implementation files. Header files should also be located in the same directory as other files.

- Implementation files for the classes should be concise enough to be submitted to Chat-GPT with a single prompt.

- Getter and setter method names should follow the pattern `get_` or `set_`, followed by the attribute name in lowercase letters.

Once these requirements are met, follow these steps:

1. Use the "Analysis" tab in the GUI to navigate to your project directory.

2. Select the mock program and the relevant C++ implementation files.

3. Choose the specific opportunities you want to scan for.

4. Click the "Analyze" button to initiate the analysis process.

Upon completion, the analysis results will be stored in a new folder named "HTML_OUT" within your project directory.

### Autonomous Refactoring

After analyzing your project for design pattern implementation opportunities, you can proceed with autonomous refactoring:

1. Switch to the refactoring tab in the GUI.

2. Convert all `.cpp.html` files to regular `.cpp` files using the provided button.

3. Input your OpenAI API key and select the desired model for refactoring.

4. Choose the `.cpp` files you want to refactor.

5. Click on "AI Refactoring" to send the files to Chat-GPT, which will implement the relevant low-latency design patterns.

If the received results are not satisfactory, you have the option to:

1. Select the refactored files.

2. Enter a custom prompt in the provided text field.

3. Refactor the files again by clicking "Re-RF using Custom Prompt."

By following these steps, you can effectively analyze and refactor your C++ codebase using the LLDPA.

