#Binary search method
def binary_search(nums,target):
    start = 0
    end = len(nums)-1

    while start<=end:
        mid = (start+end)//2
        if nums[mid]==target:
            return mid
        elif nums[mid]<target:
            start = mid+1   
        else:
            end = mid-1

    return -1

nums = [1,2,3,4,5,6,8,9]
target = 7
result = binary_search(nums,target)
if result == -1:
    for i in range(len(nums)):
        if nums[i]<target and nums[i+1]>target:
            print("The target is not present in the list,but it can inserted at index",i+1)
            break
else:
    print(f"The target is present at index {result}")
