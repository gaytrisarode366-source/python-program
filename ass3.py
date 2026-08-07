def bubble_Sort(arr):
    n =len(arr)
    for i in range(n):
        swapp=False

    for j in range(0,n-1-i):
        if arr[j]>arr[j+1] :
            arr[j],arr[j+1]=arr[j+1],arr[j]
            swapp=True

        
        if not swapp:
            break

data=[2,3,4,5,7,4,8]
bubble_Sort(data)
print("Sorted array :",data)



    
