from safe.safe_execution import safe_execute

@safe_execute(origin="plugin")
def web_plugin():
    print("plugin executado com sucesso!")
    