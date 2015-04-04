TABLE_DEFS = {
    "result": {
        "name": "result",
        "columns": {
            "id": "int not null primary key auto_increment",
            "age": "text",
            "bib_num": "text",
            "division": "text",
            "division_total": "text",
            "gun_time": "decimal(7,4)",
            "net_time": "decimal(7,4)",
            "runner_name": "text",
            "place": "text",
            "race_id": "integer",
            "result_id": "integer",
            "birthdate_lte": "date"
        },
        "column_renames": {
            "Ag": "age",
            "Age": "age",
            "Bib#": "bib_num",
            "Div": "division",
            "Div/Tot": "division_total",
            "Guntime": "gun_time",
            "Name": "runner_name",
            "Nettime": "net_time",
            "Place": "place",
            "S": "sex",
            "Time": "gun_time"
        },
    },

    "race": {
        "name": "race",
        "columns": {
            "id": "int not null primary key",
            "date": "date",
            "time": "time",
            "name": "text",
            "location": "text",
            "certification": "text"
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
}
