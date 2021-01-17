class A:
    pass

class B:
    pass

class C:
    pass

if __name__ == "__main__":
    from pathlib import Path
    print(Path(__file__).parent)