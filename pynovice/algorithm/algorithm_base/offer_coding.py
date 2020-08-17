# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-07-18 16:18
Desc:
https://s2geometry.io/resources/s2cell_statistics geo
fun_1,fun_4
'''

def fun_1(arr_x,target,m=0,n=None):
    '''
    找出target在有序数组arr_x中的位置
    eg:
    有序数组[1,3,6,10]
    (,1): -999
    [1,3): 1
    [3,6): 2
    [6,10): 3
    [10,): 999
    :param arr_x:
    :param target:
    :return:
    '''
    if n==None:
        n=len(arr_x)-1

    len_x = len(arr_x)
    if len_x == 0:
        return None
    if target < arr_x[0]:
        return -999
    if arr_x[-1] <= target:
        return 999

    if m>n:
        return m
    middle = int((m+n)/2)  # 找出中间位置
    if target == arr_x[middle]:
        return middle+1
    elif target > arr_x[middle]:
        return fun_1(arr_x, target,middle+1,n)
    else:
        return fun_1(arr_x, target,m,middle-1)

def fun_1(arr_x,target,m=0,n=None):
    '''
    给定一个有序递增数组nums，找到值为target的数值区间。

    :param arr_x:
    :param target:
    :return:
    '''
    if n==None:
        n=len(arr_x)-1
    if m>=n:
        return [min(m,n),max(m,n)]
    print(arr_x,m,n)
    middle = int((m+n)/2)  # 找出中间位置
    print(middle)

    if target>arr_x[middle]:
        if middle+1<n:
            left, right =fun_1(arr_x, target, middle+1, n)
        else:
            left, right = n,n
    elif target<arr_x[middle]:
        if middle-1>m:
            left, right = fun_1(arr_x, target, m, middle - 1)
        else:
            left, right = m,m
    else:
        if middle-1>m:
            left, _ = fun_1(arr_x, target, m, middle - 1)
        else:
            left = m
        if middle+1<n:
            _, right = fun_1(arr_x, target, middle + 1, n)
        else:
            right=n
    return left,right

def fun_2(arr_x,target):
    '''
    二叉树中和为某一值的路径
    1.数组转二叉树
    2.二叉树迭代遍历
    :param arr_x:
    :param target:
    :return:
    '''
    class TreeNode:
        def __init__(self,x):
            self.values=x
            self.left=None
            self.right=None
    def arr_2tree(arr_x):
        '''
        数组转二叉树,从低向上建立树节点
        :param arr_x:
        :return:
        '''
        len_x = len(arr_x)
        if len_x<1:
            return None
        for i,iv in enumerate(arr_x): # 转换为节点
            arr_x[i]=TreeNode(iv)
        node_i = int(len_x/2)
        while(node_i>0):
            arr_x[node_i-1].left = arr_x[2*node_i-1]
            if 2*node_i<len_x:
                arr_x[node_i-1].right = arr_x[2*node_i]
            node_i = node_i-1
        return arr_x[0]

    tree_x = arr_2tree(arr_x)

    def _fun(node,cur_list=[],out=[]):
        if (not node.left) and (not node.right):
            if sum(cur_list)+node.values == target:
                out.append(cur_list+[node.values])
        else:
            cur_list = cur_list+[node.values]
            if node.left:
                _fun(node.left,cur_list,out)
            if node.right:
                _fun(node.right, cur_list,out)
        return out

    out = _fun(tree_x)
    return out

def fun_3(arr_x1,arr_x2):
    '''
    1，给定两个单链表，求两个链表的交叉节点。
    例如：
    链表1：1，2，3，4，5；
    链表2：99，9，4，5；
    1.转链表
    2.求交叉
    '''
    ##
    if (not arr_x1)or (not arr_x2):
        return None
    len_1=len(arr_x1)
    len_2=len(arr_x2)
    if len_1>len_2:
        arr_x1,arr_x2=arr_x2,arr_x1
    len_s = abs(len_1-len_2)
    out=[]
    for i,iv in enumerate(arr_x1):
        if arr_x1[i]==arr_x2[i+len_s]:
            out.append(iv)
    return out

def fun_4(arr_x,target,m=0,n=None):
    '''
    给定一个有序递增数组nums，找到所有两个和为target的数值对[number1, number2]，如果存在则输出所有的数值对，否则返回[-1, -1]。

    :param arr_x:
    :param target:
    :return:
    '''
    if n==None:
        n=len(arr_x)-1
    if m>n:
       return [min(m,n),max(m,n)]
    #
    # len_x = len(arr_x)
    # if len_x == 0:
    #     return 999,-999
    # if target < arr_x[0]:
    #     return -999,0
    # if arr_x[-1] <= target:
    #     return len_x,999
    middle = int((m+n)/2)  # 找出中间位置
    if target == arr_x[middle]:
        print(m, middle - 1,middle + 1, n)
        fun_1(arr_x, target, middle + 1, n)
        fun_1(arr_x, target, m, middle - 1)
    elif target > arr_x[middle]:
        print(middle+1, n)
        return fun_1(arr_x, target,middle+1,n)
    else:
        print(m, middle-1)
        return fun_1(arr_x, target,m,middle-1)


# 1. 实现一个快速排序算法，注意时间复杂度和空间复杂度
def quick_sort(arr_x,m=0,n=None):
    if not arr_x:
        return arr_x
    if not n:
        n=len(arr_x)
    base = arr_x[m]
    i,j=m,n
    while(i<j):  #O(n)
        while (i<j) and (arr_x[j]>=base):
            j-=1
        arr_x[i]=arr_x[j]
        while(i<j) and (arr_x[m]<=base):
            i+=1
        arr_x[j] = arr_x[i]
    arr_x[i]=base
    if m<i-1:
        quick_sort(arr_x,m,i-1)  # O(log(n))
    if j+1<n:
        quick_sort(arr_x,j+1,n)
    return arr_x


# 如果数组只能从左向右扫描，一个for 循环
# 就是说快排的一次partition，用一个for循环实现 数组只能从左向右扫描 你现在这个版本，用了三个while循环 数组是双向扫描的

def quick_sort_v2(arr_x,m=0,n=None):
    if not arr_x:
        return arr_x
    if not n:
        n=len(arr_x)
    base = arr_x[m]
    i,j=m,n
    cur = m
    while(i<j):  #O(n)
        if arr_x[i]<=base:
            arr_x[cur],arr_x[i] = arr_x[i],arr_x[cur]
            cur=cur+1
        i+=1
    print(cur,m)
    arr_x[cur],arr_x[m]=arr_x[m],arr_x[cur]
    if m<cur-1:
        quick_sort_v2(arr_x,m,cur-1)  # O(log(n))
    if cur+1<n:
        quick_sort_v2(arr_x,cur+1,n)
    return arr_x


def lengthOfLongestSubstring(s):
    l = len(s)
    if l < 2:
        return 1

    # dp[i]表示以s[i]结尾的最长不重复子串的长度
    dp = [1 for _ in range(l)]
    map = dict()
    map[s[0]] = 0
    for i in range(1, l):
        if s[i] in map:
            if i - map[s[i]] > dp[i - 1]:
                dp[i] = dp[i - 1] + 1
            else:
                dp[i] = i - map[s[i]]
        else:
            dp[i] = dp[i - 1] + 1
        map[s[i]] = i
    return max(dp)

if __name__ == '__main__':
    # dd = fun_1(arr_x=[5,6,6,6,6,6,6,6,7,9,10], target=9)
    # print(dd)
    dd = quick_sort_v2(arr_x=[5, 6, 10, 6, 6, 6, 6, 6, 7, 9, 10])
    print(dd)

    # aa=fun_2(arr_x=[2,3,4,5,5,4], target=10)
    # print(aa)
    #
    # aa=fun_3([5,4],[1,2,3,4])
    # print(aa)