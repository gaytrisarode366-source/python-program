def Linear_search(nums,target):
    for i in range(len(nums)):
        if nums[i]==target:
            return i
    return -1

nums = [1,2,3,4,5,6,8,9]
target =7
result = Linear_search(nums,target)
if result == -1:
    for i in range(len(nums)):
        if nums[i]<target and nums[i+1]>target:
            print("The target is not present in the list, but it can be inserted at index",i+1)
            break
else:
    print(f"The target is present at index {result}")        
    
