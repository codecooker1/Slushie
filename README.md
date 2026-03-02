## What is it?

This is a simple anonymous note/quote sharing website. Live at: https://slushienotes.pythonanywhere.com/

No need to create account or sell your soul just to share your little thoughts, just type 'em, verify your email and voila!

## How do I run it?

### Prerequisites
Make sure you have Python installed. This project uses [uv](https://github.com/astral-sh/uv) for lightning-fast dependency management, but standard `pip` works just fine too.

1. Clone the repo
   ```bash
   git clone https://github.com/codecooker1/Slushie.git --depth=1 --single-branch
   cd Slushie
   ```
2. Set up the environment & dependencies
   - If using uv
     ```bash
     uv sync
     ```
   - If using pip and venv
     ```bash
     # Create and activate the virtual environment
     python -m venv .venv
     source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

     # Install dependencies
     pip install -r requirements.txt
     ```
3. Environment Variables
   Open the `.env` file and fill in the data.
   ```bash
   MAIL_PASSWORD=<google app password>
   MAIL_USERNAME=<your google username>
   APP_SECRET_KEY=<a secure password like string of your choice>
   ```
3. Fire it up
   ```bash
   # If using uv:
   uv run app.py

   # If using standard venv:
   python app.py
   ```

## Contribution

If you want to make the code better or introduce new features, feel free to create a pull request with your changes.
