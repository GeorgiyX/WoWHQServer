class SearchJSON():
    json_search = {
        "item_name":"",
        "category":[],
        "min_price":"",
        "max_price":"",
        "lvl":""
    }

    deals = {
        "best_lot" : [
            {"item_game_id": 777, "bid": 11, "buyout": 88, "time_left": "ANY", "server" : "uther", "region" : "us"},
            {"item_game_id": 82800, "bid:": 11, "buyout": 88, "pet_id": 4125, "time_left": "VERY_LONG", "server": "uther", "region": "us"}

        ]
    }
    curl - i - H
    "Content-Type: application/json" - X
    POST - d
    '{
        "best_lot" : [
            {"item_game_id": 777, "bid:": 11, "buyout": 88, "time_left": "ANY", "server" : "uther", "region" : "us"},
            {"item_game_id": 82800, "bid:": 11, "buyout": 88, "pet_id": 4125, "time_left": "VERY_LONG", "server": "uther", "region": "us"}

        ]
    }'
    http: // localhost: 5000  /api/bestaucs/ru
    .0 / tasks
    HTTP / 1.0
    201
    Created
    Content - Type: application / json
    Content - Length: 104
    Server: Werkzeug / 0.8
    .3
    Python / 2.7
    .3
    Date: Mon, 20
    May
    2013
    05: 56:21
    GMT