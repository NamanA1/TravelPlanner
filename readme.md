Travel Itinerary Planner (LangChain + Gemini API)

An AI-powered Travel Itinerary Planner that generates concise and personalized travel plans based on user inputs like city, duration, budget, and preferred language.

This project demonstrates how LangChain and Google Gemini API can be combined to build real-world, user-focused AI applications.

✨ Features
🧳 Generates short 4–5 line itineraries
🌍 Supports multiple cities and languages
💰 Budget-based recommendations (Low / Medium / High)
📅 Custom plans based on number of travel days
⚡ Fast and efficient using Gemini Flash model
🛠️ Tech Stack
Python
LangChain
Google Gemini API
python-dotenv
📂 Project Structure
travel-itinerary-planner/
│── travel_planner.py
│── .env
│── requirements.txt
│── README.md
⚙️ Setup Instructions
1️⃣ Clone the repository
git clone https://github.com/your-username/travel-itinerary-planner.git
cd travel-itinerary-planner
2️⃣ Install dependencies
pip install -r requirements.txt
3️⃣ Add your API key

Create a .env file in the root directory:

GOOGLE_API_KEY=your_api_key_here
4️⃣ Run the project
python travel_planner.py
🧠 How It Works
User provides:
City
Number of days
Budget (low / medium / high)
Language
LangChain structures the prompt.
Gemini API processes the request and generates a short itinerary including:
Famous destinations
Local experiences
Budget-aware suggestions
📌 Example

Input:

City: Manali  
Days: 3  
Budget: Medium  
Language: English  

Output:

Day 1: Visit Hadimba Temple and explore Mall Road cafes.  
Day 2: Enjoy adventure activities at Solang Valley.  
Day 3: Visit Rohtang Pass for scenic views.  
Try local Himachali food and stay in mid-range hotels.
🚀 Use Cases
Travel planning assistants
AI chatbots for tourism businesses
WhatsApp/Telegram travel bots
Micro SaaS products
🔒 Security Note
Never commit your .env file
Add .env to .gitignore
📈 Future Improvements
🏨 Hotel and cost breakdown
📍 Google Maps integration
🤖 Conversational AI agent (multi-step planning)
🌐 Web UI (Streamlit / React)
🙌 Contributing

Feel free to fork this repo, raise issues, or submit pull requests.

⭐ Support

If you found this project useful, consider giving it a ⭐ on GitHub!