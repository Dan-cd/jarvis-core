def handle(intent, context) -> str:
    if intent.name == "dev.create_plugin":
        return (
            "[DEV] Simulação ativa.\n"
            "Plugin criado no sandbox (simulado).\n"
            "Nada foi acoplado ao sistema real."
        )

    return "[DEV] Ação simulada, mas não implementada."