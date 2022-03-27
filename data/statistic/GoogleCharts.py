import json
import os


def pie_chart(param):
    diction = {
        "cols": [
            {"id": "", "label": "Topping", "pattern": "", "type": "string"},
            {"id": "", "label": "Slices", "pattern": "", "type": "number"}
        ],
        "rows": []
    }
    for key, item in param["chart"].items():
        diction["rows"].append(
            {"c": [{"v": key, "f": None}, {"v": item, "f": None}]}
        )
    d = os.path.join(os.path.join(os.getcwd(), 'static'), 'json')
    json.dump(diction, open(os.path.join(d, 'PieChart.json'), 'w'))


def combo_chart(param):
    diction = {
        "cols": [{"id": "", "label": "Topping", "pattern": "", "type": "string"},
                 {"id": "", "label": "Среднее количестово предметов", "pattern": "",
                  "type": "number"}],
        "rows": []
    }
    lessons = []
    for key in param["chart"].keys():
        diction["cols"].append(
            {"id": "", "label": key, "pattern": "", "type": "number"}
        )
        lessons.append(key)
    for key, item in param["days"].items():
        row = [{"v": key, "f": None}, {"v": 0, "f": None}]
        average = []
        for les in lessons:
            row.append({"v": item.get(les, 0), "f": None})
            average.append(item.get(les, 0))
        row[1]["v"] = round(sum(average) / len(average), 1)
        diction["rows"].append({"c": row})
    diction["rows"].sort(key=lambda x: x["c"][0]["v"])

    d = os.path.join(os.path.join(os.getcwd(), 'static'), 'json')
    json.dump(diction, open(os.path.join(d, 'ComboChart.json'), 'w'))


def bar_chart(param):
    if param["teachers"] == {}:
        raise ValueError
    diction = {
        "cols": [{"id": "", "label": "Topping", "pattern": "", "type": "string"}],
        "rows": [{"c": [{"v": "Проводили замену", "f": None}]},
                 {"c": [{"v": "Его/её заменяли", "f": None}]}]
    }
    for key in param["teachers"].keys():
        diction["cols"].append(
            {"id": "", "label": key, "pattern": "", "type": "number"}
        )
    for item in param["teachers"].values():
        diction["rows"][0]["c"].append({"v": item["replace"], "f": None})
        diction["rows"][1]["c"].append({"v": item["replaced"], "f": None})

    d = os.path.join(os.path.join(os.getcwd(), 'static'), 'json')
    json.dump(diction, open(os.path.join(d, 'BarChart.json'), 'w'))


def area_chart(param):
    name = list(param["days_teachers"].keys())[0]
    if param["days_teachers"][name] == {}:
        raise ValueError
    diction = {
        "cols": [{"id": "", "label": "Topping", "pattern": "", "type": "string"},
                 {"id": "", "label": "Вы заменяли", "pattern": "", "type": "number"},
                 {"id": "", "label": "Вас заменяли", "pattern": "", "type": "number"}],
        "rows": []
    }
    days = list(sorted(list(param["days_teachers"][name].keys())))
    ret = {"replace": 0, "replaced": 0}
    for day in days:
        rep = param["days_teachers"][name][day]
        if len(param["days_teachers"][name].items()) == 1:
            diction["rows"].append({"c": [{"v": day, "f": None},
                                          {"v": rep["replace"], "f": None},
                                          {"v": rep["replaced"], "f": None}]})
        diction["rows"].append({"c": [{"v": day, "f": None},
                                      {"v": rep["replace"], "f": None},
                                      {"v": rep["replaced"], "f": None}]})

        ret["replace"] += rep["replace"]
        ret["replaced"] += rep["replaced"]

    d = os.path.join(os.path.join(os.getcwd(), 'static'), 'json')
    json.dump(diction, open(os.path.join(d, 'AreaChart.json'), 'w'))

    return ret
