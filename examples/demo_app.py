from obx import enable

enable(mode="dev")


def calculate_fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return calculate_fibonacci(n - 1) + calculate_fibonacci(n - 2)


def process_data(items: list) -> dict:
    result = {}
    for i, item in enumerate(items):
        result[str(i)] = item * 2
    return result


def find_user(users: list, user_id: int):
    for user in users:
        if user.get("id") == user_id:
            return user
    return None


if __name__ == "__main__":
    fib = calculate_fibonacci(20)
    print(f"Fibonacci(20) = {fib}")

    data = process_data([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    print(f"Processed {len(data)} items")

    users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    user = find_user(users, 1)
    print(f"Found user: {user}")
