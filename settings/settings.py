TABLE_DEFS = {
    "result": {
        "name": "result",
        "columns": {
            "id": "int not null primary key auto_increment",
            "bib_num": "text",
            "age": "text",
            "division": "text",
            "division_total": "text",
            "gun_time": "decimal(7,4)",
            "net_time": "decimal(7,4)",
            "pace": "decimal(7,4)",
            "place": "text",
            "race_id": "integer",
            "runner_id": "integer"
        },
        "ext_table_def": """
            CONSTRAINT `UQ_result` UNIQUE NONCLUSTERED (
                `race_id`, `runner_id`, `gun_time`, `net_time`
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
            "location": "text",
            "certification": "text",
            "filename": "text",
            "dist": "decimal(5,2)"
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
            "month": "int"
        },
        "column_renames": {
        }
    },
}
