"""Lecture et typage des fichiers sources, partagés par les notebooks InduSense.

- detect_charset, detect_separator : encodage et séparateur d'un fichier
- infer_type : type d'une colonne CSV, deviné à partir des valeurs
- sql_column_type, parse_sql_tables : types déclarés et données d'un script SQL (lu avec sqlglot, jamais exécuté)
"""
import csv
from pathlib import Path

import pandas as pd
import sqlglot
from sqlglot import exp


def detect_charset(path):
    """Encodage du fichier : UTF-8 (avec ou sans BOM), sinon Windows-1252, sinon Latin-1."""
    raw = Path(path).read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"
    for enc in ("utf-8", "cp1252"):
        try:
            raw.decode(enc)
            return enc
        except UnicodeDecodeError:
            pass
    return "latin-1"  # décode toujours


def detect_separator(path, charset, n_lines=20):
    """Séparateur deviné sur les premières lignes (, ; tabulation |)."""
    with open(path, encoding=charset, newline="") as f:
        sample = "".join(f.readline() for _ in range(n_lines))
    return csv.Sniffer().sniff(sample, delimiters=",;\t|").delimiter


DATE_FORMATS = [("DATE", "%Y-%m-%d"), ("DATETIME", "%Y-%m-%d %H:%M:%S"), ("TIME", "%H:%M"), ("TIME", "%H:%M:%S")]


def infer_type(name, series):
    """IDENTITY, BOOLEAN, INTEGER, FLOAT, DATE, DATETIME, TIME ou TEXT."""
    if name == "id" or name.endswith("_id"):
        return "IDENTITY"
    values = series.dropna()
    if pd.api.types.is_numeric_dtype(series):
        if len(values) and values.isin([0, 1]).all():
            return "BOOLEAN"
        return "INTEGER" if pd.api.types.is_integer_dtype(series) or (values % 1 == 0).all() else "FLOAT"
    for type_name, fmt in DATE_FORMATS:
        if len(values) and pd.to_datetime(values, format=fmt, errors="coerce").notna().all():
            return type_name
    return "TEXT"


# Types SQL déclarés -> nos types (le reste : VARCHAR, TEXT... -> TEXT)
SQL_TYPES = {
    "INT": "INTEGER", "SMALLINT": "INTEGER", "BIGINT": "INTEGER",
    "DECIMAL": "FLOAT", "FLOAT": "FLOAT", "DOUBLE": "FLOAT",
    "DATE": "DATE", "TIMESTAMP": "DATETIME", "TIMESTAMPTZ": "DATETIME", "TIME": "TIME",
    "BOOLEAN": "BOOLEAN",
}


def sql_column_type(col):
    """Type d'une colonne de CREATE TABLE : IDENTITY pour clé primaire/étrangère ou *_id, sinon type déclaré."""
    is_key = any(isinstance(c.kind, (exp.PrimaryKeyColumnConstraint, exp.Reference)) for c in col.constraints)
    if is_key or col.name == "id" or col.name.endswith("_id"):
        return "IDENTITY"
    return SQL_TYPES.get(col.kind.this.name, "TEXT")


def parse_sql_tables(sql_text):
    """{table: (DataFrame des INSERT, {colonne: type})} à partir d'un script PostgreSQL (lu, jamais exécuté)."""
    types, rows = {}, {}
    for stmt in sqlglot.parse(sql_text, read="postgres"):
        if isinstance(stmt, exp.Create) and stmt.kind == "TABLE":
            name = stmt.this.this.name
            types[name] = {c.name: sql_column_type(c) for c in stmt.this.expressions if isinstance(c, exp.ColumnDef)}
            rows[name] = []
        elif isinstance(stmt, exp.Insert):
            name = stmt.this.this.name
            cols = [c.name for c in stmt.this.expressions]
            rows[name] += [dict(zip(cols, (v.to_py() for v in row.expressions))) for row in stmt.expression.expressions]
    return {name: (pd.DataFrame(rows[name]), types[name]) for name in types}
