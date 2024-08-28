set filepath=%~dp0
call %filepath%venv\Scripts\activate.bat
python %filepath%cleaner.py
python %filepath%rm_reactions.py
deactivate
