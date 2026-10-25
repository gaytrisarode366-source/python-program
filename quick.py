def quick_Sort(arr):
    n= len(arr)
    if n <= 1:
        return arr
#pivote element
    p = arr[0]
    left=[]
    right=[]

    for i in arr[1:]:
        if i < p:
            left.append(i)
        else:
            right.append(i)

    return quick_Sort(left)+[p]+quick_Sort(right)

arr=[2,5,7,8,4,8,1,0]
print("Quick Sort:",quick_Sort(arr))                    
