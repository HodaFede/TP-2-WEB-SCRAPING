import csv
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_user_inputs():
    today = datetime.today()
    today_str = today.strftime("%d/%m/%Y")
    in_7_days_str = (today + timedelta(days=7)).strftime("%d/%m/%Y")

    max_results = input(f"Nombre maximum de résultats (défaut: 10) : ")
    max_results = int(max_results) if max_results.strip() else 10

    start_date = input(f"Date de début (JJ/MM/AAAA) (défaut: {today_str}) : ")
    start_date = start_date.strip() if start_date.strip() else today_str

    end_date = input(f"Date de fin (JJ/MM/AAAA) (défaut: {in_7_days_str}) : ")
    end_date = end_date.strip() if end_date.strip() else in_7_days_str

    specialty = input("Spécialité médicale : ")

    sector = input("Secteur assurance (1 = Secteur 1, 2 = Secteur 2, non = Non conventionné) (défaut: 1) : ")
    sector = sector.strip() if sector.strip() else "1"

    consultation_type = input("Type de consultation (visio ou sur place) : ")
    price_min = input("Prix minimum (€) : ")
    price_max = input("Prix maximum (€) : ")
    address_filter = input("Filtre géographique (ex: 75015) : ")
    address_exclude = input("Adresse à exclure (laisser vide si aucune) : ")

    return {
        "max_results": max_results,
        "start_date": start_date,
        "end_date": end_date,
        "specialty": specialty,
        "sector": sector,
        "consultation_type": consultation_type,
        "price_min": price_min,
        "price_max": price_max,
        "address_filter": address_filter,
        "address_exclude": address_exclude,
    }

# Navigateur Selenium
def setup_driver():
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    return driver

# Champ de recherche
def find_search_field(driver, wait):
    try:
        search_input = wait.until(EC.presence_of_element_located((By.NAME, 'search_query')))
        print(" Champ de recherche trouvé (méthode 1).")
    except:
        search_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*=\"Quoi\"]')))
        print(" Champ de recherche trouvé (méthode alternative).")
    return search_input

#Extraire les infos d'un médecin 
def extract_doctor_info(doc_element):
    name = doc_element.find_element(By.CSS_SELECTOR, '[data-test="doctor-name"]').text.strip()
    next_avail = doc_element.find_element(By.CSS_SELECTOR, '[data-test="next-availability"]').text.strip()

    try:
        consultation_type = doc_element.find_element(By.CSS_SELECTOR, '[data-test="telehealth-badge"]').text.strip()
    except:
        consultation_type = "Sur place"

    try:
        address_block = doc_element.find_element(By.CSS_SELECTOR, '[data-test="address"]')
        address_lines = address_block.text.strip().split("\n")
        rue = address_lines[0]
        code_ville = address_lines[1]
        code_postal = code_ville.split()[0]
        ville = " ".join(code_ville.split()[1:])
    except:
        rue, code_postal, ville = "", "", ""

    try:
        secteur = doc_element.find_element(By.XPATH, './/span[contains(text(), "Secteur")]').text.strip()
    except:
        secteur = "Non précisé"

    try:
        prix = doc_element.find_element(By.XPATH, './/span[contains(text(), "€")]').text.strip()
    except:
        prix = "Non précisé"

    return {
        "Nom complet": name,
        "Prochaine disponibilité": next_avail,
        "Type consultation": consultation_type,
        "Secteur": secteur,
        "Prix": prix,
        "Rue": rue,
        "Code postal": code_postal,
        "Ville": ville,
    }

# Localisation
def apply_filters(data, user_inputs):
    full_address = f"{data['Rue']} {data['Code postal']} {data['Ville']}".lower()
    if user_inputs["address_filter"]:
        keyword = user_inputs["address_filter"].lower()
        if keyword not in full_address:
            return False
    if user_inputs["address_exclude"]:
        exclude_kw = user_inputs["address_exclude"].lower()
        if exclude_kw in full_address:
            return False
    return True

# Scraping page
def scrape_results(driver, user_inputs, wait):
    doctors_data = []

    while len(doctors_data) < user_inputs["max_results"]:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-test="search-result"]')))
        doctors = driver.find_elements(By.CSS_SELECTOR, '[data-test="search-result"]')
        print(f"➡️ {len(doctors)} médecins trouvés sur cette page.")

        for doc in doctors:
            if len(doctors_data) >= user_inputs["max_results"]:
                break
            try:
                data = extract_doctor_info(doc)
                if apply_filters(data, user_inputs):
                    doctors_data.append(data)
            except Exception as e:
                print(f" Erreur lors de l'extraction : {e}")

        
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, '[data-test="pagination-next-page"]')
            if "disabled" not in next_button.get_attribute("class"):
                next_button.click()
                time.sleep(2)
                print("Passage à la page suivante.")
            else:
                print(" Pas de page suivante disponible.")
                break
        except:
            print("Bouton page suivante non trouvé.")
            break

    return doctors_data

# Sauvegarde en CSV
def save_to_csv(data_list, filename="doctors_results.csv"):
    if not data_list:
        print("Aucune donnée à sauvegarder.")
        return

    keys = data_list[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)
    print(f"Données sauvegardées dans {filename}")

# Recherche et scraper
def main():
    user_inputs = get_user_inputs()
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    try:
        driver.get("https://www.doctolib.fr")
        print("Page Doctolib ouverte.")

        # gestion  cookies
        try:
            cookies_button = wait.until(EC.element_to_be_clickable((By.ID, 'didomi-notice-agree-button')))
            cookies_button.click()
            print("Cookies acceptés.")
        except:
            print("Pas de bandeau cookies détecté.")

        # Trouver le champ de recherche et exécuter la recherche
        search_input = find_search_field(driver, wait)
        search_input.send_keys(user_inputs["specialty"])
        search_input.send_keys(Keys.RETURN)

        # Attendre resultats + scraper
        doctors_data = scrape_results(driver, user_inputs, wait)
        save_to_csv(doctors_data)

    except Exception as e:
        print(f" Erreur : {e}")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Page sauvegardée dans debug_page.html pour diagnostic.")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
