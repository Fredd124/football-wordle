# Football Wordle

This repository contains a "Guess the Football Player" game, inspired by Loldle!

- **Frontend:** Built with Angular.
- **Backend:** Simple Flask API.
- **Data:** Player data is gathered using Python web scraping.

## How to use

1. **Clone the repo**

    ```sh
    git clone https://github.com/Fredd124/football-wordle.git
    ```

2. **Install dependencies**

    For the Flask backend:
    ```sh
    cd backend 
    pip install -r requirements.txt
    ```

    For the Angular frontend:
    ```sh
    cd ../frontend            
    npm install
    ```

3. **Run the servers**
    
    **Open two terminals/consoles:** One for the backend, one for the frontend.

    In Terminal 1 — Start the Flask backend::
    ```sh
    cd backend
    python3 app.py
    ```

    In Terminal 2 — Start the Angular frontend:
    ```sh
    cd frontend
    ng serve
    ```

4. **Start guessing!**

    Open your browser and go to [http://localhost:4200](http://localhost:4200) to play the game!

## Demo
The full version can be found in `Demo.mp4`.

![Demo](Demo.gif)
