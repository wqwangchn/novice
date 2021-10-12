# -*- coding: utf-8 -*-
# /usr/bin/env python

'''
Author: wenqiangw
Email: wqwangchn@163.com
Date: 2021/8/19 16:58
Desc:
'''
import sys
import re
import copy


def safe_isinstance(obj, class_path_str):
    """
    Acts as a safe version of isinstance without having to explicitly
    import packages which may not exist in the users environment.

    Checks if obj is an instance of type specified by class_path_str.

    Parameters
    ----------
    obj: Any
        Some object you want to test against
    class_path_str: str or list
        A string or list of strings specifying full class paths
        Example: `sklearn.ensemble.RandomForestRegressor`

    Returns
    --------
    bool: True if isinstance is true and the package exists, False otherwise
    """
    if isinstance(class_path_str, str):
        class_path_strs = [class_path_str]
    elif isinstance(class_path_str, list) or isinstance(class_path_str, tuple):
        class_path_strs = class_path_str
    else:
        class_path_strs = ['']

    # try each module path in order
    for class_path_str in class_path_strs:
        if "." not in class_path_str:
            raise ValueError("class_path_str must be a string or list of strings specifying a full \
                module path to a class. Eg, 'sklearn.ensemble.RandomForestRegressor'")

        # Splits on last occurence of "."
        module_name, class_name = class_path_str.rsplit(".", 1)

        # here we don't check further if the model is not imported, since we shouldn't have
        # an object of that types passed to us if the model the type is from has never been
        # imported. (and we don't want to import lots of new modules for no reason)
        if module_name not in sys.modules:
            continue

        module = sys.modules[module_name]

        # Get class
        _class = getattr(module, class_name, None)

        if _class is None:
            continue

        if isinstance(obj, _class):
            return True

    return False

def format_value(s, format_str):
    """ Strips trailing zeros and uses a unicode minus sign.
    """

    if not issubclass(type(s), str):
        s = format_str % s
    s = re.sub(r'\.?0+$', '', s)
    if s[0] == "-":
        # s = u"\u2212" + s[1:]
        s = "-" + s[1:]
    return s


def convert_color(color):
    try:
        color = pl.get_cmap(color)
    except:
        pass

    if color == "shap_red":
        color = colors.red_rgb
    elif color == "shap_blue":
        color = colors.blue_rgb

    return color

def convert_ordering(ordering, shap_values):
    if issubclass(type(ordering), OpChain):
        ordering = ordering.apply(Explanation(shap_values))
    if issubclass(type(ordering), Explanation):
        if "argsort" in [op["name"] for op in ordering.op_history]:
            ordering = ordering.values
        else:
            ordering = ordering.argsort.flip.values
    return ordering


def merge_nodes(values, partition_tree):
    """ This merges the two clustered leaf nodes with the smallest total value.
    """
    M = partition_tree.shape[0] + 1

    ptind = 0
    min_val = np.inf
    for i in range(partition_tree.shape[0]):
        ind1 = int(partition_tree[i, 0])
        ind2 = int(partition_tree[i, 1])
        if ind1 < M and ind2 < M:
            val = np.abs(values[ind1]) + np.abs(values[ind2])
            if val < min_val:
                min_val = val
                ptind = i
                # print("ptind", ptind, min_val)

    ind1 = int(partition_tree[ptind, 0])
    ind2 = int(partition_tree[ptind, 1])
    if ind1 > ind2:
        tmp = ind1
        ind1 = ind2
        ind2 = tmp

    partition_tree_new = partition_tree.copy()
    for i in range(partition_tree_new.shape[0]):
        i0 = int(partition_tree_new[i, 0])
        i1 = int(partition_tree_new[i, 1])
        if i0 == ind2:
            partition_tree_new[i, 0] = ind1
        elif i0 > ind2:
            partition_tree_new[i, 0] -= 1
            if i0 == ptind + M:
                partition_tree_new[i, 0] = ind1
            elif i0 > ptind + M:
                partition_tree_new[i, 0] -= 1

        if i1 == ind2:
            partition_tree_new[i, 1] = ind1
        elif i1 > ind2:
            partition_tree_new[i, 1] -= 1
            if i1 == ptind + M:
                partition_tree_new[i, 1] = ind1
            elif i1 > ptind + M:
                partition_tree_new[i, 1] -= 1
    partition_tree_new = np.delete(partition_tree_new, ptind, axis=0)

    # update the counts to be correct
    fill_counts(partition_tree_new)

    return partition_tree_new, ind1, ind2


def get_sort_order(dist, clust_order, cluster_threshold, feature_order):
    """ Returns a sorted order of the values where we respect the clustering order when dist[i,j] < cluster_threshold
    """

    # feature_imp = np.abs(values)

    # if partition_tree is not None:
    #     new_tree = fill_internal_max_values(partition_tree, shap_values)
    #     clust_order = sort_inds(new_tree, np.abs(shap_values))
    clust_inds = np.argsort(clust_order)

    feature_order = feature_order.copy()  # order.apply(Explanation(shap_values))
    # print("feature_order", feature_order)
    for i in range(len(feature_order) - 1):
        ind1 = feature_order[i]
        next_ind = feature_order[i + 1]
        next_ind_pos = i + 1
        for j in range(i + 1, len(feature_order)):
            ind2 = feature_order[j]

            # if feature_imp[ind] >
            # if ind1 == 2:
            #     print(ind1, ind2, dist[ind1,ind2])
            if dist[ind1, ind2] <= cluster_threshold:

                # if ind1 == 2:
                #     print(clust_inds)
                #     print(ind1, ind2, next_ind, dist[ind1,ind2], clust_inds[ind2], clust_inds[next_ind])
                if dist[ind1, next_ind] > cluster_threshold or clust_inds[ind2] < clust_inds[next_ind]:
                    next_ind = ind2
                    next_ind_pos = j
                    # print("next_ind", next_ind)
                    # print("next_ind_pos", next_ind_pos)

        # insert the next_ind next
        for j in range(next_ind_pos, i + 1, -1):
            # print("j", j)
            feature_order[j] = feature_order[j - 1]
        feature_order[i + 1] = next_ind
        # print(feature_order)

    return feature_order


def sort_inds(partition_tree, leaf_values, pos=None, inds=None):
    if inds is None:
        inds = []

    if pos is None:
        partition_tree = fill_internal_max_values(partition_tree, leaf_values)
        pos = partition_tree.shape[0] - 1

    M = partition_tree.shape[0] + 1

    if pos < 0:
        inds.append(pos + M)
        return

    left = int(partition_tree[pos, 0]) - M
    right = int(partition_tree[pos, 1]) - M

    left_val = partition_tree[left, 3] if left >= 0 else leaf_values[left + M]
    right_val = partition_tree[right, 3] if right >= 0 else leaf_values[right + M]

    if left_val < right_val:
        tmp = right
        right = left
        left = tmp

    sort_inds(partition_tree, leaf_values, left, inds)
    sort_inds(partition_tree, leaf_values, right, inds)

    return inds


class OpChain():
    """ A way to represent a set of dot chained operations on an object without actually running them.
    """

    def __init__(self, root_name=""):
        self._ops = []
        self._root_name = root_name

    def apply(self, obj):
        """ Applies all our ops to the given object.
        """
        for o in self._ops:
            op, args, kwargs = o
            if args is not None:
                obj = getattr(obj, op)(*args, **kwargs)
            else:
                obj = getattr(obj, op)
        return obj

    def __call__(self, *args, **kwargs):
        """ Update the args for the previous operation.
        """
        new_self = OpChain(self._root_name)
        new_self._ops = copy.copy(self._ops)
        new_self._ops[-1][1] = args
        new_self._ops[-1][2] = kwargs
        return new_self

    def __getitem__(self, item):
        new_self = OpChain(self._root_name)
        new_self._ops = copy.copy(self._ops)
        new_self._ops.append(["__getitem__", [item], {}])
        return new_self

    def __getattr__(self, name):
        # Don't chain special attributes
        if name.startswith("__") and name.endswith("__"):
            return None
        new_self = OpChain(self._root_name)
        new_self._ops = copy.copy(self._ops)
        new_self._ops.append([name, None, None])
        return new_self

    def __repr__(self):
        out = self._root_name
        for o in self._ops:
            op, args, kwargs = o
            out += "."
            out += op
            if (args is not None and len(args) > 0) or (kwargs is not None and len(kwargs) > 0):
                out += "("
                if args is not None and len(args) > 0:
                    out += ", ".join([str(v) for v in args])
                if kwargs is not None and len(kwargs) > 0:
                    out += ", " + ", ".join([str(k) + "=" + str(kwargs[k]) for k in kwargs.keys()])
                out += ")"
        return out