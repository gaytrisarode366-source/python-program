
Data = ["ID", "Name", "Roll", "city"]
personal_data = [
    [1, "Gaytri", 28, "Mumbai"],
    [2, "Samar", 34, "pune"],
    [3, "vicky", 25, "nashik"]
]
def display_table(cols, rows):
    print("\n" + "=" * 45)

    fmt_string = "{:<5} {:<12} {:<8} {:<12}"

    print(fmt_string.format(*cols))
    print("-" * 45)
    
    for row in rows:
        print(fmt_string.format(*row))
    print("=" * 45)

print("Student Data:")
display_table(Data, personal_data)


