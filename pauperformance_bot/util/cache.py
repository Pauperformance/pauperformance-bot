def to_pkl_name(name: str) -> str:
    return name.replace("/", "_").replace("\\", "_") + ".pkl"
