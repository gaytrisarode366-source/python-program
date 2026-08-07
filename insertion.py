def insertion_sort(arr):
   
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        
        
        while j >= 0 and key < arr[j]:
            arr[j + 1] = arr[j]
            j -= 1
            
        arr[j + 1] = key

data = [3,5,7,9,2,1]
insertion_sort(data)
print(data)        