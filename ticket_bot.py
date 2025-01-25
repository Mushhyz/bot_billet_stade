import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time
import requests

load_dotenv()

# Configuration du site
BASE_URL = "https://www.stadefrance.com/billetterie"
EVENT_NAME = os.getenv("EVENT_NAME", "Match Équipe de France")

# Authentification
EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# Configuration des billets
TICKET_QUANTITY = int(os.getenv("TICKET_QUANTITY", "2"))
TICKET_CATEGORY = os.getenv("TICKET_CATEGORY", "Catégorie 1")

# Paramètres techniques
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "5"))
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

# Informations de paiement (test)
PAYMENT_INFO = {
    "card_number": os.getenv("CARD_NUMBER", "4111111111111111"),
    "expiry_date": os.getenv("EXPIRY_DATE", "12/25"),
    "cvv": os.getenv("CVV", "123")
}

# Configuration du service CAPTCHA
CAPTCHA_API_KEY = os.getenv("CAPTCHA_API_KEY")
CAPTCHA_SITE_KEY = os.getenv("CAPTCHA_SITE_KEY")

class TicketBot:
    def __init__(self):
        self._setup_logging()
        self._setup_driver()
        self.wait = WebDriverWait(self.driver, TIMEOUT)

    def _setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ticket_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)

    def login(self):
        try:
            self.driver.get(BASE_URL)
            email = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password = self.driver.find_element(By.ID, "password")
            
            email.send_keys(EMAIL)
            password.send_keys(PASSWORD)
            
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            self.logger.info("Connexion réussie")
        except Exception as e:
            self.logger.error(f"Erreur de connexion: {str(e)}")
            raise

    def find_event(self):
        while True:
            try:
                event = self.wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, f"//a[contains(text(), '{EVENT_NAME}')]")
                    )
                )
                event.click()
                self.logger.info(f"Événement '{EVENT_NAME}' trouvé")
                break
            except TimeoutException:
                self.logger.info("Rafraîchissement de la page...")
                self.driver.refresh()
                time.sleep(REFRESH_INTERVAL)

    def select_tickets(self):
        try:
            category = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "seat-category"))
            )
            category.click()
            
            self.driver.find_element(
                By.XPATH, 
                f"//option[contains(text(), '{TICKET_CATEGORY}')]"
            ).click()

            quantity = self.driver.find_element(By.ID, "ticket-quantity")
            quantity.send_keys(str(TICKET_QUANTITY))

            self.driver.find_element(By.CLASS_NAME, "buy-button").click()
            self.logger.info(f"Sélection: {TICKET_QUANTITY} billets en {TICKET_CATEGORY}")
        except Exception as e:
            self.logger.error(f"Erreur de sélection: {str(e)}")
            raise

    def process_payment(self):
        try:
            self.wait.until(
                EC.presence_of_element_located((By.ID, "card-number"))
            ).send_keys(PAYMENT_INFO["card_number"])
            
            self.driver.find_element(By.ID, "expiry-date").send_keys(
                PAYMENT_INFO["expiry_date"]
            )
            self.driver.find_element(By.ID, "cvv").send_keys(
                PAYMENT_INFO["cvv"]
            )

            self.driver.find_element(By.ID, "cgv-checkbox").click()
            self.driver.find_element(By.ID, "confirm-payment").click()
            self.logger.info("Paiement effectué")
        except Exception as e:
            self.logger.error(f"Erreur de paiement: {str(e)}")
            raise

    def solve_captcha(self):
        try:
            captcha_response = requests.post(
                "http://2captcha.com/in.php",
                data={
                    "key": CAPTCHA_API_KEY,
                    "method": "userrecaptcha",
                    "googlekey": CAPTCHA_SITE_KEY,
                    "pageurl": self.driver.current_url
                }
            )
            captcha_id = captcha_response.text.split('|')[1]
            self.logger.info("CAPTCHA ID reçu, en attente de résolution...")

            while True:
                captcha_result = requests.get(
                    f"http://2captcha.com/res.php?key={CAPTCHA_API_KEY}&action=get&id={captcha_id}"
                )
                if captcha_result.text == "CAPCHA_NOT_READY":
                    time.sleep(5)
                else:
                    captcha_code = captcha_result.text.split('|')[1]
                    self.driver.execute_script(
                        f"document.getElementById('g-recaptcha-response').innerHTML='{captcha_code}';"
                    )
                    self.logger.info("CAPTCHA résolu")
                    break
        except Exception as e:
            self.logger.error(f"Erreur de résolution CAPTCHA: {str(e)}")
            raise

    def run(self):
        try:
            self.login()
            self.find_event()
            self.select_tickets()
            self.process_payment()
            self.logger.info("Achat terminé avec succès!")
        except Exception as e:
            self.logger.error(f"Erreur critique: {str(e)}")
        finally:
            self.driver.quit()

if __name__ == "__main__":
    bot = TicketBot()
    bot.run()
