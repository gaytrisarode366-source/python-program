def selection_Sort(arr):

    for i in range(0,len(arr)):
        minPos=i

        for j in range(i+1,len(arr)):
            if arr[minPos]<arr[j]:
                minPos=j

        temp =arr[minPos]
        arr[minPos]=arr[i]
        arr[i]=temp

data =[3,5,7,8,6,2,1]
selection_Sort(data)
print(data)                