TABLE_DEFS = {
    "result": {
        "name": "result",
        "columns": {
            "id": "int not null primary key auto_increment",
            "bib_num": "varchar(255)",
            "age": "text",
            "division": "varchar(255)",
            "division_total": "varchar(255)",
            "gun_time": "decimal(7,4)",
            "net_time": "decimal(7,4)",
            "pace": "decimal(7,4)",
            "place": "varchar(255)",
            "race_id": "integer",
            "runner_id": "integer",
            "percentile": "decimal(4,1)"
        },
        "ext_table_def": """
            CONSTRAINT `UQ_result` UNIQUE NONCLUSTERED (
                `race_id`, `runner_id`, `division_total`, `bib_num`
            )
        """,
        "column_renames": {
            "Ag": "age",
            "Age": "age",
            "Bib#": "bib_num",
            "Div": "division",
            "Div/Tot": "division_total",
            "Guntime": "gun_time",
            "Name": "runner_name",
            "Nettime": "net_time",
            "Pace": "pace",
            "Place": "place",
            "S": "sex",
            "Time": "gun_time"
        },
    },

    "race": {
        "name": "race",
        "columns": {
            "id": "int not null primary key",
            "series_id": "int",
            "date": "date",
            "time": "time",
            "name": "text",
            "location": "varchar(255)",
            "certification": "varchar(255)",
            "filename": "text",
            "dist": "decimal(5,1)"
        },
        "column_renames": {
        }
    },
              
    "runner": {
        "name": "runner",
        "columns": {
            "id": "int not null primary key",
            "name": "text",
            "sex": "text",
            "approximate_birthdate": "date"
        },
        "column_renames": {
        }
    },
              
    "series": {
        "name": "series",
        "columns": {
            "id": "int not null primary key",
            "name": "text",
            "month": "int",
            "dist": "decimal(5,1)"
        },
        "column_renames": {
        }
    },
}
