import sys
import pyttsx3
import speech_recognition as sr
import requests  # Pour appeler l'API Google Maps et envoyer les alertes
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt  # Pour gérer les événements clavier


class VoiceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interface avec Bouton Voice")
        self.setGeometry(100, 100, 400, 200)

        # Créer le bouton
        self.voice_button = QPushButton("Activer", self)
        self.voice_button.clicked.connect(self.on_voice_button_click)
        self.voice_button.setFocusPolicy(Qt.NoFocus)

        # Configurer le layout
        layout = QVBoxLayout()
        layout.addWidget(self.voice_button)

        # Configurer le widget central
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Initialiser le moteur de synthèse vocale
        self.engine = pyttsx3.init()

    def on_voice_button_click(self):
        # Action à effectuer lorsque le bouton est cliqué
        self.engine.say("Activation de l'écoute pour les bruits suspects.")
        self.engine.runAndWait()
        self.listen_for_suspicious_sounds()

    def listen_for_suspicious_sounds(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Écoute en cours...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio, language="fr-FR")
                print(f"Vous avez dit : {text}")
                # Vérifier si les mots-clés sont présents
                if any(keyword in text.lower() for keyword in ["danger", "alerte", "à l'aide", "au secours"]):
                    self.trigger_alert()
                else:
                    print("Aucun bruit suspect détecté.")
            except sr.UnknownValueError:
                print("Je n'ai pas compris le son.")
            except sr.RequestError:
                print("Erreur de connexion au service de reconnaissance vocale.")
            except Exception as e:
                print(f"Erreur : {e}")

    def trigger_alert(self):
        # Déclencher une alerte et obtenir la localisation
        self.engine.say("Alerte ! Bruit suspect détecté !")
        self.engine.runAndWait()
        print("Alerte déclenchée !")

        # Obtenir la localisation via l'API Google Maps
        location = self.get_location()
        if location:
            latitude, longitude, google_maps_link = location
            print(f"Localisation : Latitude {latitude}, Longitude {longitude}")
            print(f"Lien Google Maps : {google_maps_link}")
            self.engine.say(f"Votre localisation est latitude {latitude} et longitude {longitude}.")
            self.engine.say("Vous pouvez consulter votre position sur Google Maps.")
            self.engine.runAndWait()
        else:
            latitude, longitude, google_maps_link = None, None, None
            print("Impossible d'obtenir la localisation.")
            self.engine.say("Impossible d'obtenir votre localisation.")
            self.engine.runAndWait()

        # Envoyer l'alerte à l'API Django
        self.envoyer_alerte("Bruit suspect détecté", "critical", latitude, longitude, google_maps_link)

    def envoyer_alerte(self, message, niveau="info", latitude=None, longitude=None, maps_link=None):
        """
        Envoie une alerte à l'API Django.
        """
        API_URL = "http://127.0.0.1:8000/api/alerts/"
        
        data = {
            "message": message,
            "niveau": niveau,
            "latitude": latitude,
            "longitude": longitude,
            "maps_link": maps_link
        }
        
        headers = {'Content-Type': 'application/json'}
        
        try:
            response = requests.post(API_URL, json=data, headers=headers)
            if response.status_code == 201:
                print("✅ Alerte envoyée avec succès :", response.json())
            else:
                print("❌ Erreur lors de l'envoi de l'alerte :", response.text)
        except requests.exceptions.RequestException as e:
            print("❌ Problème de connexion à l'API :", e)

    def get_location(self):
        try:
            # Remplacez "YOUR_API_KEY" par votre clé API Google
            api_key = "AIzaSyDZRfqodpSlcYJ9BfclQ8ba5Pg3Q_4hfYI"
            url = f"https://www.googleapis.com/geolocation/v1/geolocate?key={api_key}"

            # Corps de la requête pour demander la localisation
            payload = {
                "considerIp": True  # Utiliser également l'adresse IP si nécessaire
            }

            # Envoyer une requête POST à l'API Google Geolocation
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                location = data.get("location")
                if location:
                    latitude = location.get("lat")
                    longitude = location.get("lng")
                    # Retourner un lien Google Maps
                    google_maps_link = f"https://www.google.com/maps?q={latitude},{longitude}"
                    return latitude, longitude, google_maps_link
                else:
                    print("Impossible d'obtenir les coordonnées.")
                    return None
            else:
                print(f"Erreur API : {response.status_code}, {response.text}")
                return None
        except Exception as e:
            print(f"Erreur lors de l'appel à l'API : {e}")
            return None

    def keyPressEvent(self, event):
        # Détecter si la touche "Espace" est pressée
        if event.key() == Qt.Key_Space:
            print("Touche Espace pressée. Déclenchement de l'alerte.")
            self.trigger_alert()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceApp()
    window.show()
    sys.exit(app.exec_())
