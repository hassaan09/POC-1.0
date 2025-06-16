# Shiza POC 1.0

## Description

Shiza POC 1.0 is an automation tool designed to perform web-based tasks using natural language commands. This project leverages **Selenium** for browser automation, **Gradio** for building an interactive frontend, and **Speech Recognition** to process voice commands. The system accepts multiple input modalities (text, voice, file), and processes tasks with a series of pre-defined steps.

### PyAutoGUI Role

In addition to Selenium, **PyAutoGUI** plays a crucial role in handling tasks that require GUI automation outside of browser interactions. PyAutoGUI is used to:

- **Simulate Mouse Movements & Clicks**: When elements are not easily accessible through Selenium (e.g., system alerts, pop-ups), PyAutoGUI is used to simulate mouse movements and clicks directly on the screen.
  
- **Keyboard Automation**: PyAutoGUI is responsible for simulating keyboard actions such as typing text, pressing special keys (e.g., Enter, Escape), and more, for tasks like typing in desktop applications or interacting with system pop-ups.

- **Screenshot Capture**: While Selenium handles in-browser screenshot capture, PyAutoGUI extends this by allowing screenshots of the entire screen or specific regions, useful for capturing desktop interactions or system-wide alerts.


---

## Installation

To get started with **Shiza POC 1.0**, follow the steps below:

1. **Install Python 3.11.8**
   
   Make sure Python 3.11.8 is installed on your system.

2. **Install Dependencies**

   Run the following command to install all required dependencies automatically:

   ```bash
   pip install -r requirements.txt

## Run the Main Application
    python main.py

## Flow Diagram
   ![alt text](<Flow Diagram 2.0.PNG>) 

## Natural Language Pseudocode

## **1. AutomationEngine Class**

### **1.1 Initialization (`INIT`)**
- **Process**: Initialize the **UI Tree Manager**, **Logger**, and placeholders for the **browser driver** and **status**.

### **1.2 Setup Browser Driver (`setup_driver`)**
- **Process**: Configure and launch the Chrome browser using **Selenium** in a **headless-safe mode**.

### **1.3 Execute Task (`execute_task`)**
- **Input**: An **execution plan** (a sequence of tasks).
- **Process**:
  - Validate the **execution plan**.
  - Set up the **browser**.
  - For each step in the **execution plan**:
    - Update the task **status**.
    - Execute the corresponding action (e.g., **navigate**, **click**, **type**, **wait**).
  - Keep the **browser** open after completing the task.

### **1.4 Execute Step (`execute_step`)**
- **Input**: A **step**, **dynamic values**, and **task information**.
- **Process**:
  - Resolve the type of action (e.g., **navigate**, **click**, **type**, **wait**).
  - Delegate the task to specific methods (e.g., **navigate_to_url**, **click_element**, etc.).

### **1.5 Navigate to URL (`navigate_to_url`)**
- **Process**: Open the provided **URL** in the browser and wait for it to load completely.

### **1.6 Find Element (`find_element`)**
- **Process**: Use the **UI Tree Manager** to locate the UI element using the specified **selector**.

### **1.7 Click Element (`click_element`)**
- **Process**: Locate and click on the element using **Selenium**.

### **1.8 Type Text (`type_text`)**
- **Process**: Locate the input field, clear its content, type the specified text, and press **ENTER**.

### **1.9 Take Screenshot (`take_screenshot`)**
- **Process**: Save a screenshot to the configured directory for further analysis.

### **1.10 Cleanup (`cleanup`)**
- **Process**: Close the browser and clean up the **browser driver**.

---

## **2. TaskAutomationApp (Gradio Frontend Interface)**

### **2.1 Initialization (`INIT`)**
- **Process**: Set up the **InputHandler** and **TaskProcessor**.
  - Prepare the necessary directories for processing.

### **2.2 Process Input (`process_input`)**
- **Input**: **text_input**, **voice_input**, or **file_input**.
- **Process**:
  - Determine the modality of the input (**text**, **voice**, or **file**).
  - Convert the input into a structured **user command**.
  - Generate an **execution plan** via the **TaskProcessor**.
  - Start a new **automation thread** to run the task.

### **2.3 Start Automation Thread (`start_automation_thread`)**
- **Process**: Execute the **AutomationEngine.execute_task** method in a new thread.

### **2.4 Create Interface (`create_interface`)**
- **Process**: Build the **Gradio UI** to:
  - Accept **text**, **voice**, or **file** input.
  - Display real-time **status** and feedback of the task.
  - Provide **help** and example instructions for users.

### **2.5 Launch Interface (`launch`)**
- **Process**: Launch the **Gradio** app locally at **127.0.0.1:7860**.

---

## **3. InputHandler Class**

### **3.1 Initialization (`INIT`)**
- **Process**: Initialize **Speech Recognition** recognizer and **microphone** for processing voice input.

### **3.2 Process Text Input (`process_text_input`)**
- **Input**: **text** (raw input).
- **Process**:
  - Validate if the input is **empty** or **invalid**.
  - Clean up extra spaces and return the processed **text**.

### **3.3 Process Voice Input (`process_voice_input`)**
- **Input**: **audio_file**.
- **Process**:
  - Save the **audio file** temporarily to disk.
  - Transcribe the speech to **text** using **speech recognition**.
  - Delete the temporary audio file and return the transcribed **text**.

### **3.4 Process File Input (`process_file_input`)**
- **Input**: **file** (text file).
- **Process**:
  - Decode the content of the **file**.
  - Validate if the file is **empty** or **invalid**.
  - Return the cleaned and decoded **file content**.

---

## **4. TaskProcessor Class**

### **4.1 Initialization (`INIT`)**
- **Process**: Initialize the **UITreeManager** for managing UI tasks.

### **4.2 Process User Input (`process_user_input`)**
- **Input**: **user_input** (text from user).
- **Process**:
  - Find the most relevant task template using the **UITreeManager**.
  - If a match is found, retrieve the task's **action steps**.
  - Extract dynamic values (e.g., **email**, **search query**) from the user input.
  - Return the generated **task execution plan**.

### **4.3 Extract Dynamic Values (`extract_dynamic_values`)**
- **Input**: **user_input** and **task_info**.
- **Process**:
  - Depending on the task type (e.g., **email_compose**, **web_search**, **web_navigate**), extract relevant dynamic values using **regular expressions**.
  - Return a dictionary with dynamic values for the task (e.g., **email address**, **search term**, **URL**).

---

## **5. UITreeManager Class**

### **5.1 Initialization (`INIT`)**
- **Process**: Initialize the **TF-IDF Vectorizer** and load **UI mappings** from **Excel files**.

### **5.2 Load UI Mappings (`load_ui_mappings`)**
- **Process**: Load **UI mappings**, **task templates**, and **element selectors** from **Excel files**.
  - Prepare the **TF-IDF matrix** for task matching.

### **5.3 Prepare TF-IDF Matrix (`prepare_tfidf_matrix`)**
- **Process**: Combine task names, **keywords**, and **descriptions**.
  - Transform this text data into **TF-IDF vectors**.

### **5.4 Find Best Matching Task (`find_best_matching_task`)**
- **Input**: **user_input** (raw text).
- **Process**:
  - Transform the **user input** into a **TF-IDF vector**.
  - Calculate the **cosine similarity** between the input and predefined tasks.
  - Find the best matching task based on the similarity score.
  - Return the matching task if the similarity score exceeds a predefined threshold.

### **5.5 Get Task Steps (`get_task_steps`)**
- **Input**: **task_id** (ID of a specific task).
- **Process**:
  - Retrieve the list of action steps for the given task from the **UI mappings**.
  - Return the sorted steps for execution.

### **5.6 Get Element Selector (`get_element_selector`)**
- **Input**: **element_id**.
- **Process**:
  - Retrieve the element's **selector** information (XPath, CSS selector) from the **UI mappings**.
  - Return the selector details.

---