RESULT_TIME_COLUMN_NAMES = ['Guntime', 'Nettime', 'Chiptim', 'Time', 'Pace']

TABLE_DEFS = {
    "app_run":
    {
        "name": "app_run",
        "columns":
        {
            "id": "integer primary key",
            "ts": "datetime"
        }
    },

    "log":
    {
        "name": "log_entries",
        "columns":
        {
            "id": "integer primary key",
            "app_run_id": "integer not null",
            "error": "bit",
            "filename": "text",
            "category": "text",
            "details": "text"
        }
    },

    "result":
    {
        "name": "result",
        "columns":
        {
            "id": "integer primary key",
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
            UNIQUE(race_id, runner_id, division_total, bib_num)
        """,
        "column_renames":
        {
            "Ag": "age",
            "Age": "age",
            "Bib#": "bib_num",
            "Chiptim": "net_time",
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

    "race":
    {
        "name": "race",
        "columns":
        {
            "id": "integer primary key",
            "series_id": "integer",
            "date_time": "datetime",
            "name": "text",
            "location": "varchar(255)",
            "certification": "varchar(255)",
            "filename": "text",
            "dist": "decimal(5,1)"
        },
        "column_renames": {
        }
    },

    "runner":
    {
        "name": "runner",
        "columns":
        {
            "id": "integer primary key",
            "name": "text",
            "sex": "text",
            "approximate_birthdate": "date",
            "first_name": "text",
            "last_name": "text",
            "middle_name": "text",
            "name_suffix": "text"
        },
        "column_renames": {
        }
    },

    "series":
    {
        "name": "series",
        "columns":
        {
            "id": "integer primary key",
            "name": "text",
            "month": "integer",
            "dist": "decimal(5,1)"
        },
        "column_renames": {
        }
    }
}
