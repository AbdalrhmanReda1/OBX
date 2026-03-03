from obx import enable, snapshot

enable(mode="dev")


def divide_numbers(a: float, b: float) -> float:
    return a / b


def load_config(path: str) -> dict:
    import json
    with open(path) as f:
        return json.load(f)


def process_users(users: list) -> list:
    result = []
    for user in users:
        name = user["name"]
        email = user["email"]
        result.append({"name": name, "email": email})
    return result


def slow_operation(n: int) -> int:
    import time
    time.sleep(0.01)
    total = sum(range(n))
    return total


if __name__ == "__main__":
    snapshot("start", {"operation": "begin"})

    try:
        result = divide_numbers(10, 0)
    except ZeroDivisionError as exc:
        from obx.shield.crash_shield import get_crash_shield
        get_crash_shield().intercept(exc)
        print("ZeroDivisionError caught and analyzed by OBX")

    total = slow_operation(100_000)
    print(f"Slow operation result: {total}")

    snapshot("end", {"operation": "complete", "result": total})
