import requests
from bs4 import BeautifulSoup
import re
import argparse


def recuperer_html(url):
    reponse = requests.get(url)
    reponse.raise_for_status()
    return reponse.text

def supprimer_balises_html(texte_html):
    soupe = BeautifulSoup(texte_html, 'html.parser')
    return soupe.get_text()

def charger_parasites(chemin_fichier):
    with open(chemin_fichier, 'r', encoding='utf-8') as fichier:
        parasites = fichier.read().splitlines()
    return parasites

def supprimer_parasites(occurrences, parasites):
    return {mot: occurrences[mot] for mot in occurrences if mot not in parasites}

def extraire_valeurs_attribut(texte_html, balise, attribut):
    soupe = BeautifulSoup(texte_html, 'html.parser')
    return [element.get(attribut) for element in soupe.find_all(balise) if element.has_attr(attribut)]

def compter_occurrences(texte):
    texte = texte.lower()
    texte = re.sub(r'[^\w\s]','', texte)
    mots = texte.split()
    occurrences = {}
    for mot in mots:
        occurrences[mot] = occurrences.get(mot, 0) + 1
    return dict(sorted(occurrences.items(), key=lambda item: item[1], reverse=True))

def audit_ref_seo(url, chemin_parasites):
    html = recuperer_html(url)
    texte_sans_html = supprimer_balises_html(html)
    occurrences = compter_occurrences(texte_sans_html)
    parasites = charger_parasites(chemin_parasites)
    mots_cles = supprimer_parasites(occurrences, parasites)
    
    alt_images = extraire_valeurs_attribut(html, 'img', 'alt')
    liens_href = extraire_valeurs_attribut(html, 'a', 'href')

    liens_entrants = [href for href in liens_href if href.startswith(url)]
    liens_sortants = [href for href in liens_href if not href.startswith(url)]

    return {
        'Mots clés': list(mots_cles.items())[:3],  # Affiche les 3 premiers mots clés
        'Nombre de liens entrants': len(liens_entrants),
        'Nombre de liens sortants': len(liens_sortants),
        'Balises alt manquantes': sum(1 for alt in alt_images if not alt)
    }

# Utilisation de la fonction audit_ref_seo
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Effectuer un audit SEO simple sur une page web.')
    parser.add_argument('url', help='Adresse URL de la page web à analyser')
    parser.add_argument('fichier_parasites', help='Chemin pour accéder au fichier CSV contenant les mots parasites', default='parasite.csv', nargs='?')
    args = parser.parse_args()

    resultats = audit_ref_seo(args.url, args.fichier_parasites)
    print(resultats)
