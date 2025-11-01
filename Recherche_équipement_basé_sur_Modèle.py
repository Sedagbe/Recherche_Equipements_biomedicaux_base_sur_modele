import requests
from bs4 import BeautifulSoup
import re

# En-tête pour simuler un vrai navigateur
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BiomedScanner/1.0; +https://example.com)"
}

# Fonction pour chercher sur DuckDuckGo
def rechercher_modele(modele):
    print(f"\n🔎 Recherche d'informations pour : {modele}\n")

    # Requête sur DuckDuckGo HTML (version légère)
    url = "https://html.duckduckgo.com/html/"
    data = {"q": modele + " medical device OR biomedical OR manual OR datasheet"}
    try:
        response = requests.post(url, data=data, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException:
        print("⚠️  Erreur réseau : impossible d'accéder à DuckDuckGo.")
        return []

    # Analyse du HTML
    soup = BeautifulSoup(response.text, "html.parser")
    liens = []
    for a in soup.select("a.result__a"):
        titre = a.get_text().strip()
        lien = a.get("href")
        if lien and lien.startswith("http"):
            liens.append((titre, lien))
    return liens[:10]  # Limité à 10 résultats pertinents

# Fonction pour analyser le contenu d'une page web
def analyser_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        texte = response.text
        soup = BeautifulSoup(texte, "html.parser")
        contenu = soup.get_text(separator="\n")
    except:
        return {}

    # Recherche d'informations clés
    info = {}
    if re.search(r"Model|Modèle|Reference|Ref|KR-|SN", contenu, re.IGNORECASE):
        info["modele_trouve"] = True
    fabricant = re.findall(r"(Manufacturer|Fabricant|Brand)\s*[:\-]?\s*([A-Za-z0-9\s,&]+)", contenu)
    if fabricant:
        info["fabricant"] = list({f[1].strip() for f in fabricant})
    pdfs = re.findall(r"https?://[^\s]+\.pdf", contenu)
    if pdfs:
        info["pdfs"] = list(set(pdfs))
    return info

# Fonction principale
def main():
    print("=== IDENTIFICATION D'APPAREIL BIOMÉDICAL ===")
    print("Exemple : KR-1000, etc.\n")

    modele = input("👉 Entrez le modèle ou numéro de série : ").strip()
    if not modele:
        print("❌ Aucun modèle saisi.")
        return

    resultats = rechercher_modele(modele)
    if not resultats:
        print("⚠️  Aucun résultat trouvé sur le web.")
        return

    print("\n🌐 Résultats trouvés :\n")
    for i, (titre, lien) in enumerate(resultats, 1):
        print(f"{i}. {titre}\n   🔗 {lien}\n")

    choix = input("Souhaitez-vous analyser une page pour plus d'infos ? (oui/non) : ").lower()
    if choix in ["oui", "o", "y"]:
        num = int(input("Numéro du lien à analyser (1-10) : "))
        if 1 <= num <= len(resultats):
            url = resultats[num - 1][1]
            print(f"\n📥 Analyse de la page : {url}\n")
            infos = analyser_page(url)
            if not infos:
                print("Aucune information utile extraite.")
            else:
                print("✅ Informations extraites :")
                if "fabricant" in infos:
                    print("   Fabricant(s) :", ", ".join(infos["fabricant"]))
                if "pdfs" in infos:
                    print("   Manuels PDF trouvés :")
                    for pdf in infos["pdfs"]:
                        print("   📄", pdf)
                if "modele_trouve" in infos:
                    print("   ✔️  Le modèle semble présent dans cette page.")
        else:
            print("Numéro invalide.")
    else:
        print("\nFin du programme. ")

if __name__ == "__main__":
    main()
