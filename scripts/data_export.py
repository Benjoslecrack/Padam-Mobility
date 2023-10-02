import csv
import os
import psycopg2
import typer

def export_monthly_and_yearly_stats(year: int, month: int):
    # Établir la connexion à la base de données warehouse_data
    conn_warehouse = psycopg2.connect(
        host="localhost",
        database="warehouse_data",
        user="postgres",
        password="admin"
    )

    # Ouvrir un curseur pour la base de données warehouse_data
    cur_warehouse = conn_warehouse.cursor()

    # Requête SQL pour obtenir les statistiques mensuelles
    monthly_stats_query = "SELECT * FROM monthly_stats WHERE year = %s AND month = %s;"
    cur_warehouse.execute(monthly_stats_query, (year, month))

    # Récupérer les résultats de la requête pour les statistiques mensuelles
    monthly_stats_results = cur_warehouse.fetchall()

    # Requête SQL pour obtenir les statistiques annuelles
    yearly_stats_query = "SELECT * FROM yearly_stats WHERE year = %s;"
    cur_warehouse.execute(yearly_stats_query, (year,))

    # Récupérer les résultats de la requête pour les statistiques annuelles
    yearly_stats_results = cur_warehouse.fetchall()

    # Chemin du dossier "exports" situé un cran au-dessus du dossier du script
    exports_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports")

    # Assurer que le dossier "exports" existe, sinon le créer
    os.makedirs(exports_directory, exist_ok=True)

    # Chemin du fichier CSV des statistiques mensuelles
    monthly_csv_path = os.path.join(exports_directory, f"year={year}", f"entity_stats_monthly_{year}_{month}.csv")

    # Écrire les statistiques mensuelles dans le fichier CSV
    with open(monthly_csv_path, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # Écrire l'en-tête du fichier CSV
        csvwriter.writerow(["year", "month", "sum_values", "min_values", "max_values", "mean_values"])
        # Écrire les données dans le fichier CSV
        csvwriter.writerows(monthly_stats_results)

    # Chemin du fichier CSV des statistiques annuelles
    yearly_csv_path = os.path.join(exports_directory, f"year={year}", f"entity_stats_yearly_{year}.csv")

    # Écrire les statistiques annuelles dans le fichier CSV
    with open(yearly_csv_path, "w", newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        # Écrire l'en-tête du fichier CSV
        csvwriter.writerow(["year", "sum_values", "min_values", "max_values", "mean_values"])
        # Écrire les données dans le fichier CSV
        csvwriter.writerows(yearly_stats_results)

    # Valider et fermer la connexion et le curseur
    conn_warehouse.commit()
    cur_warehouse.close()
    conn_warehouse.close()

def main(year: int, month: int):
    export_monthly_and_yearly_stats(year, month)

if __name__ == "__main__":
    typer.run(main)
