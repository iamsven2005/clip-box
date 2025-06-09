# Clip Box

Clip Box is a simple web application that allows users to copy text content from one PC to another using a Flask backend and SQLite database. The application generates a random code for each submission, which can be used to retrieve the content within a limited time frame.

## Features

- Submit text content (up to 1024 bytes).
- Generate a unique random code for each submission.
- Store submission history with timestamps and user information.
- Retrieve content using the generated random code.
- Content is available for 5 minutes only.

## Project Structure

```
clip_box
├── app.py               # Main application file
├── conf.ini             # Configuration settings
├── requirements.txt     # Project dependencies
├── README.md            # Project documentation
├── database
│   └── clipbox.db       # SQLite database file
├── static
│   └── style.css        # CSS styles for the application
├── templates
│   ├── index.html       # Main HTML template for submission
│   └── history.html     # HTML template for displaying submission history
└── utils
    └── __init__.py      # Initialization file for utility functions
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/sg_it/clip_box.git
   cd clip_box
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the application by editing the `conf.ini` file as needed.

## Usage

1. Run the application:
   ```
   python app.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`.

3. Enter the text content you wish to copy and click the submit button. A random code will be generated for your submission.

4. To retrieve the content, enter the random code within 5 minutes of submission.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes -p 12215' git push git@192.168.1.71:/sg_it/clip_box

GIT_SSH_COMMAND='ssh -i ~/.ssh/id_ed25519 -o IdentitiesOnly=yes -p 12215' git clone git@192.168.1.71:/sg_it/p101