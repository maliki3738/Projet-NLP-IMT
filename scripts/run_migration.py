#!/usr/bin/env python3
"""Exécute un fichier SQL sur une base MySQL sans dépendre du client `mysql`.

Usage:
  python scripts/run_migration.py --host localhost --port 3306 --user root --database chainlit --file scripts/mysql_add_missing_columns_compat.sql

Le script demande le mot de passe si `--password` n'est pas fourni.
"""
import argparse
import getpass
import pymysql
import sys


def run_sql_file(conn, path: str):
	with open(path, "r", encoding="utf-8") as f:
		sql = f.read()

	# Split statements on ';' and execute one by one
	statements = [s.strip() for s in sql.split(";") if s.strip()]

	with conn.cursor() as cur:
		for stmt in statements:
			try:
				cur.execute(stmt)
			except Exception as e:
				print(f"Erreur lors de l'exécution d'une instruction:\n{stmt[:200]}...\n-> {e}")
	conn.commit()


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("--host", default="localhost")
	parser.add_argument("--port", default=3306, type=int)
	parser.add_argument("--user", default="root")
	parser.add_argument("--password", default=None)
	parser.add_argument("--database", default="chainlit")
	parser.add_argument("--file", default="scripts/mysql_add_missing_columns_compat.sql")
	args = parser.parse_args()

	if args.password is None:
		args.password = getpass.getpass("MySQL password: ")

	# Try to connect to the target database; if it doesn't exist, create it then reconnect
	try:
		conn = pymysql.connect(host=args.host, port=args.port, user=args.user, password=args.password, database=args.database, charset="utf8mb4", autocommit=False)
	except pymysql.err.OperationalError as e:
		# 1049 = Unknown database
		if e.args and e.args[0] == 1049:
			print(f"Base '{args.database}' introuvable — création en cours...")
			try:
				# connect without database
				conn0 = pymysql.connect(host=args.host, port=args.port, user=args.user, password=args.password, charset="utf8mb4", autocommit=True)
				with conn0.cursor() as cur:
					cur.execute(f"CREATE DATABASE IF NOT EXISTS `{args.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
				conn0.close()
				# reconnect to the newly created database
				conn = pymysql.connect(host=args.host, port=args.port, user=args.user, password=args.password, database=args.database, charset="utf8mb4", autocommit=False)
			except Exception as e2:
				print(f"Impossible de créer la base '{args.database}': {e2}")
				sys.exit(1)
		else:
			print(f"Impossible de se connecter à MySQL: {e}")
			sys.exit(1)
	except Exception as e:
		print(f"Impossible de se connecter à MySQL: {e}")
		sys.exit(1)

	try:
		run_sql_file(conn, args.file)
		print("Migration exécutée avec succès.")
	finally:
		conn.close()


if __name__ == "__main__":
	main()

