# coding=utf-8
# /usr/bin/env python

'''
Author: wenqiangw
Email: wenqiangw@opera.com
Date: 2020-07-10 13:16
Desc: 快速排序,冒泡排序,堆排序
'''

def quick_sort(_list,m=0,n=None):
    ''' “挖坑填数+分治法”
    时间复杂度：
        最坏情况: 每次基准都是最小值n*(n-1)=O(n^2) 冒泡排序
        最优情况&平均情况：每次刚好一分为二，nlog(n)
            T(n)=2T(n/2)+n  -> T(n/2)=2T(n/4)+n/2 -> T(1)=1
            n + 2(n/2) + 2^2(n/4) + ... + 2^x(1) = nlog(n)
            2^x=n x=log(n)
    空间负责度：O(1)
    :param _list:
    :param m:
    :param n:
    :return:
    '''
    if not n:
        n = len(_list) - 1
    i,j=m,n
    base = _list[i]
    print('    Base:',base, _list[:i] + [None] + _list[i + 1:])
    while i < j:
        while (i < j) and (_list[j] >= base):
            j -= 1
        _list[i] = _list[j]
        print('    <----', _list[:j] + [None] + _list[j + 1:])
        while (i < j) and (_list[i] <= base):
            i += 1
        _list[j] = _list[i]
        print('    ---->', _list[:i] + [None] + _list[i + 1:])
    _list[i] = base
    print(_list)
    if m < i:
        quick_sort(_list, m, i)
    if n > j+1:
        quick_sort(_list, j+1, n)
    return _list

def quick_sort_v2(_list,m=0,n=None):
    ''' 快排一次循环
    时间复杂度：
        最坏情况: 每次基准都是最小值n*(n-1)=O(n^2) 冒泡排序
        最优情况&平均情况：每次刚好一分为二，nlog(n)
            T(n)=2T(n/2)+n  -> T(n/2)=2T(n/4)+n/2 -> T(1)=1
            n + 2(n/2) + 2^2(n/4) + ... + 2^x(1) = nlog(n)
            2^x=n x=log(n)
    空间负责度：O(1)
    :param _list:
    :param m:
    :param n:
    :return:
    '''
    if not _list:
        return _list
    if not n:
        n = len(_list)
    base = _list[m]
    i, j = m, n
    cur = m
    while (i < j):  # O(n)
        if _list[i] <= base:
            _list[cur], _list[i] = _list[i], _list[cur]
            cur = cur + 1
        i += 1
    if cur>m:
        _list[cur-1], _list[m] = _list[m], _list[cur-1]
    if m < cur - 2:
        quick_sort_v2(_list, m, cur - 2)  # O(log(n))
    if cur < n:
        quick_sort_v2(_list, cur, n)
    print(_list)
    return _list

def bubble_sort(_list):
    '''
    小规模数据时可使用，交换相邻的两个数使最大值排到最后面
    优化：1.遍历中无数据交换，说明整个数组已经有序，停止循环。
        2.记录遍历时最后发生数据交换的位置，这个位置之后的数据显然已经有序了,不需要再循环。
    :param _list:
    :return:
    '''
    n = len(_list)
    sorted_stop = n
    for i in range(n-1):
        is_sorted = True
        m = min(n,sorted_stop)
        for j in range(m-1):
            if _list[j+1]<_list[j]:
                _list[j+1],_list[j]=_list[j],_list[j+1]
                sorted_stop = j+1  # 之后的数据有序
                is_sorted = False  # 数组是否已经有序
        if is_sorted:
            break
    print(_list)

def heap_sort(_list):
    '''
    1.堆化数组，2.堆排序
    操作：堆插入&堆删除
    升序数组(最大堆)，降序数组(最小堆)
    :param _list:
    :return:
    '''

    def minheap_fixdown(_list,i,j):
        '''
        最小堆数组，堆内从上向下恢复堆次序
        :param _list:
        :return:
        '''
        _left = i * 2
        _right = i * 2 + 1
        _change = _left
        if _right<=j:
            if _list[_left-1]>_list[_right-1]:
                _change = _right
        if _change<=j:
            if _list[i-1]>_list[_change-1]:
                _list[i - 1], _list[_change-1]=_list[_change-1],_list[i-1]
                minheap_fixdown(_list, _change,j)

    n = len(_list)
    # 1.堆化数组 - 从下向上堆化 O(nlogn)
    heap_i = int(n / 2)  # 从最后一个分支节点开始调整堆
    while heap_i > 0:
        minheap_fixdown(_list,heap_i,n)
        heap_i = heap_i-1
        print(_list)
    print('----')
    # 2.堆排序 - O(nlogn)
    idx = n
    while idx>0:
        _list[idx - 1], _list[0] = _list[0], _list[idx-1]
        minheap_fixdown(_list,1,idx-1)
        idx = idx-1
        print(_list)
    return _list

def fancy_sort(_list=[1,2,4,3,6,5,8,7]):
    ''' 花式排序,很简单O(n)
    有1,2,3,..n 的无序整数数组，求排序算法。要求时间复杂度 O(n)， 空间复杂度O(1)。
    因为数组是1->n，所以可以找到一种机会，a[i]的位置就是b[a[i]-1]
    :param _list:
    :return:
    '''
    for i,iv in enumerate(_list):
        while(iv != _list[iv-1]):
            _list[i], _list[iv-1] = _list[iv-1],_list[i]
    print(_list)


if __name__ == '__main__':
    the_list = [10, 1, 18, 30, 23, 12, 7, 5, 18, 9]
    # the_list=[4,4,3]
    print(the_list)
    # aa = quick_sort(the_list)
    aa = quick_sort_v2(the_list)
    # bb = bubble_sort(the_list)
    # cc = heap_sort(the_list)
    # fancy_sort()