import psycopg2

# Établir la connexion à la base de données production_data
conn_production = psycopg2.connect(
    host="localhost",
    database="production_data",
    user="postgres",
    password="admin"
)

# Établir la connexion à la base de données warehouse_data
conn_warehouse = psycopg2.connect(
    host="localhost",
    database="warehouse_data",
    user="postgres",
    password="admin"
)

# Ouvrir un curseur pour la base de données production_data
cur_production = conn_production.cursor()

# Ouvrir un curseur pour la base de données warehouse_data
cur_warehouse = conn_warehouse.cursor()

# Requête SQL pour effectuer un chargement incrémentiel des données
incremental_load_query = """
INSERT INTO warehouse_data.entity (created_at, value)
SELECT pd.created_at, pd.value
FROM production_data.entity pd
LEFT JOIN public.entity wd
ON pd.created_at = wd.created_at
WHERE wd.created_at IS NULL;
"""

# Exécuter la requête de chargement incrémentiel
cur_warehouse.execute(incremental_load_query)

# Requête SQL pour créer la vue des statistiques mensuelles
monthly_stats_view_query = """
CREATE OR REPLACE VIEW monthly_stats AS
SELECT
  EXTRACT(YEAR FROM created_at) AS year,
  EXTRACT(MONTH FROM created_at) AS month,
  SUM(value) AS sum_values,
  MIN(value) AS min_values,
  MAX(value) AS max_values,
  AVG(value) AS mean_values
FROM warehouse_data.entity
GROUP BY EXTRACT(YEAR FROM created_at), EXTRACT(MONTH FROM created_at);
"""

# Exécuter la requête pour créer la vue des statistiques mensuelles
cur_warehouse.execute(monthly_stats_view_query)

# Valider et fermer les connexions et curseurs
conn_production.commit()
conn_warehouse.commit()
cur_production.close()
cur_warehouse.close()
conn_production.close()
conn_warehouse.close()
