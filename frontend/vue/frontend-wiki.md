
===FRONTEND WIKI===

1. Overview

    - The Vue frontend is a modern application that provides a dynamic, interactive user experience for Chigame, including features like lobbies, tournaments, forums, and user profiles.
    - All Vue code is located in the frontend/vue directory of Chigame.


2. Requirements

    Required Software:
    - Node.js
    - npm


3. Installation

    Make sure when working on vue code to first:
    - cd frontend/vue

    To install Node
    Download: https://nodejs.org/

    To install npm (should come with node by default but just in case):
    - in linux run...
    sudo apt install npm
    (npm install or npm i should work too)

4. Running the Development Server

    To start the Vue frontend:
    - npm run dev

    Default URL (http://localhost:5173)
    Will auto-reload as you update

5. Usage

    Main Pages (in frontend/vue/src/components/pages):
    - Home (/)
    - About (/about)
    - Games (/games)
    - Lobbies (/lobbies)
    - Tournaments (/tournaments)
    - Forums (/forums)
    - Profile (/profile)
    - Login/Signup (/login, /signup)

    Navbar and footer has links to all pages

    Routing
    - Must define routes(link paths) in frontend/vue/src/router.js, and if including in navbar or footer, link to them as well in frontend/vue/src/components.

    Images: frontend/vue/src/pages/images/ and frontend/vue/src/components/images/


6. Future Tips

    Adding new pages:
    - Create a new .vue file in frontend/vue/src/components/pages/.
    - Import and add it to the routes in frontend/vue/src/router.js.

    Styling:
    - Use <style scoped> in your Vue files for local styles.

    Resources:
    - Vue 3 Docs https://vuejs.org/guide/introduction#introduction
    - Vue Router Docs https://router.vuejs.org/guide/
    - Vue Style Guide https://v2.vuejs.org/v2/style-guide/?redirect=true

7. Troubleshooting

    npm ERR! enoent ... package.json:
    - Make sure you are in the frontend/vue directory before running any npm commands.

    Port already in use:
    - If localhost:5173 is busy, Vue will suggest another port in the terminal.

    Where to ask for help:
    - (As of 2025) use Slack to ask for any questions, current frontend team 2025 is Claire Zhang, Paige Jacobsen, David Lee, Rolando Vazquez, and Jenn Uche (may still be in the Slack)
