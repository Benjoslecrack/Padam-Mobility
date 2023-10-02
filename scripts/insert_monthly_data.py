import datetime
import os
import random
from typing import List, Literal, Tuple
import psycopg2
from psycopg2 import extensions
from dateutil.relativedelta import relativedelta
import typer

# La variable d'environnement RANDOM_MAIN_CONTROLLER détermine la quantité de données générées.
# Si elle n'est pas définie, elle est fixée à 100 par défaut.
RANDOM_MAIN_CONTROLLER = int(os.environ.get("RANDOM_MAIN_CONTROLLER", 100))

def get_connection_db(target: Literal["production", "warehouse"]) -> extensions.connection:
    """
    Établit et retourne une connexion à la base de données en fonction de la cible (production ou entrepôt).
    """
    return psycopg2.connect(
        host="localhost",
        database="production_data",
        user="postgres",
        password="admin"
    )

def get_connection_production_db() -> extensions.connection:
    """
    Retourne une connexion à la base de données de production.
    """
    return get_connection_db(target="production")

def get_connection_warehouse_db() -> extensions.connection:
    """
    Retourne une connexion à la base de données de l'entrepôt.
    """
    return get_connection_db(target="warehouse")

def delete_monthly_data_entity_content(year: int, month: int):
    """
    Supprime les données de l'entité pour l'année et le mois spécifiés.
    """
    conn = get_connection_production_db()  # Établir une connexion à la base de données de production
    cursor = conn.cursor()  # Créer un objet curseur pour exécuter des requêtes SQL

    # Requête SQL pour supprimer les données pour l'année et le mois spécifiés
    drop_query = f"""
    DELETE FROM "entity"
        WHERE 
            EXTRACT(YEAR FROM "created_at") = {year} 
            AND
            EXTRACT(MONTH FROM "created_at") = {month} 
    """
    cursor.execute(query=drop_query)  # Exécuter la requête DELETE
    conn.commit()  # Valider la transaction dans la base de données

    cursor.close()  # Fermer le curseur
    conn.close()  # Fermer la connexion

def generate_data(year: int, month: int) -> List[Tuple[datetime.datetime, int]]:
    """
    Génère des données pour l'année et le mois spécifiés.
    """
    random.seed(year + month)  # Initialiser le générateur de nombres aléatoires avec une graine basée sur l'année et le mois
    print(f"Generating data for year {year} and month {month}")
    random.seed(year + month)
    random_control_param = min(13 - month, month)
    random_control_scale = RANDOM_MAIN_CONTROLLER
    min_delay_between_entity_seconds = int(
        1 / random_control_param * 10_000 / (random_control_scale)
    )
    max_delay_between_entity_seconds = int(
        1 / random_control_param * 10_000 / (random_control_scale) * 2
    )
    min_value = random_control_scale * random_control_param
    max_value = 2 * random_control_scale * random_control_param

    first_date = datetime.datetime(year=year, month=month, day=1)
    current_date = first_date
    elements_to_add = []
    while current_date < first_date + relativedelta(months=1):
        if current_date.weekday() < 5:
            value = random.randint(min_value, max_value)
        else:
            value = random.randint(2 * min_value, 2 * max_value)
        elements_to_add.append((current_date, value))

        current_date += relativedelta(
            seconds=random.randint(
                min_delay_between_entity_seconds, max_delay_between_entity_seconds
            )
        )
    print(
        (
            f"Generating data for year {year} and month {month} -> "
            f"{len(elements_to_add)} elements to insert"
        )
    )
    return elements_to_add  # Retourner la liste des données générées

def insert_into_entity_table(data: List[Tuple[datetime.datetime, int]]):
    """
    Insère les données spécifiées dans la table "entity" de la base de données de production.
    """
    conn = get_connection_production_db()  # Établir une connexion à la base de données de production
    cursor = conn.cursor()  # Créer un objet curseur pour exécuter des requêtes SQL

    # Requête SQL pour insérer les données dans la table "entity"
    insert_query = """INSERT INTO "entity"
                (
                    "created_at",
                    "value"
                )
                VALUES (%s, %s)
    """
    cursor.executemany(query=insert_query, vars_list=data)  # Exécuter la requête INSERT avec les données spécifiées
    conn.commit()  # Valider la transaction dans la base de données

    cursor.close()  # Fermer le curseur
    conn.close()  # Fermer la connexion

def main(year: int, month: int):
    """
    Fonction principale du script. Supprime les données existantes de l'entité pour l'année et le mois spécifiés,
    génère de nouvelles données et les insère dans la table "entity".
    """
    delete_monthly_data_entity_content(year=year, month=month)  # Supprimer les données existantes
    data = generate_data(year=year, month=month)  # Générer de nouvelles données
    insert_into_entity_table(data=data)  # Insérer les nouvelles données dans la base de données

if __name__ == "__main__":
    typer.run(main)  # Exécuter la fonction main() lorsque le script est exécuté en tant que programme principal
