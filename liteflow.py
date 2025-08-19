def run(workflow, data=None):
    if isinstance(workflow, (list, tuple)):  # sequential tasks
        for item in workflow:
            data = run(item, data)

        return data

    if isinstance(workflow, dict):  # branching tasks
        new_data = []
        for key, value in workflow.items():
            if callable(key) and key(data):  # branch based on a function
                d = run(value, data)
                new_data.append(d)
            elif key == data:  # branch based on a key match
                d = run(value, data)
                new_data.append(d)
        return new_data

    if isinstance(workflow, set):  # parallel tasks
        new_data = []
        for item in workflow:
            d = run(item, data)
            new_data.append(d)
        return new_data

    if callable(workflow):
        return workflow(data)

    if hasattr(workflow, "run"):
        return workflow.run(data)
