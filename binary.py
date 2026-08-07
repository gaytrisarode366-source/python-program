def binary_Search(arr,key):
    start =0
    end=len(arr)

    while start<=end :
        mid = (start+end)//2
        if arr[mid]==key :
           return mid

        if arr[mid]<key:
            start=mid+1
        else:
            end=mid-1
    return -1

data = [3,6,4,7,4,8,9]
key = 6
print("index for key :",binary_Search(data,key))
  

