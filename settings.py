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
            "runner_name": "text",
            "net_time": "decimal(7,4)",
            "place": "text",
            "time": "decimal(7,4)",
            "race_id": "integer"
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
            "Time": "time"
        },
    },
            
    "race": {
        "name": "race",
        "columns": {
            "id": "int not null primary key",
            "date": "date",
            "time": "time",
            "name": "text",
            "location": "text"
        },
        "column_renames": {
        }
    },
}
