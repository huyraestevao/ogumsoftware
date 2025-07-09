 main
    ensaio_id: int
    Ea: float
    tipo_dado_y: str
    df: pd.DataFrame
 main

    def __init__(self) -> None:
        self.history: List[Dict[str, Any]] = []

    def push(self, data: pd.DataFrame, module_name: str) -> None:
 main
        record = {
            "timestamp": datetime.datetime.now(),
            "module": module_name,
            "columns": list(data.columns),
            "data": copy.deepcopy(data),
        }
        self.history.append(record)

    def pop(self) -> Optional[Dict[str, Any]]:
 main
        return list(self.history)

