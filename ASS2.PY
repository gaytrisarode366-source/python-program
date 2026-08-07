import math

n = int(input("enter the number of books:"))

B_name=[]
borrow_CO =[]

for i in range[n]:
    name = int(input(f"Enter the name of Book {i+1}:"))
    count =int(input(f"Enter borrow count of {name} :"))
    B_name.append(name)
    borrow_CO.append(count)

while True:
    print("====BOOK LIBRARY======")
    print("1. Average borrow count ")
    print("2. Heighest and lowest borrow count")
    print("3. Count not Borrowd Book ")
    print("4. Most frequently borrowed book")
    print("5. Display all record")

    choice = int(input("Enter the choce number :"))

    if choice == 1:
        average = sum(borrow_counts) / len(borrow_counts)
        print("Average borrow count:",average)
        break

    elif choice == 2:
        max_count = max(borrow_counts)
        min_count = min(borrow_counts)

        max_index = borrow_counts.index(max_count)
        min_index = borrow_counts.index(min_count)

        print(f"Max borrowd book {max_count} and index is {max_index} ")
        print(f"Min borrowd book {min_count} and index is {min_index}")
        break

    elif choice == 3:
        zero = borrow_counts.count(0)
        print("Book not borrowe :",zero)
        break

    elif choice == 4:
        frequency = {}

        for count in borrow_counts:
            if count in frequency:
                frequency[count] += 1
            else:
                frequency[count] = 1

        mode = None
        max_freq = 0

        for count in frequency:
            if frequency[count] > max_freq:
                max_freq = frequency[count]
                mode = count

        print("Most frequent borrow count (Mode) =", mode)

    elif choice == 5:
        print("Display all Book Records")
        for i in range(len(B_name)):
            print(book_names[i], ":", borrow_CO[i])
        break;

    else:
        print("Enter wrong choice plese try again")


    

    

