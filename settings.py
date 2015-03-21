TABLE_DEFS = {
	"result": {
		"name": "result",
		"columns": {
			"age": {"type": "Text"},
			"bib_num": {"type": "Text"},
			"division": {"type": "Text"},
			"division_total": {"type": "Text"},
			"gun_time": {"type": "Text"},
			"runner_name": {"type": "Text"},
			"net_time": {"type": "Text"},
			"place": {"type": "Text"},
			"time": {"type": "Text"}
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
		}
	},
			
	"race": {
		"name": "race",
		"columns": {
			"date": {"type": "Text"},
			"time": {"type": "Text"},
			"name": {"type": "Text"},
			"location": {"type": "Text"}
		},
		"column_renames": {
		}
	},
}
